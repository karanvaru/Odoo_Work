# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ChecklistName(models.Model):
    _name = "checklist.name.line"
    _description = 'Quality Checklist Line'

    task_id = fields.Many2one(
        'project.task'
    )
    checklist_id = fields.Many2one(
        'quality.checklist',
        string='Checklist'
    )
    checkbox = fields.Boolean(
        string='Checkbox',
        default=False
    )
    checklist_name_id = fields.Many2one(
        'quality.checklist.name',
        string='Checklist Names'
    )