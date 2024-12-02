# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
from odoo.osv.expression import AND
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_multi_currency = fields.Boolean(string="Multi Currency")
    apply_exchange_difference = fields.Boolean(string="Apply Exchnage Difference", default=True)
    multi_currency_ids = fields.Many2many("res.currency", string="Seleced Currencies")

class PosPayment(models.Model):
    _inherit = 'pos.payment'

    is_multi_currency_payment = fields.Boolean(string="Multi Currency Payment")
    other_currency_id = fields.Many2one('res.currency', string='Other Currency')
    other_currency_rate = fields.Float(string='Conversion Rate', digits=(
        12, 6), help='Conversion rate from company currency to order currency.')
    other_currency_amount = fields.Float(string='Currency Amount')
    
    def _export_for_ui(self, payment):
        result = super(PosPayment, self)._export_for_ui(payment)
        result['is_multi_currency_payment'] = payment.is_multi_currency_payment
        result['other_currency_id'] = payment.other_currency_id.id if payment.other_currency_id else False
        result['other_currency_rate'] = payment.other_currency_rate
        result['other_currency_amount'] = payment.other_currency_amount
        result['id'] = payment.id
        result['wk_payment_name'] = payment.payment_method_id.name if payment.payment_method_id else False
        return result

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        result = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        result['other_currency_id'] = ui_paymentline.get('other_currency_id') or False
        result['other_currency_rate'] = ui_paymentline.get('other_currency_rate') or False
        result['other_currency_amount'] = ui_paymentline.get('other_currency_amount') or False
        result['is_multi_currency_payment'] = ui_paymentline.get('is_multi_currency_payment') or False
        return result
    
    # Inherited this function to make the changes to the currency of changes
    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        if len(pos_order['statement_ids']) == 1:
            prec_acc = order.pricelist_id.currency_id.decimal_places
            order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
            order_bank_statement_lines.unlink()
            other_currency_id = False
            for payments in pos_order['statement_ids']:
                if payments[2].get('other_currency_id'):
                    other_currency_id = payments[2].get('other_currency_id')
                order.add_payment(self._payment_fields(order, payments[2]))
            order.amount_paid = sum(order.payment_ids.mapped('amount'))
            if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
                cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
                if not cash_payment_method:
                    raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
                return_payment_vals = {
                    'name': _('return'),
                    'pos_order_id': order.id,
                    'amount': -pos_order['amount_return'],
                    'payment_date': fields.Datetime.now(),
                    'payment_method_id': cash_payment_method.id,
                    'is_change': True,
                }

                if other_currency_id:
                    currency = self.env['res.currency'].browse([other_currency_id])
                    if currency:
                        amt = (pos_order['amount_return'] * currency.rate) / order.pricelist_id.currency_id.rate
                        return_payment_vals['other_currency_id'] = currency.id
                        return_payment_vals['other_currency_amount'] = amt
                        return_payment_vals['other_currency_rate'] = currency.rate
                        return_payment_vals['is_multi_currency_payment'] = True
                
                order.add_payment(return_payment_vals)
        else:
            return super(PosOrder, self)._process_payment_lines(pos_order, order, pos_session, draft)

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        if result.get('statement_ids'):
            multi_payment_lines = []
            for statement_id in result.get('statement_ids'):
                data = {}
                if statement_id[2].get('is_multi_currency_payment'):
                    result['is_multi_currency_payment'] = True
                    data['cid'] = statement_id[2].get('id')
                    data['name'] = statement_id[2].get('wk_payment_name')
                    data['other_currency_id'] = statement_id[2].get('other_currency_id')
                    data['other_currency_amount'] = statement_id[2].get('other_currency_amount')
                    data['amount'] = statement_id[2].get('amount')
                    data['is_change'] = statement_id[2].get('is_change')
                    multi_payment_lines.append(data)
            result['multi_payment_lines'] = multi_payment_lines
        return result

