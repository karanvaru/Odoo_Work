from odoo import models, fields, api


class amazon_inventory_wizard(models.TransientModel):
    _name = "amazon.inventory.wizard"
    _description = 'amazon.inventory.wizard'

    instance_id = fields.Many2one("amazon.instance.ept", "Instance")
    fba_warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse",
                                       related="instance_id.fba_warehouse_id", readonly=True)

    @api.multi
    def import_products_stock(self):
        self.env['stock.inventory'].import_amazon_fba_stock(self.instance_id)
        return True
