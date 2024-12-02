from odoo import models, fields

class ManufacturingOrderWizard(models.TransientModel):
    _name = 'manufacturing.order.wizard'
    _description = 'Manufacturing Order Creation Wizard'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)

    