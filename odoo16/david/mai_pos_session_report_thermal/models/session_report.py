from datetime import datetime, timedelta
import pytz
from odoo import fields, models, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class PosConfig(models.Model):
    _inherit = 'pos.config'

    do_session_report = fields.Boolean(string='Allowed to print Session Report')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    do_session_report = fields.Boolean(related='pos_config_id.do_session_report',readonly=False)    


class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_return_order = fields.Boolean(string='Return Order')

    def refund(self):
        res = super(PosOrder, self).refund()
        self.env['pos.order'].search([('id', '=', res['res_id'])]).is_return_order = True
        return res

class PosSession(models.Model):
    _inherit = 'pos.session'


    def session_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        return self.env.ref('mai_pos_session_report_thermal.action_report_session').report_action(self)

    def get_payment_details(self):
        orders = self.env['pos.order'].search([('session_id', '=', self.id)])
        data = self.env["pos.payment"].read_group([('pos_order_id', 'in', orders.ids)], ['amount'], 'payment_method_id', lazy=False)
        pos_payment_method_obj = self.env['pos.payment.method']
        payment_data_dict = {}
        for i in data:
            p_id = pos_payment_method_obj.browse(i.get('payment_method_id')[0])
            amount = i.get('amount')
            payment_data_dict[p_id.id] = {'name': p_id.name, 'total': amount}
        return [payment_data_dict.get(d) for d in payment_data_dict]

    def get_session_detail_mai(self):
        order_ids = self.env['pos.order'].search([('session_id', '=', self.id)])
        discount = 0.0
        taxes = 0.0
        total_sale = 0.0
        total_gross = 0.0
        total_return = 0.0
        products_sold = {}
        for order in order_ids:
            total_sale += order.amount_total
            currency = order.session_id.currency_id
            total_gross += order.amount_total
            for line in order.lines:
                if line.product_id.pos_categ_id.name:
                    if line.product_id.pos_categ_id.name in products_sold:
                        products_sold[line.product_id.pos_categ_id.name] += line.qty
                    else:
                        products_sold.update({
                            line.product_id.pos_categ_id.name: line.qty
                        })
                else:
                    if 'undefine' in products_sold:
                        products_sold['undefine'] += line.qty
                    else:
                        products_sold.update({
                                'undefine': line.qty
                                })
                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes += tax.get('amount', 0)
                discount += line.discount
            if order.is_return_order:
                total_return -= order.amount_total
        return {
            'total_sale': total_sale,
            'discount': discount,
            'tax': taxes,
            'products_sold': products_sold or False,
            'total_gross': total_gross - taxes - discount + total_return,
            'total_return': total_return

        }

    def get_current_datetime(self):
        if self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '+':
            date_time = datetime.now() + timedelta(hours=hour_tz, minutes=min_tz)
        if sign == '-':
            date_time = datetime.now() - timedelta(hours=hour_tz, minutes=min_tz)
        return date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_session_open_date(self):
        return self.start_at.strftime(DEFAULT_SERVER_DATE_FORMAT)

    def get_session_open_time(self):
        return self.start_at.strftime("%I:%M %p")
