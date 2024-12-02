# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
#from openerp.exceptions import UserError
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    instruction_job_id = fields.Many2one(
        'instruction.job.order',
        string="Instruction No",
        required=False,
        domain = [('status', '!=', 'cancel')]
    )
    description = fields.Char(
        string="Instructions",
        related = 'instruction_job_id.description',
        readonly=True,
    )
    leader_id = fields.Many2one(
        'hr.employee',
        string="Leader",
        required=False,
        domain = [('workshop_position_type', '=', 'leader')],
    )
    workers_ids = fields.Many2many(
        'hr.employee',
        string="Workers",
        required=False,
        domain = [('workshop_position_type', '=', 'worker')],
    )
    note = fields.Text(
        string="Report",
        required=False,
    )
    task_id = fields.Many2one(
        'project.task',
        string="Job Order"
    )

    @api.onchange('instruction_job_id')
    def onchnage_instruction_job_id(self):
        for rec in self:
            rec.description = rec.instruction_job_id.description
            rec.name = rec.instruction_job_id.description

