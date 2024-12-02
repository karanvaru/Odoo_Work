# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.tools import format_datetime, formatLang


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

#     mark_up = fields.Monetary(
#         string="Mark Up",
#     )
    mark_up = fields.Float(
        string="Markup",
        default=0,
        digits=(16, 2),
        help="You can apply a mark-up by setting a negative discount.")



    @api.depends('applied_on', 'categ_id', 'mark_up', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _compute_name_and_price(self):
        for item in self:
            if item.categ_id and item.applied_on == '2_product_category':
                item.name = _("Category: %s") % (item.categ_id.display_name)
            elif item.product_tmpl_id and item.applied_on == '1_product':
                item.name = _("Product: %s") % (item.product_tmpl_id.display_name)
            elif item.product_id and item.applied_on == '0_product_variant':
                item.name = _("Variant: %s") % (item.product_id.display_name)
            else:
                item.name = _("All Products")

            if item.compute_price == 'fixed':
                item.price = formatLang(
                    item.env, item.fixed_price, monetary=True, dp="Product Price", currency_obj=item.currency_id)
            elif item.compute_price == 'percentage':
                item.price = _("%s %% discount", item.percent_price)
#                 if item.mark_up:
#                     item.price = _("%s Mark Up", item.mark_up)
            else:
                item.price = _("%(percentage)s %% discount and %(price)s surcharge", percentage=item.price_discount,
                               price=item.price_surcharge)
                if item.mark_up and not item.price_discount:
                    item.price = _("%(markup)s Mark Up and %(price)s surcharge", markup=item.mark_up,
                                   price=item.price_surcharge)

    @api.depends_context('lang')
    @api.depends('compute_price', 'price_discount', 'mark_up', 'price_surcharge', 'base', 'price_round')
    def _compute_rule_tip(self):
        base_selection_vals = {elem[0]: elem[1] for elem in self._fields['base']._description_selection(self.env)}
        self.rule_tip = False
        for item in self:
            if item.compute_price != 'formula':
                continue
            base_amount = 100
            discount_factor = (100 - item.price_discount) / 100
            discounted_price = base_amount * discount_factor
            if item.mark_up: # patch
                discounted_price = (discounted_price + (discounted_price * (item.mark_up / 100))) or 0.0# patch

            if item.price_round:
                discounted_price = tools.float_round(discounted_price, precision_rounding=item.price_round)
            surcharge = tools.format_amount(item.env, item.price_surcharge, item.currency_id)
            item.rule_tip = _(
                "%(base)s with a %(discount)s %% discount and %(surcharge)s extra fee\n"
                "Example: %(amount)s * %(discount_charge)s + %(price_surcharge)s → %(total_amount)s",
                base=base_selection_vals[item.base],
                discount=item.price_discount,
                surcharge=surcharge,
                amount=tools.format_amount(item.env, 100, item.currency_id),
                discount_charge=discount_factor,
                price_surcharge=surcharge,
                total_amount=tools.format_amount(
                    item.env, discounted_price + item.price_surcharge, item.currency_id),
            )



#     @api.depends_context('lang')
#     @api.depends('compute_price', 'price_discount', 'mark_up', 'price_surcharge', 'base', 'price_round')
#     def _compute_rule_tip(self):
#         base_selection_vals = {elem[0]: elem[1] for elem in self._fields['base']._description_selection(self.env)}
#         self.rule_tip = False
#         for item in self:
#             if item.compute_price != 'formula':
#                 continue
#             base_amount = 100
#             discount_factor = (100 - item.price_discount) / 100
#             print ("discount_factor ________________",discount_factor)
#             markup_factor = (100 + item.mark_up) / 100
#             print ("markup_factor ------------",markup_factor)
# 
#             discounted_price = base_amount * discount_factor * markup_factor
#             if item.price_round:
#                 discounted_price = tools.float_round(discounted_price, precision_rounding=item.price_round)
#             surcharge = tools.format_amount(item.env, item.price_surcharge, item.currency_id)
#             item.rule_tip = _(
#                 "%(base)s with a %(discount)s %% discount and %(surcharge)s extra fee\n"
#                 "Example: %(amount)s * %(discount_charge)s + %(price_surcharge)s → %(total_amount)s",
#                 base=base_selection_vals[item.base],
#                 discount=item.price_discount,
#                 surcharge=surcharge,
#                 amount=tools.format_amount(item.env, 100, item.currency_id),
#                 discount_charge=discount_factor,
#                 price_surcharge=surcharge,
#                 total_amount=tools.format_amount(
#                     item.env, discounted_price + item.price_surcharge, item.currency_id),
#             )
#             if item.mark_up and not item.price_discount:
#                 item.rule_tip = _(
#                     "%(base)s with a %(markup)s Mark Up and %(surcharge)s extra fee\n"
#                     "Example: %(amount)s + %(markup)s + %(price_surcharge)s → %(total_amount)s",
#                     markup=item.mark_up,
#                     base=base_selection_vals[item.base],
#                     discount=item.price_discount,
#                     surcharge=surcharge,
#                     amount=tools.format_amount(item.env, 100, item.currency_id),
#                     discount_charge=discount_factor,
#                     price_surcharge=surcharge,
#                     total_amount=tools.format_amount(
#                         item.env, base_amount + item.mark_up + item.price_surcharge, item.currency_id),
#                 )

    @api.onchange('compute_price')
    def _onchange_compute_price(self):
        result = super(PricelistItem, self)._onchange_compute_price()
        if self.compute_price != 'percentage':
            self.mark_up = 0.0
        if self.compute_price != 'formula':
            self.mark_up = 0.0
        return result

    @api.constrains('percent_price', 'mark_up', 'price_discount')
    def _check_discount_mark_up_value(self):
        for item in self:
            if item.mark_up < 0.0 or item.price_discount < 0.0:
                raise ValidationError(_('Negative Value Not Allowed'))
#             elif item.percent_price > 0.0 and item.mark_up > 0.0 or item.price_discount > 0.0 and item.mark_up > 0.0:
#                 raise ValidationError(_('Enter Discount Value Or Mark Up Value'))

    def _compute_price(self, product, quantity, uom, date, currency=None):
        """Compute the unit price of a product in the context of a pricelist application.

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param currency: pricelist currency (for the specific case where self is empty)

        :returns: price according to pricelist rule, expressed in pricelist currency
        :rtype: float
        """
        product.ensure_one()
        uom.ensure_one()

        currency = currency or self.currency_id
        currency.ensure_one()
        print ("\n")
        # Pricelist specific values are specified according to product UoM
        # and must be multiplied according to the factor between uoms
        product_uom = product.uom_id
        if product_uom != uom:
            convert = lambda p: product_uom._compute_price(p, uom)
        else:
            convert = lambda p: p

        if self.compute_price == 'fixed':
            price = convert(self.fixed_price)
        elif self.compute_price == 'percentage':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            price = (base_price - (base_price * (self.percent_price / 100))) or 0.0
        elif self.compute_price == 'formula':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            # complete formula
            price_limit = base_price
            price = (base_price - (base_price * (self.price_discount / 100))) or 0.0
            if self.mark_up: # patch
                price = (price + (price * (self.mark_up / 100))) or 0.0# patch

            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            if self.price_surcharge:
                price += convert(self.price_surcharge)

            if self.price_min_margin:
                price = max(price, price_limit + convert(self.price_min_margin))

            if self.price_max_margin:
                price = min(price, price_limit + convert(self.price_max_margin))
        else:  # empty self, or extended pricelist price computation logic
            price = self._compute_base_price(product, quantity, uom, date, currency)

        return price



#     def _compute_pricexx(self, product, quantity, uom, date, currency=None):
#         """Compute the unit price of a product in the context of a pricelist application.
#         :param product: recordset of product (product.product/product.template)
#         :param float qty: quantity of products requested (in given uom)
#         :param uom: unit of measure (uom.uom record)
#         :param datetime date: date to use for price computation and currency conversions
#         :param currency: pricelist currency (for the specific case where self is empty)
# 
#         :returns: price according to pricelist rule, expressed in pricelist currency
#         :rtype: float
#         """
#         product.ensure_one()
#         uom.ensure_one()
# 
#         currency = currency or self.currency_id
#         currency.ensure_one()
# 
#         # Pricelist specific values are specified according to product UoM
#         # and must be multiplied according to the factor between uoms
#         product_uom = product.uom_id
#         if product_uom != uom:
#             convert = lambda p: product_uom._compute_price(p, uom)
#         else:
#             convert = lambda p: p
# 
#         if self.compute_price == 'fixed':
#             price = convert(self.fixed_price)
#         elif self.compute_price == 'percentage':
#             base_price = self._compute_base_price(product, quantity, uom, date, currency)
#             price = (base_price - (base_price * (self.percent_price / 100))) or 0.0
#             if self.mark_up:
#                 price = base_price + self.mark_up or 0.0
#         elif self.compute_price == 'formula':
#             base_price = self._compute_base_price(product, quantity, uom, date, currency)
#             # complete formula
#             price_limit = base_price
#             price = (base_price - (base_price * (self.price_discount / 100))) or 0.0
#             if self.mark_up:
#                 price = base_price + self.mark_up or 0.0
#             if self.price_round:
#                 price = tools.float_round(price, precision_rounding=self.price_round)
# 
#             if self.price_surcharge:
#                 price += convert(self.price_surcharge)
# 
#             if self.price_min_margin:
#                 price = max(price, price_limit + convert(self.price_min_margin))
# 
#             if self.price_max_margin:
#                 price = min(price, price_limit + convert(self.price_max_margin))
#         else:  # empty self, or extended pricelist price computation logic
#             price = self._compute_base_price(product, quantity, uom, date, currency)
# 
#         return price
