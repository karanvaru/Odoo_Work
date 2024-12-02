# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InstructionJobOrder(models.Model):
    _name = "instruction.job.order"
    _description = 'Instruction Job Order'
    
    name = fields.Char(
        string="Number",
        readonly= True,
    )
    pick_date = fields.Date(
        string="Date",
        default=fields.Date.today(),
        #readonly= True,
    )
    user_id = fields.Many2one(
        'res.users',
        string="User",
        default= lambda self: self.env.user.id,
        readonly=True,
    )
    description = fields.Char(
        string="Instructions",
        required=True,
    )
    status = fields.Selection(
        selection=[('pending','Pending'),
                    ('in_progress','In Progress'),
                    ('complete','Complete'),
                    ('cancel', 'Cancelled')
        ],
        string='Status',
        default='in_progress',
        required=True,
    )
    start_date = fields.Datetime(
        string="Start Date",
        default=fields.Datetime.now,
    )
    end_date = fields.Datetime(
        string="End Date",
        default=fields.Datetime.now,
    )
    note = fields.Text(
        string="Notes"
    )
    task_id = fields.Many2one(
        'project.task',
        string="Task"
    )

    @api.model
    def create(self, vals):
        result = super(InstructionJobOrder, self).create(vals)
        for record in result:
            if result.task_id and result.task_id.number:
                order_id = self.env['instruction.job.order'].search([('task_id', '=', result.task_id.id)])
                record.name = result.task_id.number + ' / ' + str(len(order_id))
        return result

    #@api.multi
    def name_get(self):
        return [(instruction.id, '%s%s' % (instruction.name and '[%s] ' % instruction.name or '', instruction.description))
                for instruction in self]
