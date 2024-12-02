
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_passport_number = fields.Char(
        string="ED No/Passport No",
    )
    staying_at = fields.Char(
        string="Last Staying at",
        readonly=True
    )
