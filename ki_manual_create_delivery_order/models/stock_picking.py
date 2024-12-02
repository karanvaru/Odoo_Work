from odoo import api, fields, models, _


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order Reference',
        related='sale_line_id.order_id'
    )
