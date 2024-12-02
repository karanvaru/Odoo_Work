# -*- coding: utf-8 -*-

from odoo import models, fields

class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'
    
    custom_project_id = fields.Many2one(
        'project.project',
        string='Project',
        copy=True,
    )
    custom_task_id = fields.Many2one(
        'project.task',
        string='Task / Job Order',
        copy=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
