from odoo import http, _, fields
from odoo.http import request


class WEBBarcode(http.Controller):

    # Contract Details
    @http.route('/web/contract/details', type='json', auth="none")
    def contract_details(self, **kw):
        uid = request.session.uid
        # if not uid:
        #     return {
        #         'code': 100,
        #         'message': 'Session Expired!',
        #         'data': []
        #     }
        default_code = kw.get('default_code', False)
        try:
            res = request.env['contract.line'].sudo().search(
                [('product_id.default_code', '=', default_code), ('contract_id.state', '=', 'active')], limit=1)
            data = []
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            print('1111111111111111111111', res)
            if not res:
                product = request.env['product.product'].sudo().search(
                    [('default_code', '=', default_code), ('categ_id.type', '=', 'cartridge')], limit=1)
                if product:
                    vals = {
                        'product_id': {
                            'id': product.id,
                            'name': product.display_name,
                            'asset_number': product.default_code,
                            'serial_number': product.barcode,
                            'image_url': base_url + '/web/image/product.product/%s/image_1920' % product.id,
                        },
                        'partner_id': {
                            'id': product.customer_id.id,
                            'name': product.customer_id.name,
                            'street': product.customer_id.street,
                            'street2': product.customer_id.street2,
                            'city': product.customer_id.city,
                            'state': product.customer_id.state_id.name,
                            'zip': product.customer_id.zip,
                            'country': product.customer_id.country_id.name
                        },
                        'partner_shipping_id': {
                            'id': product.partner_shipping_pro_id.id,
                            'name': product.partner_shipping_pro_id.name,
                        },
                        'category_id': {
                            'id': product.categ_id.id,
                            'name': product.categ_id.name,
                        }
                    }
                    data.append(vals)
                    return {
                        'code': 1000,
                        'message': 'Product Found Successfully!',
                        'data': data,
                    }

                else:
                    return {
                        'code': 1001,
                        'message': '!!! Contract not Found !!!',
                        'data': [],
                        'register_data': [],
                        'refill_data': []
                    }

            else:
                for rec in res:
                    vals = {
                        'contract_id': {
                            'contract_id': rec.contract_id.id,
                            'name': rec.contract_id.name,
                        },
                        'date_start': rec.contract_id.date_start,
                        'Location': {
                            'id': rec.contract_id.partner_shipping_id.id,
                            'name': rec.contract_id.partner_shipping_id.name
                        },
                        'partner_id': {
                            'id': rec.contract_id.partner_id.id,
                            'name': rec.contract_id.partner_id.name,
                            'street': rec.contract_id.partner_id.street,
                            'street2': rec.contract_id.partner_id.street2,
                            'city': rec.contract_id.partner_id.city,
                            'state': rec.contract_id.partner_id.state_id.name,
                            'zip': rec.contract_id.partner_id.zip,
                            'country': rec.contract_id.partner_id.country_id.name
                        },
                        'product_id': {
                            'id': rec.product_id.id,
                            'name': rec.product_id.name,
                            'asset_number': rec.product_id.default_code,
                            'serial_number': rec.product_id.barcode,
                        },
                        'department': rec.department
                    }
                    data.append(vals)

        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }

        return {
            'code': 1000,
            'message': 'Contract Found Successfully!',
            'data': data,
        }
