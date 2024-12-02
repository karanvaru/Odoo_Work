from odoo import models, api

class PurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    @api.onchange('task_id')
    def custom_onchange_task_new(self):
        for rec in self:
            rec.custom_task_id = rec.task_id.id


    @api.onchange('project_id')
    def custom_onchange_project_new(self):
        for rec in self:
            rec.custom_project_id = rec.project_id.id

