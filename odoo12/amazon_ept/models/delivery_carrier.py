"""
Delivery Carrier
"""
from odoo import models, fields, api


class DeliveryCarrier(models.Model):
    """
        @author : Dhaval Sanghani [19-03-2019]
        Amazon Delivery Code will set at time Update Order Status
        Based on matching shipping service level category Carrier will set in Sales Order
    """
    _inherit = "delivery.carrier"

    amz_delivery_carrier_code = fields.Many2one('amazon.delivery.carrier.code.ept',
                                                string="Amazon Delivery Code")

    shipping_service_level_category = fields.Selection(
        [('Expedited', 'Expedited'), ('NextDay', 'NextDay'), ('SecondDay', 'SecondDay'),
         ('Standard', 'Standard'), ('FreeEconomy', 'FreeEconomy')],
        "Shipping Service Level Category", default='Standard')