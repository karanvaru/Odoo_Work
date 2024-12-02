from odoo import models,fields,api
class stock_location_route(models.Model):
    _inherit="stock.location.route"
    
    is_removal_order=fields.Boolean("Is Removal Order ?",default=False)