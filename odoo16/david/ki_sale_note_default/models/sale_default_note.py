from odoo import api, fields, models, _


class SaleDefaultNote(models.Model):
    _name = "sale.default.note.template"

    name = fields.Char(
        string="Name",
        required=True
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string="Customer",
    )
    note = fields.Char(
        string="Note",
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
    )
    product_note = fields.Char(
        string="Note",
    )
