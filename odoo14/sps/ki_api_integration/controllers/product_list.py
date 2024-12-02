from odoo import http, _, fields
from odoo.http import request


class ProductList(http.Controller):

    @http.route('/web/product/list', type='json', auth="user")
    def product_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        user_id = request.env['res.users'].browse(uid)
        try:
            # contract_id = int(kw.get('contract_id', False))
            category_id = int(kw.get('category_id', False))
            name = kw.get('name', False)
            # default_code = kw.get('default_code', False)
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit <= 1:
                limit = 10

            domain = [('product_status', '=', 'active')]
            data = []
            product_length = 0
            if name and name != '':
                domain.append('|')
                domain.append(('name', 'ilike', name))
                domain.append(('default_code', '=', name))

            if category_id:
                category_browse_id = request.env['product.category'].browse(category_id)
                if category_browse_id.type == 'printer':
                    domain.append(('categ_id.type', '=', 'printer'))
                else:
                    domain.append(('categ_id.type', '=', 'cartridge'))

            product = request.env['product.product'].search(domain, limit=limit, offset=start)
            product_length = request.env['product.product'].search_count(domain)
            for rec in product:
                res = request.env['contract.line'].sudo().search(
                    [('product_id.default_code', '=', rec.default_code), ('contract_id.state', '=', 'active')],
                    limit=limit,
                    offset=start)
                contract_line = res.filtered(lambda i: i.product_id == rec)

                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'default_code': rec.default_code,
                    'image_url': base_url + '/web/image/product.product/%s/image_1920' % rec.id,
                    'date_start': res.date_start,
                    'partner_id': {
                        'id': contract_line.contract_id.partner_id.id,
                        'name': contract_line.contract_id.partner_id.name,
                    },
                    'partner_shipping_id': {
                        'id': contract_line.contract_id.partner_shipping_id.id,
                        'name': contract_line.contract_id.partner_shipping_id.name,
                    },
                    'category_id': {
                        'id': rec.categ_id.id,
                        'name': rec.categ_id.name,
                    }
                    # 'barcode': rec.barcode,
                    # 'categ_id': rec.categ_id.name,
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
            'message': 'Products Found Successfully!',
            'data': data,
            'records': product_length
        }

    @http.route('/web/product/search', type='json', auth="user")
    def product_search(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            name = kw.get('name', False)
            type = kw.get('type', False)

            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            if limit <= 1:
                limit = 10
            domain = []
            if name:
                domain = ['|', ('name', 'ilike', name), ('default_code', '=', name)]
            if type:
                domain.append(('categ_id.type', '=', type))
            product_id_length = request.env['product.product'].sudo().search_count(domain)
            product = request.env['product.product'].sudo().search(domain, limit=limit, offset=start, order='name')
        except Exception as e:
            return {
                'code': 100,
                'message': e,
                'data': []
            }
        if not product:
            return {
                'code': 100,
                'message': 'Product Not Found!',
                'data': []
            }
        data = []
        for rec in product:
            data.append(
                {
                    'id': rec.id,
                    'name': rec.name,
                    'default_code': rec.default_code,
                    'categ_id': {
                        'id': rec.categ_id.id,
                        'name': rec.categ_id.name
                    }
                }
            )
        return {
            'code': 1000,
            'message': 'Product Found Successfully!',
            'data': data,
            'records': product_id_length
        }
