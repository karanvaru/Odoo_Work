from odoo import models, fields

class ShiprocketShippingCharge(models.Model):
    _name = "shiprocket.shipping.charge"
    _rec_name = "courier_name"

    courier_name = fields.Char(string="Courier Name", help="Courier Name.")
    courier_id = fields.Char(string="Courier Company ID", help="Courier Company ID")
    rate_amount = fields.Float(string="Service Rate", help="Rate given by Shippit")
    estimated_transit_time = fields.Char(string="Estimated Transit Time", help="Estimated Transit Time.")
    picking_id = fields.Many2one("stock.picking", string="Delivery Order")

    def set_service(self):
        self.ensure_one()
        self.picking_id.shiprocket_shipping_charge_id = self.id
