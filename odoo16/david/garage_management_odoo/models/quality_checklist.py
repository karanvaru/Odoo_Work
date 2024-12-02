# -*- coding: utf-8 -*-

from odoo import fields, models

class QualityChecklist(models.Model):
    _inherit = "quality.checklist"

    checklist_name_ids = fields.Many2many(
    	'quality.checklist.name',
        store=True,
    	string="Checklists"
    )