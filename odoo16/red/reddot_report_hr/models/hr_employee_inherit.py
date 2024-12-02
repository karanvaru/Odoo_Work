from odoo import _, api, fields, models


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    probation_renewal_date = fields.Date(
        string='Probation Renewal Date',
        store=True
    )
    

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    probation_renewal_date = fields.Date(
        string='Probation Renewal Date',
        store=True
    )