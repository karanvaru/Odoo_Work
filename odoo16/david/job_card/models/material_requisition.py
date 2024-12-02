# -*- coding: utf-8 -*-

from odoo import models, fields


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    task_id = fields.Many2one(
        'project.task',
        string='Job Card',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
