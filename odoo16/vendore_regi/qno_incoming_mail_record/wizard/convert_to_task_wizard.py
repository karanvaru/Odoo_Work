# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ConvertToTaskWizard(models.TransientModel):
    _name = 'convert.to.task.wizard'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )

    user_ids = fields.Many2many(
        'res.users',
        string='Assignee',
    )

    def convert_to_task(self):
        project_task = self.env['project.task']
        active_model = self._context.get('active_model', False)
        mail_records = self.env[active_model].search([('id', 'in', self._context.get('active_ids', []))])

        data_list = []
        for rec in mail_records:
            if not rec.task_id:
                task_dct = {
                    'name': rec.name,
                    'description': rec.description
                }
                if self.project_id:
                    task_dct['project_id'] = self.project_id.id
                if self.user_ids:
                    task_dct['user_ids'] = self.user_ids

                task = project_task.create(task_dct)
                rec.task_id = task.id
            else:
                data_list.append(rec)
        if data_list:
            error_data = ''
            for rec in data_list:
                error_data += '\n' + rec.name
            raise ValidationError("Task already created for :   %s" % error_data)
