from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(selection_add=[('bluedart_ts', 'Blue Dart')])
