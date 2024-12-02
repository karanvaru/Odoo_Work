# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    # @api.multi #odoo13
    def show_mpr_project_action(self):
        self.ensure_one()
        #res = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition')
        res = self.env['ir.actions.act_window']._for_xml_id('material_purchase_requisitions.action_material_purchase_requisition')
        #res = res.sudo().read()[0]
        res['domain'] = str([('custom_project_id', '=', self.id)])
        return res

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # @api.multi #odoo13
    def show_mpr_task_action(self):
        self.ensure_one()
        # res = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition')
        res = self.env['ir.actions.act_window']._for_xml_id('material_purchase_requisitions.action_material_purchase_requisition')
        #res = res.sudo().read()[0]
        res['domain'] = str([('custom_task_id', '=', self.id)])
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
