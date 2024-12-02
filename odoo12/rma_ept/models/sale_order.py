from odoo import models,fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def compute_rma(self):
        for order in self:
            rma=self.env['crm.claim.ept'].search([('picking_id.sale_id','=',order.id)])
            order.rma_count = len(rma)
    
    rma_count = fields.Integer('RMA',compute=compute_rma)
    
    @api.multi
    def action_view_rma(self):
        rma=self.env['crm.claim.ept'].search([('picking_id.sale_id','=',self.id)])
        if len(rma)==1:
            return {
            'name': "RMA",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.claim.ept',
            'type': 'ir.actions.act_window',
            'res_id':rma.ids[0]
            }
        else:
            return {
            'name': "RMA",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'crm.claim.ept',
            'type': 'ir.actions.act_window',
            'domain':[('id','in',rma.ids)]
            }