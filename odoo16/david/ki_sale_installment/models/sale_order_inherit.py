from odoo import models, fields,api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    sale_installment_plan_id = fields.Many2one(
        'sale.installment.plan',
        string='Installment Plan'
    )

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        res = super(SaleOrderInherit, self)._get_invoiced()
        for order in self:
            invoices = self.env['account.move'].sudo().search([('custom_sale_id','=',self.id)])
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
        return res