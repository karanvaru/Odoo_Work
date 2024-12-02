from odoo import models, fields, api, _



class Partner(models.Model):
    _inherit = 'res.partner'
    
    capex_category_id = fields.Many2one(
        'capex.category',
        string='Capex Category'
    )
