from odoo import models, fields, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    email_employee_ids = fields.Many2many(
        'hr.employee',
        string="Employee"
    )
