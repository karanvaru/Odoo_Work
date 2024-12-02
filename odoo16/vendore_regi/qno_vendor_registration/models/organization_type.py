from odoo import api, fields, models, _


class OrganizationType(models.Model):
    _name = 'organization.type'

    name = fields.Char(
        string="Name",
        required=True
    )