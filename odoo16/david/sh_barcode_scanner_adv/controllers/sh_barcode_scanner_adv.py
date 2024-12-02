# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError


class StockAdjustment(http.Controller):

    @http.route(['/sh_barcode_scanner/sh_barcode_scanner_get_widget_data'], type="json", auth="user", cors="*")
    def sh_barcode_scanner_get_widget_data(self, **post):
        values = {}
        user_is_stock_manager = request.env.user.has_group(
            'stock.group_stock_manager')
        user_has_stock_multi_locations = request.env.user.has_group(
            'stock.group_stock_multi_locations')
        values['user_is_stock_manager'] = user_is_stock_manager
        values['user_has_stock_multi_locations'] = user_has_stock_multi_locations
        values['sh_inven_adjt_barcode_scanner_auto_close_popup'] = request.env.company.sudo(
        ).sh_inven_adjt_barcode_scanner_auto_close_popup
        values['sh_inven_adjt_barcode_scanner_warn_sound'] = request.env.company.sudo(
        ).sh_inven_adjt_barcode_scanner_warn_sound

        if user_has_stock_multi_locations:
            domain = [('usage', 'in', ['internal', 'transit'])]
            locations = request.env['stock.location'].search_read(
                domain, ['id', 'display_name'])
            values['locations'] = locations
        return values

    @http.route(['/sh_barcode_scanner/sh_barcode_scanner_search_stock_quant_by_barcode'], type="json", auth="user", cors="*")
    def sh_barcode_scanner_search_stock_quant_by_barcode(self, **post):
        values = {}
        values['result'] = False
        barcode = post.get('barcode', False)
        location_id = post.get('location_id', False)
        location_name = post.get('location_name', False)
        scan_negative_stock = post.get('scan_negative_stock')

        if barcode not in ['', "", False, None]:
            is_multi_barcode = request.env.user.has_group(
                'sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')
            domain_quant = []
            domain_product = []
            if request.env.company.sudo().sh_inven_adjt_barcode_scanner_type == "barcode":
                domain_quant = [("product_id.barcode", "=", barcode)]
                domain_product = [("barcode", "=", barcode)]

                if is_multi_barcode:
                    domain_quant = ['|',
                                      ("product_id.barcode", "=", barcode),
                                      ("product_id.barcode_line_ids.name", "=", barcode)
                                      ]
                    domain_product = ['|',
                                      ("barcode", "=", barcode),
                                      ("barcode_line_ids.name", "=", barcode)
                                      ]
            elif request.env.company.sudo().sh_inven_adjt_barcode_scanner_type == "int_ref":
                domain_quant = [("product_id.default_code", "=", barcode)]
                domain_product = [("default_code", "=", barcode)]

            elif request.env.company.sudo().sh_inven_adjt_barcode_scanner_type == "sh_qr_code":
                domain_quant = [("product_id.sh_qr_code", "=", barcode)]
                domain_product = [("sh_qr_code", "=", barcode)]

            elif request.env.company.sudo().sh_inven_adjt_barcode_scanner_type == "all":
                domain_quant = ["|", "|",
                                  ("product_id.default_code", "=", barcode),
                                  ("product_id.barcode", "=", barcode),
                                  ("product_id.sh_qr_code", "=", barcode)
                                  ]
                domain_product = ["|", "|",
                                  ("default_code", "=", barcode),
                                  ("barcode", "=", barcode),
                                  ("sh_qr_code", "=", barcode)
                                  ]
                if is_multi_barcode:
                    domain_quant = ["|", "|", "|",
                                      ("product_id.default_code", "=", barcode),
                                      ("product_id.barcode", "=", barcode),
                                      ("product_id.sh_qr_code", "=", barcode),
                                      ("product_id.barcode_line_ids.name","=", barcode),
                                      ]
                    domain_product = ["|", "|", "|",
                                      ("default_code", "=", barcode),
                                      ("barcode", "=", barcode),
                                      ("sh_qr_code", "=", barcode),
                                      ("barcode_line_ids.name","=", barcode),
                                      ]

            domain = [
                ('location_id.usage', 'in', ['internal', 'transit']),
            ]
            if location_id:
                domain.append(('location_id', '=', location_id))

            domain = domain + domain_quant
            quant = request.env['stock.quant'].search(domain)

            if quant:
                # Take only one first quant if multiple quants found.
                quant = quant[0]
                if scan_negative_stock == True:
                    quant.inventory_quantity -= 1
                else:
                    quant.inventory_quantity += 1
                values['result'] = True
                values['message'] = "Product Added Successfully"

            elif request.env.company.sudo().sh_inven_adjt_barcode_scanner_create_new_quant:
    
                domain_product = [('company_id','in', (request.env.company.id, False))] + domain_product
                product = request.env['product.product'].search(domain_product,limit=1)

                if product:
                    if not location_id:
                        location_id = request.env['stock.location'].search([('company_id','=', request.env.company.id),('usage', 'in', ['internal', 'transit'])], limit=1).id

                    if scan_negative_stock == True:

                        quant = request.env['stock.quant'].with_company(request.env.company).create({
                                                                'product_id' : product.id,
                                                                'inventory_quantity' : -1,
                                                                'location_id' : location_id,
                                                                })
                        values['result'] = True
                        values['message'] = "Product Added Successfully"
                    else:
                        quant = request.env['stock.quant'].with_company(request.env.company).create({
                                                                'product_id' : product.id,
                                                                'inventory_quantity' : 1,
                                                                'location_id' : location_id,
                                                                })
                        values['result'] = True
                        values['message'] = "Product Added Successfully"

                else:
                    values['result'] = False
                    message = 'Product not found for this scanned barcode: ' + barcode
                    values['message'] = message
            else:
                values['result'] = False
                message = 'Record not found for this scanned barcode: ' + barcode
                if location_name:
                    message = 'Record not found for this scanned barcode: ' + \
                        barcode + ' and location: ' + location_name
                values['message'] = message
        else:
            values['result'] = False
            values['message'] = 'Please enter/type barcode in barcode input and try again.'
        return values

    @http.route(['/sh_barcode_scanner/sh_barcode_scanner_stock_quant_tree_btn_apply'], type="json", auth="user", cors="*")
    def sh_barcode_scanner_stock_quant_tree_btn_apply(self, **post):
        if not request.env.user.has_group('stock.group_stock_manager'):
            raise UserError(_('Only stock manager can do this action'))

        values = {}
        domain = [
            ('location_id.usage', 'in', ['internal', 'transit']),
            ('inventory_quantity_set', '!=', False),
        ]
        quants = request.env['stock.quant'].search(domain)
        if quants:
            for quant in quants:
                quant.action_apply_inventory()
            values['result'] = True
            values['message'] = 'All Counted Quantity successfully applied'

        else:
            values['result'] = False
            values['message'] = 'No any inventory line found for this action - Apply'
        return values
