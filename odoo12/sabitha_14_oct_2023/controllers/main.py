from odoo import http
from odoo.addons.sabitha_14_oct_2023.models import manufacturing_order_wizard

class ManufacturingOrderWizardController(http.Controller):
    @http.route('/manufacturing_order/create', auth='user', type='json')
    def action_create_manufacturing_order(self, **post):
        data = post.get('form')
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        manufacturing_order = self.create_manufacturing_order(product_id, quantity)

        return {'manufacturing_order_id': manufacturing_order.id}
