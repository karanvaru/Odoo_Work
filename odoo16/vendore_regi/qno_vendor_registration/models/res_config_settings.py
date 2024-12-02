from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    url = fields.Char(
        string="Url",
        readonly=False,
        store=True,
        related="company_id.url",
    )
    api_url = fields.Char(
        string="API Url",
        readonly=False,
        store=True,
        related="company_id.api_url",
    )
    database_name = fields.Char(
        string="Database",
        readonly=False,
        store=True,
        related="company_id.database_name",
    )
    active = fields.Boolean(
        string="Active",
        readonly=False,
        store=True,
        related="company_id.custom_active",
    )
