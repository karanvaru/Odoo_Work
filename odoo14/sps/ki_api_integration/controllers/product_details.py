from odoo import http, _, fields
from odoo.http import request


class ProductDetails(http.Controller):

    @http.route('/web/product/details', type='json', auth="user")
    def product_details(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            product_id = int(kw.get('product_id', False))
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not product_id:
                return {
                    'code': 1001,
                    'message': '!!! Product not Found !!!',
                    'data': [],
                    'register_data': [],
                    'refill_data': []
                }

            else:
                res = request.env['product.product'].sudo().search(
                    [('id', '=', product_id), ('product_status', '=', 'active')])
                register_line_id = request.env['product.in.out.register.lines'].sudo().search(
                    [('product_id', '=', product_id)])
                refill_id = request.env['refill.request'].sudo().search(
                    [('product_id', '=', product_id)])
                refill_data = []
                register_data = []
                val = {
                    'name': res.name,
                    'default_code': res.default_code,
                    'image_url': base_url + '/web/image/product.product/%s/image_1920' % res.id,
                    'date_start': res.current_contract_id.date_start,
                    'contract_id': {
                        'id': res.current_contract_id.id,
                        'name': res.current_contract_id.name
                    },
                    'product_id': {
                        'id': res.id,
                        'name': res.name,
                    },
                    'partner_id': {
                        'id': res.current_contract_id.partner_id.id,
                        'name': res.current_contract_id.partner_id.name,
                    },
                    'partner_shipping_id': {
                        'id': res.current_contract_id.partner_shipping_id.id,
                        'name': res.current_contract_id.partner_shipping_id.name,
                    },
                }
                if refill_id:
                    for refill in refill_id:
                        vals = {
                            'id': refill.id,
                            'name': refill.name,
                            'date': refill.date,
                        }
                        refill_data.append(vals)
                if register_line_id:
                    for reg in register_line_id:
                        value = {
                            'id': reg.id,
                            'name': reg.reference,
                            'date': reg.date,
                            'quantity': reg.quantity,
                            'operation_type': reg.operation_type,
                            'partner_id': reg.partner_id.id,
                        }
                        register_data.append(value)
                val['register_data'] = register_data
                val['refill_data'] = refill_data
        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': [],
                'register_data': [],
                'refill_data': []
            }
        return {
            'code': 1000,
            'message': 'Product Found Successfully!',
            'data': val,
        }
