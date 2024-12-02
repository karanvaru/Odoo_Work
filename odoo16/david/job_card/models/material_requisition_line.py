# -*- coding: utf-8 -*-

from odoo import models, fields


class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = 'material.purchase.requisition.line'

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        related='requisition_id.task_id',
        store=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
