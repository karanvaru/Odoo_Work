from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(selection_add=[('gati_ts', 'Gati')])


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"
    gati_packet_id = fields.Many2one('gati.docket.package.number', string="Gati Package Number")

