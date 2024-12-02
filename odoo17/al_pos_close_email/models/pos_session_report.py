from odoo import models, api, fields, _


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        data = super(ReportSaleDetails, self).get_sale_details(date_start, date_stop, config_ids, session_ids)
        configs = []
        sessions = []
        if config_ids:
            configs = self.env['pos.config'].search([('id', 'in', config_ids)])
            if session_ids:
                sessions = self.env['pos.session'].search([('id', 'in', session_ids)])
            else:
                sessions = self.env['pos.session'].search(
                    [('config_id', 'in', configs.ids), ('start_at', '>=', date_start), ('stop_at', '<=', date_stop)])
        else:
            sessions = self.env['pos.session'].search([('id', 'in', session_ids)])
            for session in sessions:
                configs.append(session.config_id)
        sold_qty = 0
        refund_qty = 0
        for rec in sessions[0].order_ids:
            for line in rec.lines:
                if line.qty >= 0:
                    sold_qty += line.qty
                else:
                    refund_qty += line.qty
        diffrence_amount = sessions[0].cash_register_balance_end_real - sessions[0].total_payments_amount
        data.update({
            'cashier': sessions[0].user_id.name,
            'payment_method': ', '.join(sessions[0].payment_method_ids.mapped('name')),
            'order_count': sessions[0].order_count,
            'sold_qty': sold_qty,
            'refund_qty': refund_qty,
            'close_session_manual_counted': sessions[0].cash_register_balance_end_real,
            'close_session_real_counted': sessions[0].total_payments_amount,
            'diff': diffrence_amount
        })
        return data
