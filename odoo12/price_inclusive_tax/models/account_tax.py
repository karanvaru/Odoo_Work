#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import odoo
from odoo.tools.float_utils import float_round as round
from odoo import api, fields, models, _

class AccountTax(models.Model):
    _inherit = "account.tax"

    is_group_inclusive = fields.Boolean('Included in Price')

    @api.onchange('amount_type')
    def _onchange_amount_type(self):
        if self.amount_type != 'group' and self.is_group_inclusive:
            self.is_group_inclusive = False
        return

    @api.multi
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        check = self.getGroupTypeTax()
        if check:
            if len(self) == 0:
                company_id = self.env.user.company_id
            else:
                company_id = self[0].company_id
            if not currency:
                currency = company_id.currency_id
            taxes = []
            # By default, for each tax, tax amount will first be computed
            # and rounded at the 'Account' decimal precision for each
            # PO/SO/invoice line and then these rounded amounts will be
            # summed, leading to the total amount for that tax. But, if the
            # company has tax_calculation_rounding_method = round_globally,
            # we still follow the same method, but we use a much larger
            # precision when we round the tax amount for each line (we use
            # the 'Account' decimal precision + 5), and that way it's like
            # rounding after the sum of the tax amounts of each line
            prec = currency.decimal_places

            # In some cases, it is necessary to force/prevent the rounding of the tax and the total
            # amounts. For example, in SO/PO line, we don't want to round the price unit at the
            # precision of the currency.
            # The context key 'round' allows to force the standard behavior.
            round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
            round_total = True
            if 'round' in self.env.context:
                round_tax = bool(self.env.context['round'])
                round_total = bool(self.env.context['round'])

            if not round_tax:
                prec += 5

            base_values = self.env.context.get('base_values')
            if not base_values:
                total_excluded = total_included = base = round(price_unit * quantity, prec)
            else:
                total_excluded, total_included, base = base_values

            # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
            # search. However, the search method is overridden in account.tax in order to add a domain
            # depending on the context. This domain might filter out some taxes from self, e.g. in the
            # case of group taxes.
            for tax in self.sorted(key=lambda r: r.sequence):
                if tax.amount_type == 'group':
                    children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))
                    ret = children.compute_all(price_unit, currency, quantity, product, partner)
                    group_tax_amount = 0.0
                    group_tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
                    if not round_tax:
                        group_tax_amount = round(group_tax_amount, prec)
                    else:
                        group_tax_amount = currency.round(group_tax_amount)
                    if tax.is_group_inclusive:
                        ret['total_excluded'] = total_excluded - group_tax_amount
                        ret['total_included'] = total_included
                        ret['base'] = base - group_tax_amount
                    else:
                        ret['total_excluded'] = total_excluded
                        ret['total_included'] = total_included + group_tax_amount
                    splitTax = group_tax_amount/2.0
                    for taxData in ret.get('taxes'):
                        retBase = ret.get('base')
                        restAmount = retBase - splitTax
                        taxData['base'] = restAmount
                        taxData['amount'] = splitTax
                    total_excluded = ret['total_excluded']
                    base = ret['base'] if tax.include_base_amount else base
                    total_included = ret['total_included']
                    tax_amount = total_included - total_excluded
                    taxes += ret['taxes']
                    continue

                tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
                if not round_tax:
                    tax_amount = round(tax_amount, prec)
                else:
                    tax_amount = currency.round(tax_amount)

                if tax.price_include:
                    total_excluded -= tax_amount
                    base -= tax_amount
                else:
                    total_included += tax_amount

                # Keep base amount used for the current tax
                tax_base = base

                if tax.include_base_amount:
                    base += tax_amount

                taxes.append({
                    'id': tax.id,
                    'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                    'amount': tax_amount,
                    'base': tax_base,
                    'sequence': tax.sequence,
                    'account_id': tax.account_id.id,
                    'refund_account_id': tax.refund_account_id.id,
                    'analytic': tax.analytic,
                })

            return {
                'taxes': sorted(taxes, key=lambda k: k['sequence']),
                'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
                'total_included': currency.round(total_included) if round_total else total_included,
                'base': base,
            }
        return super(AccountTax, self).compute_all(price_unit, currency, quantity, product, partner)
    
    def getGroupTypeTax(self):
        flag = False
        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':
                flag = True
                break
        return flag

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        res = super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)
        self.ensure_one()
        if self.amount_type == 'group' and self.is_group_inclusive:
            return base_amount - (base_amount / (1 + self.amount / 100))
        if self.amount_type == 'group' and not self.is_group_inclusive:
            return base_amount * self.amount / 100
        return res
