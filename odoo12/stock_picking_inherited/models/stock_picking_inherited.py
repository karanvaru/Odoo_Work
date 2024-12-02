from odoo import models,fields,api,_

class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'