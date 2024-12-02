from odoo import models, fields, api


class amazon_fulfillment_center(models.Model):
    _name = "amazon.fulfillment.center"
    _description = 'amazon.fulfillment.center'
    _rec_name = 'center_code'

    @api.one
    @api.depends('warehouse_id', 'warehouse_id.seller_id')
    def _get_seller_id(self):
        if self.warehouse_id and self.warehouse_id.seller_id:
            self.seller_id = self.warehouse_id.seller_id.id

    seller_id = fields.Many2one('amazon.seller.ept', string='Amazon Seller', compute=_get_seller_id,
                                store=True, readonly=True)
    center_code = fields.Char(size=50, string='Fulfillment Center Code', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    _sql_constraints = [('fulfillment_center_unique_constraint', 'unique(seller_id,center_code)',
                         "Fulfillment center must be unique by seller.")]


class res_partner(models.Model):
    _inherit="res.partner"
    
    fax = fields.Char("Fax",help="Fax Number")