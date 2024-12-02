from odoo import models, fields, api, _


class SaleDeliveryItem(models.Model):
    _name = 'sale.delivery.items'

    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )
    description = fields.Text(
        'Description'
    )
    quantity = fields.Float(
        "Quantity"
    )
    delivered = fields.Float(
        "Delivered"
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="UOM",
    )
    unit_price = fields.Float(
        "Unit Price"
    )
    tax_ids = fields.Many2many(
        'account.tax',
        string="Taxes"
    )
    discount = fields.Float(
        "Disc %"
    )
    sub_total = fields.Float(
        "Subtotal",
        compute="_compute_sub_total"
    )
    order_id = fields.Many2one(
        'sale.order',
    )

    @api.depends('unit_price', 'quantity')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.unit_price * rec.quantity

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.unit_price = rec.product_id.lst_price
            rec.tax_ids = rec.product_id.taxes_id.ids
