from odoo import api, fields, models, _


class BusinessCategory(models.Model):
    _name = 'business.category'

    name = fields.Char(
        string="Name",
        required=True
    )