class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        result = super(ReportSaleDetails, self).get_sale_details(date_start, date_stop, config_ids, session_ids)
        domain = [('state', 'in', ['paid', 'invoiced', 'done'])]
        domain = AND([domain,
                      [('date_order', '>=', fields.Datetime.to_string(result.get('date_start'))),
                       ('date_order', '<=', fields.Datetime.to_string(result.get('date_stop')))]
                      ])
        orders = self.env['pos.order'].search(domain)
        if orders.payment_ids.ids:
            query = """
                SELECT {group_by_field}, sum(other_currency_amount) AS amount
                FROM pos_payment
                WHERE id IN %s
                GROUP BY {group_by_field}
                """
            self._cr.execute(query.format(
                group_by_field='other_currency_id'), (tuple(orders.payment_ids.ids),))
            res = self._cr.dictfetchall()
            result['other_currency_name'] = []
            result['other_currency_amount'] = []
            amount = []
            currency_sign = []
            symbol = []
            order_with_curr = {}
            data = {}
            for rec in res:
                other_currency = self.env['res.currency'].browse(rec.get('other_currency_id'))
                total_amount = rec.get('amount')
                if other_currency.name and other_currency.symbol and (total_amount is not None):
                    currency_sign.append(other_currency.name)
                    symbol.append(other_currency.symbol)
                    total_amount_currency = round(total_amount, 2)
                    amount.append(total_amount_currency)
            if amount and currency_sign and symbol:
                order_with_curr["amount"] = amount
                order_with_curr["currency_sign"] = currency_sign
                order_with_curr["symbol"] = symbol
                for i, curr in enumerate(order_with_curr['currency_sign']):
                    data[curr] = str(order_with_curr["symbol"][i]) + \
                        str(order_with_curr["amount"][i])
                result["currency_amount"] = data
        return result

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_enable_multi_currency = fields.Boolean(related='pos_config_id.enable_multi_currency', readonly=False)
    pos_apply_exchange_difference = fields.Boolean(related='pos_config_id.apply_exchange_difference', readonly=False)
    pos_multi_currency_ids = fields.Many2many(related='pos_config_id.multi_currency_ids', readonly=False)

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def get_currency(self):
        currency_id = self.env['res.config.settings'].sudo().search([]).pos_multi_currency_ids
        currency_data = []
        for rec in currency_id:
            currency_object = {}
            currency_object["decimal_places"] = rec.decimal_places
            currency_object["id"] = rec.id
            currency_object["name"] = rec.name
            currency_object["position"] = rec.position
            currency_object["rate"] = rec.rate
            currency_object["rounding"] = rec.rounding
            currency_object["symbol"] = rec.symbol
            currency_data.append(currency_object)
        return currency_data

class PosSession(models.Model):
    _inherit = 'pos.session'

    def get_closing_control_data(self):
        result = super().get_closing_control_data()
        orders = self.env['pos.order'].browse(self.order_ids.ids)
        if orders.payment_ids.ids:
            query = """
                SELECT {group_by_field}, sum(other_currency_amount) AS amount
                FROM pos_payment
                WHERE id IN %s
                GROUP BY {group_by_field}
                """
            self._cr.execute(query.format(group_by_field='other_currency_id'), (tuple(orders.payment_ids.ids),))
            res= self._cr.dictfetchall()
            result['other_currency_name']=[]
            result['other_currency_amount']=[]
            amount = []
            currency_sign = []
            symbol=[]
            order_with_curr={}
            data={}
            for rec in res:
                other_currency = self.env['res.currency'].browse(
                    rec.get('other_currency_id'))
                total_amount = rec.get('amount')
                if other_currency.name and other_currency.symbol and (total_amount is not None):
                    currency_sign.append(other_currency.name)
                    symbol.append(other_currency.symbol)
                    total_amount_currency = round(total_amount, 2)
                    amount.append(total_amount_currency)
            if amount and currency_sign and symbol:
                order_with_curr["amount"] = amount
                order_with_curr["currency_sign"] = currency_sign
                order_with_curr["symbol"] = symbol
                for i, curr in enumerate(order_with_curr['currency_sign']):
                    data[curr] = str(order_with_curr["symbol"][i])+str(order_with_curr["amount"][i])
                result["currency_amount"] = data
        return result
