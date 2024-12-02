from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    carrier_pickup_time = fields.Datetime("Pickup Date")
    def create_bludart_label(self):
        if self.delivery_type == "bluedart_ts":
            res = self.carrier_id.bluedart_ts_send_shipping(self)
            self.write({'carrier_tracking_ref': res[0].get('tracking_number', ''),
                        'carrier_price': res[0].get('exact_price', 0.0)})

