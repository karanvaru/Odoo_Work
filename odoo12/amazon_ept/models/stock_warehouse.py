from odoo import models, fields


class stock_warehouse(models.Model):
    _inherit = "stock.warehouse"

    seller_id = fields.Many2one('amazon.seller.ept', string='Amazon Seller')


    fulfillment_center_ids = fields.One2many('amazon.fulfillment.center', 'warehouse_id',
                                             string='Fulfillment Centers')
    is_fba_warehouse = fields.Boolean("Is FBA Warehouse ?")
    validity_days = fields.Integer('Validity Days',
                                   help="If days, are set, system will set validity date when "
                                        "reserving product in sale order.")
    unsellable_location_id = fields.Many2one('stock.location', string="Unsellable Location",
                                             help="Amazon unsellable location")
