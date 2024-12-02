from odoo import api, fields, models, _


class MobileService(models.Model):
    _inherit = 'mobile.service'

    product_id = fields.Many2one(
        'product.product',
        string="Product",
        domain="[('brand_name','=',brand_name)]"
    )

    stock_lot_id = fields.Many2one(
        'stock.lot',
        string='Serial Number',
        domain="[('product_id','=',product_id)]",
        copy=False,
    )

    @api.onchange('stock_lot_id')
    def onchange_stock_lot_id(self):
        if self.stock_lot_id:
            self.imei_no = self.stock_lot_id.name
        else:
            self.imei_no = ''
