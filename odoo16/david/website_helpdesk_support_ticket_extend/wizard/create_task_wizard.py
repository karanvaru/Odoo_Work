# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class CreateTask(models.TransientModel):
    _name = 'create.task'
    _description = 'Create Task Wizard'

    title = fields.Char(
        string="Title"
    )
    user_ids = fields.Many2many(
        'res.users',
        string="Assignees"
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )
    date_deadline = fields.Date(
        string="Deadline",
    )

    @api.model
    def default_get(self, fields):
        result = super(CreateTask, self).default_get(fields)
        helpdesk_id = self.env['helpdesk.support'].browse(self._context.get('active_id'))
        if helpdesk_id.subject:
            task_name = helpdesk_id.subject + '(' + helpdesk_id.name + ')'
        else:
            task_name = helpdesk_id.name
        result.update({
            'user_ids': [(6, 0, helpdesk_id.user_id.ids)],
            'project_id': helpdesk_id.project_id.id,
            'date_deadline': helpdesk_id.close_date,
            'title': task_name,
        })
        return result

    def action_create_tasks(self):
        vals_task = []
        helpdesk_id = self.env['helpdesk.support'].browse(self._context.get('active_id'))
        task_vals = {
            'name': self.title,
            'user_ids': [(6, 0, self.user_ids.ids)],
            'date_deadline': self.date_deadline,
            'project_id': self.project_id.id,
            'partner_id': helpdesk_id.partner_id.id,
            'description': helpdesk_id.description,
            'ticket_id': helpdesk_id.id,
        }
        task_id = self.env['project.task'].sudo().create(task_vals)
        vals_task.append((4, task_id.id))
        vals = {
            'task_id': task_id.id,
            'is_task_created': True,
            'custom_project_task_ids': vals_task,
        }
        helpdesk_id.write(vals)
