from odoo import api, fields, models, _


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    panel_type = fields.Selection([
        ('acdb', 'ACDB'),
        ('dcdb', 'DCDB'),
        ('inverter', 'Inverter'),
        ('solar_panel', 'Solar Panel'),
    ], string='Panel Type')
