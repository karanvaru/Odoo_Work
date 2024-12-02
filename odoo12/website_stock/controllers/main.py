# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import http, tools, api, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @api.model
    def get_present_qty(self, product_id, line_id=None):
        sale_order_obj = request.env['sale.order.line'].sudo()
        if line_id:
            present_qty = sale_order_obj.browse([line_id]).product_uom_qty
            return present_qty
        else:
            present_qty = 0
            order = request.website.sale_get_order()
            if order:
                order_lines = order.website_order_line
            else:
                order_lines = []
            for line in order_lines:
                line_product = sale_order_obj.browse([line.id]).product_id
                if line_product.id == int(product_id):
                    present_qty = sale_order_obj.browse([line.id]).product_uom_qty
                    break
            return present_qty

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        if float(add_qty) == 0:
            add_qty = '1'
        allow_order = request.website.check_if_allowed(int(product_id))
        if allow_order == 1:
            res = super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)
            return res

        else:
            get_quantity = request.website.sudo().stock_qty_validate(
                product_id=int(product_id))
            present_qty = self.get_present_qty(product_id)
            temp = float(present_qty) + float(add_qty)
            if float(get_quantity) >= temp:
                return super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        sale_order_obj = request.registry.get('sale.order.line')
        present_qty = self.get_present_qty(product_id, line_id)
        get_quantity = request.website.stock_qty_validate(
            product_id=int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))
        if add_qty:
            quantity = float(add_qty) + float(present_qty)
        elif set_qty:
            quantity = float(set_qty)
        else:
            quantity = 0.0

        if allow_order == 1:
            return super(WebsiteSale, self).cart_update_json(product_id, line_id, add_qty, set_qty)

        elif get_quantity >= quantity:
            return super(WebsiteSale, self).cart_update_json(product_id, line_id, add_qty, set_qty)

        return super(WebsiteSale, self).cart_update_json(product_id, line_id, None, present_qty)

    @http.route(['/shop/cart/update_json/msg'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json_msg(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        sale_order_obj = request.registry.get('sale.order.line')
        present_qty = self.get_present_qty(product_id, line_id)
        get_quantity = request.website.stock_qty_validate(
            product_id=int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))
        if add_qty:
            quantity = float(add_qty) + float(present_qty)
        elif set_qty:
            quantity = float(set_qty)
        else:
            quantity = 0.0
        if allow_order == -1:
            if get_quantity < quantity:
                return 'error message'

    @http.route(['/shop/cart/update/msg'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_msg(self, product_id, add_qty=1, set_qty=0, **kw):
        result = {'status': 'allow'}
        if float(add_qty) == 0.0:
            add_qty = '1'
        allow_order = request.website.check_if_allowed(int(product_id))
        if allow_order == -1:
            get_quantity = request.website.stock_qty_validate(
                product_id=int(product_id))
            present_qty = self.get_present_qty(product_id)
            temp = float(present_qty) + float(add_qty)
            if float(get_quantity) < temp:
                result['present_qty'] = present_qty
                result['get_quantity'] = get_quantity
                result['remain_qty'] = (get_quantity - present_qty)
                result['status'] = 'deny'
        return result

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        check = request.website.shop_checkout_validate()
        if not check:
            return request.redirect("/shop/cart")
        return super(WebsiteSale, self).checkout(**post)

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        check = request.website.shop_checkout_validate()
        if not check:
            return request.redirect("/shop/cart")
        return super(WebsiteSale, self).payment(**post)

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        config_setting = request.website.get_config_settings_values()
        
        if config_setting.get('wk_warehouse_type') == 'specific':
            stock_location_id = config_setting.get('wk_stock_location')
            request.context = dict(request.context, location=int(stock_location_id))

        return super(WebsiteSale, self).shop(page, category, search, ppg, **post)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        config_setting = request.website.get_config_settings_values()

        if config_setting.get('wk_warehouse_type') == 'specific':
            stock_location_id = config_setting.get('wk_stock_location')
            request.context = dict(request.context, location=int(stock_location_id))

        return super(WebsiteSale, self).product(product, category, search, **kwargs)

# Responsible Developer:- Sunny Kumar Yadav #