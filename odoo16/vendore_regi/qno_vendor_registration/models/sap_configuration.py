from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SapConfiguration(models.Model):
    _name = 'sap.configuration'

    # company_id = fields.Many2one(
    #     'res.company',
    #     string='Company',
    #     readonly=True,
    #     default=lambda self: self.env.company
    # )
    url = fields.Char(
        string="Url",
        # related='company_id.url',
        readonly=True,
    )
    api_url = fields.Char(
        string="API Url",
        # related='company_id.api_url'
    )
    database_name = fields.Char(
        string="Database",
        # related='company_id.database_name'
    )
    active = fields.Boolean(
        string="Active",
        # related='company_id.custom_active'
    )

    @api.constrains('active')
    def _check_active(self):
        for record in self:
            exist = self.search_count([('active', '=', True)])
            if exist > 1:
                raise ValidationError(_('You can activate only one configuration at time!'))
