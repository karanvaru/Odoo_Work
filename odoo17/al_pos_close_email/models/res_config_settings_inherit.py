from odoo import fields, models, api, _


class ResConfigSettingsInheritance(models.TransientModel):
    _inherit = "res.config.settings"

    email_employee_ids = fields.Many2many(
        'hr.employee',
        related='company_id.email_employee_ids',
        string="Employee",
        readonly=False,
    )