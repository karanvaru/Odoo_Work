from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    delivery_item_template_id = fields.Many2one(
        "sale.order.template",
        string="Delivery Item Template",
    )
    delivery_item_ids = fields.One2many(
        "sale.delivery.items",
        "order_id",
        string="Deliverable Item"
    )

    @api.onchange('delivery_item_template_id')
    def _onchange_delivery_item_template(self):
        self.delivery_item_ids = [(5, 0, 0)]
        for rec in self.delivery_item_template_id.sale_order_template_line_ids:
            vals = {
                'product_id': rec.product_id.id,
                'description': rec.name,
                'quantity': rec.product_uom_qty,
                'uom_id': rec.product_uom_id.id,
                'unit_price': rec.product_id.lst_price,
                'tax_ids': rec.product_id.taxes_id.ids,
            }
            self.delivery_item_ids = [(0, 0, vals)]
