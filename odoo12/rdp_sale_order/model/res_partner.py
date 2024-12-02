from odoo import fields,models,api,_
from datetime import datetime, timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'

    so_gem_rp_count = fields.Integer('GeM SO', compute='compute_so_gem_rp_count')
    # sale_gem_rp = fields.Boolean('SO GeM RP', default=False)

    def compute_so_gem_rp_count(self):
        for rec in self:
            rec.so_gem_rp_count = rec.env['sale.order'].search_count([('so_gem_rp_id.id','=',rec.id)])

    def sale_order_gem_rp_count(self):
        return {
            'name': 'SaleOrder',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [('so_gem_rp_id.id','=',self.id)],
        }