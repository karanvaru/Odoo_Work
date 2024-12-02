from odoo import http, _, fields
from odoo.http import request


class ContractList(http.Controller):

    @http.route('/web/list/contract', type='json', auth="user")
    def contract_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        res = request.env['res.users'].browse(uid)
        if not res.partner_id:
            return {
                'code': 200,
                'message': 'There is no contract',
                'data': []
            }
        try:
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            # base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit < 1:
                limit = 10
            contract_ls = False

            if request.env.user.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                contract_ls = request.env['contract.contract'].sudo().search([('state', '=', 'active'), '|', '|',
                                                                              ('partner_id', '=',
                                                                               res.partner_id.parent_id.id),
                                                                              ('partner_id', '=', res.partner_id.id),
                                                                              ('partner_id', 'child_of',
                                                                               res.partner_id.parent_id.id)],
                                                                             limit=limit, offset=start)
                contract_length = request.env['contract.contract'].search_count([])
            elif request.env.user.has_group('ki_contract_menu.group_smart_printer_admin') or request.env.user.has_group(
                    'ki_contract_menu.group_smart_printer_administrator'):
                contract_ls = request.env['contract.contract'].search([], limit=limit, offset=start)
                contract_length = request.env['contract.contract'].search_count([])

            if not contract_ls:
                return {
                    'code': 100,
                    'message': 'Product Not Found!',
                    'data': []
                }
            data = []
            for rec in contract_ls:
                for i in rec.contract_line_fixed_ids:
                    vals = {
                        'id': rec.id,
                        'date_start': rec.date_start,
                        'barcode': i.product_id.barcode,
                        # 'image_url': base_url + '/web/image/product.product/%s/image_1920' % rec.id,
                        # 'partner_id': {
                        #     'id': rec.partner_id.id,
                        #     'name': rec.partner_id.name,
                        # },
                        # 'partner_shipping_id': {
                        #     'id': rec.partner_shipping_id.id,
                        #     'name': rec.partner_shipping_id.name,
                        # },
                        # 'product_id': {
                        #     'id': rec.contract_line_fixed_ids.product_id.id,
                        #     'name': rec.contract_line_fixed_ids.product_id.name,
                        #     'default_code': rec.contract_line_fixed_ids.product_id.default_code,
                        # },
                        # 'categ_id': {
                        #     'id': rec.contract_line_fixed_ids.categ_id.id,
                        #     'name': rec.contract_line_fixed_ids.categ_id.name,
                        # }

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
            'message': 'Contracts Found Successfully!',
            'data': data,
            'records': contract_length
        }
