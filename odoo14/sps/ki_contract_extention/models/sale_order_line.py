from odoo import api, fields, models, _


class ContractExtention(models.Model):
    _inherit = "sale.order.line"

    location = fields.Char(string='Location')

