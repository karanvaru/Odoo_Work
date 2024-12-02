from odoo import http, _, fields
from odoo.http import request


class RefillRequest(http.Controller):
    # Refill Request Create
    @http.route('/web/refill/request/create', type='json', auth="user")
    def refill_request(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        refill_id = request.env['refill.request'].sudo().search([])
        try:
            product_id = int(kw.get('product_id', False))
            date = kw.get('date', False)

            refill_line = []
            if not product_id:
                return {
                    'code': 200,
                    'message': 'Please add Product!',
                    'data': []
                }
            for rec in kw.get('refill_parts_lines', []):
                vals = {
                    'product_part_id': rec['product_part_id'],
                    'quantity': rec['qty'],
                    'comments': rec['note'],
                }
                refill_line.append((0, 0, vals))
            res = refill_id.sudo().create({
                'product_id': product_id,
                'date': date,
                'refill_ids': refill_line,
            })
        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }
        return {
            'code': 1000,
            'message': 'Refill Request Create Completed',
            'data': {
                'id': res.id,
            }
        }

    @http.route('/web/refill/request/list', type='json', auth="user")
    def refill_request_list(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if limit <= 1:
                limit = 10
            refill_id = request.env['refill.request'].sudo().search([], limit=limit, offset=start)
            refill_length = request.env['refill.request'].search_count([])
            if not refill_id:
                return {
                    'code': 200,
                    'message': 'There is no any Refill Request',
                    'data': []
                }
            data = []
            for rec in refill_id:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'date': rec.date,
                    'user_id': {
                        'id': rec.user_id.id,
                        'name': rec.user_id.display_name,
                    },
                    'company_id': {
                        'id': rec.company_id.id,
                        'name': rec.company_id.display_name,
                    },
                    'product_id': {
                        'id': rec.product_id.id,
                        'name': rec.product_id.display_name,
                    },
                    'ticket_id': {
                        'id': rec.ticket_id.id,
                        'name': rec.ticket_id.display_name,
                    },
                    'stage_id': {
                        'name': rec.state,
                    }
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
            'message': 'Refill Request List Found Successfully.',
            'data': data,
            'records': refill_length

        }

    @http.route('/web/refill/request/detail', type='json', auth="user")
    def refill_request_detail(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            refill_request_id = int(kw.get('refill_request_id', False))
            domain = [('id', '=', refill_request_id)]
            request_id = request.env['refill.request'].sudo().search(domain)
            product_parts = []

            if not request_id:
                return {
                    'code': 100,
                    'message': 'There is no any Product Register',
                    'data': [],
                }

            for i in request_id.refill_ids:
                val_line = {
                    'id': i.id,
                    'product_part_id': i.product_part_id.id,
                    'product_name': i.product_part_id.display_name,
                    'qty': i.quantity,
                    'note': i.comments or ""
                }
                product_parts.append(val_line)

            vals = {
                'id': request_id.id,
                'name': request_id.name,
                'date': request_id.date,
                'user_id': {
                    'id': request_id.user_id.id,
                    'name': request_id.user_id.display_name,
                },
                'company_id': {
                    'id': request_id.company_id.id,
                    'name': request_id.company_id.display_name,
                },
                'product_id': {
                    'id': request_id.product_id.id,
                    'name': request_id.product_id.display_name,
                },
                'ticket_id': {
                    'id': request_id.ticket_id.id,
                    'name': request_id.ticket_id.display_name,
                },
                'stage_id': {
                    'name': request_id.state,
                },
                'refill_parts_lines': product_parts

            }

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                # 'data': [],
                # 'line_lis': []
            }

        return {
            'code': 1000,
            'message': 'Refill Request Detail Found Successfully.',
            'data': vals,
            # 'records': register_length
        }

    @http.route('/web/refill/request/approve', type='json', auth="user")
    def refill_request_verification(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            refill_request_id = int(kw.get('refill_request_id', False))
            domain = [('id', '=', refill_request_id)]
            request_id = request.env['refill.request'].sudo().search(domain)

            if not request_id:
                return {
                    'code': 100,
                    'message': 'There is no any Refill Request',
                    'data': [],
                }

            for i in request_id:
                i.action_confirm

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                # 'data': [],
                # 'line_lis': []
            }

        return {
            'code': 1000,
            'message': 'Refill Request Approve Successfully.',
            # 'data': ,
            # 'records': register_length
        }

    @http.route('/web/refill/request/edit', type='json', auth="user")
    def refill_request_edit(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            refill_id = int(kw.get('refill_id', False))
            date = kw.get('date', False)
            new_id = request.env['refill.request'].browse(refill_id)

            if not refill_id:
                return {
                    'code': 200,
                    'message': 'Refill Request not Found!',
                    'data': []
                }

            for rec in kw.get('refill_parts_lines', []):
                new_line_id = request.env['refill.request.line'].browse(int(rec['id']))
                new_line_id.update({
                    'product_part_id': rec['product_part_id'],
                    'quantity': rec['qty'],
                    'comments': rec['note'],
                })

            new_id.update({
                'date': date,
            })

        except Exception as e:
            return {
                'code': 1001,
                'message': e,
                'data': []
            }

        return {
            'code': 1000,
            'message': 'Refill Request Edited Successfully',
        }

    @http.route('/web/cartridge/validation', type='json', auth="user")
    def cartridge_validation(self, **kw):
        uid = request.session.uid
        if not uid:
            return {
                'code': 100,
                'message': 'Session Expired!',
                'data': []
            }
        try:
            prefix = 'C-'
            if prefix not in kw.get('default_code', False):
                default_code = prefix + kw.get('default_code', False)
            else:
                default_code = kw.get('default_code', False)

            url_params = request.httprequest.args.to_dict()
            start = int(url_params.get('start', 0))
            end = int(url_params.get('end', 0))
            limit = end + 1 - start
            if limit <= 1:
                limit = 10
            # domain = [('categ_id.type', '=', 'cartridge'), ('default_code', '=', default_code)]
            if not default_code:
                return {
                    'code': 200,
                    'message': 'Product Not Found!!',
                    'data': []
                }

            domain1 = [('default_code', '=', default_code), ('category_type', '=', 'cartridge')]
            pro_parts_id = request.env['product.product'].sudo().search(domain1, limit=limit, offset=start,
                                                                        order='write_date desc')
            if not pro_parts_id:
                return {
                    'code': 200,
                    'message': 'Cartridge Not Found!!',
                    'data': []
                }
            product_part = []
            for i in pro_parts_id.part_product_line_ids:
                val_line = {
                    'product_part_id': i.product_part_id.id,
                    'product_name': i.product_part_id.display_name,
                    'qty': i.product_qty,
                    'note': i.note or ""
                }
                product_part.append(val_line)

            data = []
            if not pro_parts_id:
                return {
                    'code': 1001,
                    'message': '!!! Product not Found !!!',
                    'data': [],
                }
            for recs in pro_parts_id:
                vals = {
                    'id': recs.id,
                    'name': recs.display_name,
                    'default_code': recs.default_code,
                    'categ_id': recs.categ_id.id,
                    'part_product_line_ids': product_part,
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
            'message': 'Cartridge Found Successfully!',
            'data': data,
            # 'records': pro_parts_length
        }