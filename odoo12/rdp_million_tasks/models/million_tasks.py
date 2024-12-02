from odoo import api, fields, models, _
from datetime import date, datetime
import time


class MillionTasks(models.Model):
    _name = "million.tasks"
    _description = "Million Tasks"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Reference No", copy=False, index=True,
                       default=lambda self: _('New'))
    tasks = fields.Many2one('m.tasks', string="Tasks")
    category = fields.Many2one('c.category', string="Category")
    job_position = fields.Many2one('hr.job', string="Job Position")
    notes = fields.Text('Notes')
    parent = fields.Many2one(string="Parent Category", related="category.parent_category")
    responsible_id = fields.Many2one('res.users', string="Responsible")
    accountable_id = fields.Many2one('res.users', string="Accountable")
    consulted_id = fields.Many2one('res.users', string="Consulted")
    informed_id = fields.Many2one('res.users', string="Informed")
    department_id = fields.Many2one("hr.department", string="Department", compute="compute_job_position", store="1")
    parent_department_id = fields.Many2one("hr.department", string="Parent Department", compute="compute_job_position", store="1")


    @api.depends('job_position')
    def compute_job_position(self):
        for record in self:
            record.department_id = record.job_position.department_id.id
            record.parent_department_id = record.job_position.x_studio_field_4XmH5.id


    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('million.tasks.sequence'),
        })
    
        return super(MillionTasks, self).create(vals)


class Tasks(models.Model):
    _name = "m.tasks"

    name = fields.Char(string="Name")


class Category(models.Model):
    _name = "c.category"

    name = fields.Char(string="Name")
    parent_category = fields.Many2one('c.category', string="Parent Category")


class JobPostionsPage(models.Model):
    _inherit = "hr.job"

    name = fields.Char(string="Name")
    million_tasks = fields.One2many('million.tasks', string="Million Tasks", compute="million_tasks_page")

    @api.multi
    def million_tasks_page(self):
        for rec in self:
            tasks_id = self.env['million.tasks'].search([('job_position', '=', rec.id)])
            if tasks_id:
                rec.million_tasks = tasks_id

            # vals ={
            #     'million_tasks': [(0, 0,{'tasks': ts.tasks.id, 'category': ts.category})for ts in self.million_tasks]
            #     }
            # return vals
