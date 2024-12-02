from odoo import api, fields, models, _


class ContractExtention(models.Model):
    _inherit = "contract.line"

    location = fields.Char(string='Location')


