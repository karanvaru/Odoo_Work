from odoo import models,fields,api

class stock_warehouse(models.Model):
    _inherit='stock.warehouse'
    
    return_partner_id=fields.Many2one('res.partner',"Return Address")