# -*- coding: utf-8 -*

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    product_id_helpdesk = fields.Many2one(
        'product.product',
        string='Product',
    )
    
    price_rate = fields.Float(
        string='Price / Rate (Company Currency)',
        default=lambda self :('0'),
        copy=False,
    )
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for project in self:
            project.price_rate = project.partner_id.price_rate
            project.product_id_helpdesk = project.partner_id.product_id_helpdesk
    
