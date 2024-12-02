import dateutil.utils
from odoo import http, _, fields
from odoo.http import request


class PartsAdd(http.Controller):

    # Parts List
    @http.route('/web/parts/add/list', type='json', auth="user")
    def parts_add_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            product_id = int(kw.get('product_id', False))
            if not product_id:
                return {
                    'code': 200,
                    'message': 'Please Enter Product!!',
                    'data': []
                }
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit <= 1:
                limit = 10
            domain1 = [('id', '=', product_id)]
            pro_parts_id = request.env['product.product'].sudo().search(domain1, limit=limit, offset=start,
                                                                        order='write_date desc')
            pro_parts_length = len(pro_parts_id.part_product_line_ids.ids)
            if not pro_parts_id:
                return {
                    'code': 1001,
                    'message': '!!! Parts not Found !!!',
                    'data': [],
                }
            data = []
            for rec in pro_parts_id.part_product_line_ids:
                vals = {
                    'product_part_id': rec.product_part_id.id,
                    'name': rec.product_part_id.display_name,
                    'note': rec.note,
                    'product_qty': rec.product_qty,
                }
                data.append(vals)
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'Prats Found Successfully!!',
            'data': data,
            'records': pro_parts_length
        }

    # @http.route('/web/cartridge/validation', type='json', auth="user")
    # def cartridge_validation(self, **kw):
    #     uid = request.session.uid
    #     if not uid:
    #         return {
    #             'code': 100,
    #             'message': 'Session Expired!',
    #             'data': []
    #         }
    #     try:
    #         default_code = kw.get('default_code', False)
    #         url_params = request.httprequest.args.to_dict()
    #         start = int(url_params.get('start', 0))
    #         end = int(url_params.get('end', 0))
    #         limit = end + 1 - start
    #         if limit <= 1:
    #             limit = 10
    #         # domain = [('categ_id.type', '=', 'cartridge'), ('default_code', '=', default_code)]
    #         if not default_code:
    #             return {
    #                 'code': 200,
    #                 'message': 'Product Not Found!!',
    #                 'data': []
    #             }
    #         domain1 = [('default_code', '=', default_code)]
    #         pro_parts_id = request.env['product.product'].sudo().search(domain1, limit=limit, offset=start,
    #                                                                     order='write_date desc')
    #         product_part = []
    #         for i in pro_parts_id.part_product_line_ids:
    #             val_line = {
    #                 'product_part_id': i.product_part_id.id,
    #                 'product_name': i.product_part_id.display_name,
    #                 'qty': i.product_qty,
    #                 'note': i.note or ""
    #             }
    #             product_part.append(val_line)
    #
    #         data = []
    #         if not pro_parts_id:
    #             return {
    #                 'code': 1001,
    #                 'message': '!!! Product not Found !!!',
    #                 'data': [],
    #             }
    #         for recs in pro_parts_id:
    #             vals = {
    #                 'id': recs.id,
    #                 'name': recs.display_name,
    #                 'default_code': recs.default_code,
    #                 'categ_id': recs.categ_id.id,
    #                 'part_product_line_ids': product_part,
    #             }
    #         data.append(vals)
    #
    #     except Exception as e:
    #         return {
    #             'code': 1001,
    #             'message': e,
    #             'data': []
    #         }
    #     return {
    #         'code': 1000,
    #         'message': 'Cartridge Found Successfully!',
    #         'data': data,
    #         # 'records': pro_parts_length
    #     }

    @http.route('/web/parts/add/create', type='json', auth="user")
    def parts_add_create(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        product_part_id = request.env['cartridge.part.line'].sudo().search([])
        try:
            product_id = int(kw.get('product_id', False))
            date = kw.get('date', False)
            data = []
            for rec in kw.get('part_line_ids', []):
                vals = {
                    'product_id': product_id,
                    'date': date,
                    'product_part_id': rec['product_part_id'],
                    'product_qty': rec['product_qty'],
                    'note': rec['note']
                }
                data.append(vals)
                res = product_part_id.sudo().create(vals)
                validate = res.action_validate_stock()

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': data
            }
        return {
            'code': 1000,
            'message': 'Refill Create Successfully',
        }
