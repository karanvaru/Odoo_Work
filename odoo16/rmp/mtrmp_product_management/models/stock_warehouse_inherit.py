from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    user_id = fields.Many2one('res.users', string="Manager")

    def _cron_critical_products(self):
        for wh in self.env['stock.warehouse'].search([]):
            manager = wh.user_id
            email_tmpl = self.env.ref('mtrmp_product_management.critical_stock_product_mail_template')
            critical_products = self.env['product.product'].with_context(warehouse=wh.id).search([]).filtered(
                lambda p: p.virtual_available <= p.min_qty
            )
            email_values = {
                'products': critical_products,
                'manager': manager.email
            }
            email_tmpl.with_context(email_values).send_mail(wh.id, force_send=True, email_values=None)
