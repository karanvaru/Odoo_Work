# -*- coding: utf-8 -*

from odoo import models, fields, api

class ProjectPrice(models.Model):
    _inherit = 'project.task'
    
    price_rate = fields.Float(
        string='Price / Rate (Company Currency)',
        default=0.0,
        copy=False,
    )

    product_id_helpdesk = fields.Many2one(
        'product.product',
        string='Product',
    )
    
    @api.onchange('project_id')
    def _onchange_project_custom(self):
        # result = super(ProjectPrice, self)._onchange_project()
        self.price_rate = self.project_id.price_rate
        self.product_id_helpdesk = self.project_id.product_id_helpdesk
        # return result
    
    
