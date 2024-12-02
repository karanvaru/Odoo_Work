from odoo import _, api, fields, models


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_anual_type = fields.Boolean(
        string='Is Anual Type?',
    )