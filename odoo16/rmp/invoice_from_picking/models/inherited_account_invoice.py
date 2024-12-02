# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class Accountinvoice(models.Model):
    _inherit = 'account.move'

    picking_ids = fields.Many2many('stock.picking', string="Picking References")

    original_order_lines = fields.Many2many(
        'sale.order.line',
        string="Original Order Lines"
    )

