from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        picking = super(StockPicking, self).create(vals)
        custom_requisition_id = picking.custom_requisition_id
        if picking.custom_requisition_id:
            picking.update({
                'jobcard_id' : custom_requisition_id.task_id.id,
                'custom_analytic_account_id' : custom_requisition_id.analytic_account_id.id,
                'custom_project_id' : custom_requisition_id.custom_project_id.id,
            })
        return picking

