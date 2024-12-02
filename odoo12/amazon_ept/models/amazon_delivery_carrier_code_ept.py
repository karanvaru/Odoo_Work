"""
Amazon Delivery Carrier Code
"""
from odoo import models, fields


class AmazonDeliveryCarrierCodeEpt(models.Model):
    """
        @author : Dhaval Sanghani [19-03-2019]
        This model provides list of Amazon Delivery Carrier Code
    """
    _name = "amazon.delivery.carrier.code.ept"
    _description = 'amazon.delivery.carrier.code.ept'

    name = fields.Char('Carrier Code')
