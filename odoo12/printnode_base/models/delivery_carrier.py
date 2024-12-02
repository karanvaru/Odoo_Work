# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    autoprint_paperformat_id = fields.Many2one(
        comodel_name='printnode.paper',
        string='Autoprint Paper Format',
        help=(
            'This settings defines which paperformat '
            'should be chosen for printing lables of this carrier.'
        ),
    )
