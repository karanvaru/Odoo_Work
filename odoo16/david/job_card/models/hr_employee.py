# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
    
#     workshop_position_id = fields.Many2one(
#         'workshop.position',
#         string="Workshop Position"
#     )
    workshop_position_type = fields.Selection(
        [('leader','Leader'),
         ('worker','Worker')],
        string="Workshop Position",
        groups='hr.group_hr_user',
    )

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
#     workshop_position_id = fields.Many2one(
#         'workshop.position',
#         string="Workshop Position"
#     )
    workshop_position_type = fields.Selection(
        [('leader','Leader'),
         ('worker','Worker')],
        string="Workshop Position",
        groups='hr.group_hr_user',
    )

 