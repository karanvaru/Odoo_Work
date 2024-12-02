from odoo import fields, models, api


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    port_code = fields.Char("Port Code")
