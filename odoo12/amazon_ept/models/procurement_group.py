from odoo import models, fields


class procurement_group(models.Model):
    _inherit = 'procurement.group'

    odoo_shipment_id = fields.Many2one('amazon.inbound.shipment.ept', string='Shipment')
    removal_order_id = fields.Many2one('amazon.removal.order.ept',string='Removal Order')
