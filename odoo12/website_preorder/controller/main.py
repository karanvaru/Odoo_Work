# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
from odoo import api, http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime

_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    @http.route(['/minimum/quantity/validation'], type='json', methods=['POST'], auth="public", website=True)
    def minimum_quantity_validation(self, product_id, set_value, **post):
        product = request.env['product.product'].browse(int(product_id))
        stock_value_qty = request.website.get_preorder_product_stock_qty(product)
        min_qty_order = request.website.sudo().get_preorder_min_qty(product)
        if set_value and set_value > stock_value_qty and set_value < min_qty_order:
            return True
        return False

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        sale_order_obj = request.registry.get('sale.order.line')
        present_qty = self.get_present_qty(product_id, line_id)
        product = request.env['product.product'].browse(int(product_id))
        get_quantity = request.website.stock_qty_validate(
            product_id=int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))
        stock_value = request.website.get_preorder_product_stock_qty(product)
        if add_qty:
            quantity = float(add_qty) + float(present_qty)
        elif set_qty:
            quantity = float(set_qty)
        else:
            quantity = 0.0

        if stock_value <=0 :
            total_preorder_qty = get_quantity
        else:
            total_preorder_qty = get_quantity + product.max_order_qty

        if request.env['website'].get_pre_order(product):
            if product.payment_type == 'percent':
                if get_quantity <= 0 and quantity > product.max_order_qty:
                    return super(WebsiteSale, self).cart_update_json(product_id, line_id, None, product.max_order_qty)
                elif quantity > get_quantity:
                    return super(WebsiteSale, self).cart_update_json(product_id, line_id, None,get_quantity)
            elif quantity > total_preorder_qty:
                return super(WebsiteSale, self).cart_update_json(product_id, line_id, None,total_preorder_qty)
        elif product.wk_order_allow == 'deny':
            if not request.env['website'].get_pre_order(product) and quantity > get_quantity:
                return super(WebsiteSale, self).cart_update_json(product_id, line_id, None,get_quantity)

        return super(WebsiteSale, self).cart_update_json(product_id, line_id, add_qty, set_qty)


    @http.route(['/shop/cart/order/check/msg'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json_check_msg(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        sale_order_obj = request.registry.get('sale.order.line')
        present_qty = self.get_present_qty(product_id, line_id)
        product = request.env['product.product'].browse(int(product_id))
        get_quantity = request.website.stock_qty_validate(
            product_id=int(product_id))
        allow_order = request.website.check_if_allowed(int(product_id))
        stock_value = request.website.get_preorder_product_stock_qty(product)
        if add_qty:
            quantity = float(add_qty) + float(present_qty)
        elif set_qty:
            quantity = float(set_qty)
        else:
            quantity = 0.0

        if stock_value <=0 :
            total_preorder_qty = get_quantity
        else:
            total_preorder_qty = get_quantity + product.max_order_qty

        if request.env['website'].get_pre_order(product):
            if product.payment_type == 'percent':
                if get_quantity <= 0 and quantity > product.max_order_qty:
                    return 'error message'
                elif quantity > get_quantity:
                    return 'error message'
            elif quantity > total_preorder_qty:
                return 'error message'
        elif product.wk_order_allow == 'deny':
            if not request.env['website'].get_pre_order(product) and quantity > get_quantity:
                return 'error message'

    @http.route(['/shop/cart/order/check'], type='json', auth="public", methods=['POST'], website=True)
    def check_preorder(self,**kw):
        product_id = kw.get('product_id',False)
        stock_value = kw.get('value',False)
        add_qty = kw.get('add_qty',False)
        product_obj = request.env["product.product"].browse(int(product_id))
        res = request.website.sale_get_order()
        if product_id:
            if res and res.order_line:
                for line in res.order_line:
                    if line.product_id.id == product_obj.id and request.env['website'].get_pre_order(product_obj):
                        total_qty = float(stock_value) - (int(line.product_uom_qty)+int(add_qty))
                        if product_obj.payment_type == 'percent':
                            if (float(stock_value) - int(line.product_uom_qty)) <=0 :
                                return True
                            else:
                                return False
                        elif total_qty < 0:
                                return True
            if request.env['website'].get_pre_order(product_obj):
                if product_obj.payment_type == 'percent':
                    if float(stock_value) <=0 :
                        return True
                elif int(add_qty) > float(stock_value):
                    return True
        return False

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
                    present_qty = sale_order_obj.browse(
                        [line.id]).product_uom_qty
                    break
            return present_qty

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        check = request.website.min_preorder_checkout_validate()
        if check:
            return super(WebsiteSale, self).checkout(**post)
        else:
            # request.redirect("/shop/cart")
            return False

    @http.route(['/shop/cart/order'], type='json', auth="public", methods=['POST'], website=True)
    def get_order_id(self, product_id, add_qty=None, set_qty=0, **kw):
        active_config = request.env['website'].get_preorder_config_settings_values(
        )

        res = request.website.sale_get_order()
        product = request.env['product.product'].browse(int(product_id))

        add_percent_msg = active_config.get('add_pre_order_msg') if active_config.get('add_pre_order_msg') else "You cannot place an order for a partial payment pre order product with other products, please empty your cart first to place your order for a partial payment pre order product"
        stock_value = request.website.get_preorder_product_stock_qty(product)
        total_preorder_qty = (stock_value + product.max_order_qty) if stock_value > 0 else product.max_order_qty

        if res and res.order_line:
            if res.preorder_payment_state == 'partial':
                return {'status': False, 'msg': _("Please Complete you current Order before proceeding to Further orders.")}
            if any(line.is_preorder and line.product_id.payment_type == 'percent' and line.product_id.id != product.id and request.website.get_preorder_product_stock_qty(line.product_id) <= 0 for line in res.order_line):
                return {'status': False, 'msg': _(add_percent_msg)}

            for line in res.order_line:
                if line.product_id.id == product.id:
                    total_qty = int(add_qty) + int(line.product_uom_qty)
                    if request.env['website'].get_pre_order(product):
                        if product.payment_type == 'percent':
                            if stock_value <= 0 and total_qty > product.max_order_qty:
                                return {'status': False, 'msg': _("You are Trying to add more than available quantity of the Product.")}
                            elif stock_value > 0 and total_qty > stock_value:
                                if int(line.product_uom_qty) < stock_value:
                                    return {'status': False, 'msg': _("You are Trying to add more than available quantity of the Product.")}
                                else:
                                    return {'status': False, 'msg': _(add_percent_msg)}
                        elif total_qty > total_preorder_qty:
                           return {'status': False, 'msg': _("You are Trying to add more than available quantity of the Product.")}
                    elif product.wk_order_allow == 'deny':
                        if not request.env['website'].get_pre_order(product) and total_qty > stock_value:
                            return {'status': False, 'msg': _("You are Trying to add more than available quantity of the Product.")}
                    return {'status': True, 'msg': "2"}
            if not any(line.product_id.id == product.id for line in res.order_line):
                if request.env['website'].get_pre_order(product):
                    if product.payment_type == 'percent':
                        if stock_value <= 0:
                            return {'status': False, 'msg': _(add_percent_msg)}
                        elif stock_value > 0 and add_qty > stock_value:
                            return {'status': False, 'msg': _("You are Trying to add more than available quantity of the Product.")}
                    elif add_qty > total_preorder_qty:
                        return {'status': False, 'msg': _("You are trying to add more than available quantity of the Product.")}
                elif product.wk_order_allow == 'deny':
                    if not request.env['website'].get_pre_order(product) and add_qty > stock_value:
                        return {'status': False, 'msg': _("You are trying to add more than available quantity of the Product.")}
        else:
            if request.env['website'].get_pre_order(product):
                if product.payment_type == 'percent':
                    if stock_value <= 0 and int(add_qty) > product.max_order_qty:
                        return {'status': False, 'msg': _("You are Trying to add more than available quantity of the Product.")}
                    elif stock_value > 0 and add_qty > stock_value:
                        return {'status': False, 'msg': _("You are Trying to add more than available quantity of the Product.")}
                elif add_qty > total_preorder_qty:
                    return {'status': False, 'msg': _("You are trying to add more than available quantity of the Product.")}
            elif product.wk_order_allow == 'deny':
                if not request.env['website'].get_pre_order(product) and add_qty > stock_value:
                    return {'status': False, 'msg': _("You are trying to add more than available quantity of the Product.")}
        return {'status': True, 'msg': ""}


    @http.route(['/shop/preorder/product'], type='json', auth="public", methods=['POST'], website=True)
    def get_preorder_product(self, product_id, **kw):
        product = request.env['product.product'].browse(int(product_id))
        return product.is_preorder_type

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        try:
            if add_qty:
                add_qty = float(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = float(set_qty)
        except ValueError:
            set_qty = 0
        partner = request.env['res.users'].browse(request.uid).partner_id
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id:
            last_order = partner.last_website_so_id
            sale_order_id = last_order and last_order.sudo().state == 'draft' and last_order.id
        if product_id and sale_order_id:
            sale_order = request.env['sale.order'].browse(sale_order_id)
            product = request.env['product.product'].browse(int(product_id))
            stock_value = request.website.get_preorder_product_stock_qty(product)
            total_preorder_qty = (stock_value + product.max_order_qty) if stock_value > 0 else product.max_order_qty
            product_in_order_line = [
                line.product_id.id for line in sale_order.sudo().order_line]
            if sale_order and sale_order.sudo().order_line:
                if sale_order.sudo().preorder_payment_state == 'partial':
                    return False
                if any(line.is_preorder and line.product_id.payment_type == 'percent' and line.product_id.id != product.id and request.website.get_preorder_product_stock_qty(line.product_id) <= 0 for line in sale_order.sudo().order_line):
                    return False
                for line in sale_order.sudo().order_line:
                    if line.product_id.id == product.id:
                        total_qty = int(add_qty) + int(line.product_uom_qty)
                        if request.env['website'].get_pre_order(product):
                            if product.payment_type == 'percent':
                                if stock_value <= 0 and total_qty > product.max_order_qty:
                                    return False
                                elif stock_value > 0 and total_qty > stock_value:
                                    return False
                            elif total_qty > total_preorder_qty:
                               return False
                        elif product.wk_order_allow == 'deny':
                            if not request.env['website'].get_pre_order(product) and total_qty > stock_value:
                                return False
                if not any(line.product_id.id == product.id for line in sale_order.sudo().order_line):
                    if request.env['website'].get_pre_order(product):
                        if product.payment_type == 'percent':
                            if stock_value <= 0:
                                return False
                return super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)
            else:
                return super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)
        else:
            return super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)

    @http.route(['/shop/redirect/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def redirect_cart(self, **post):
        order_id = int(post.get('preorder_id'))
        request.session['sale_order_id'] = order_id
        request.session['sale_last_order_id'] = order_id
        order = request.env['sale.order'].sudo().browse(order_id)
        order.state = 'draft'
        order.fully_paid = True
        for line in order.website_order_line:
            if line.product_id.is_preorder_type and not order.is_paid:
                line.price_unit = line.product_id.website_price - line.preorder_amount
        return request.redirect("/shop/payment")

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        res = super(WebsiteSale, self).payment_validate(
            transaction_id, sale_order_id, **post)
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order.is_preorder:
                for line in order.website_order_line:
                    if line.is_preorder and line.product_id.payment_type == 'percent':
                        if order.preorder_payment_state == 'draft':
                            order.preorder_payment_state = 'partial'
                        elif order.preorder_payment_state == 'partial':
                            line.price_unit = line.product_id.price or line.product_id.website_price
                            order.preorder_payment_state = 'complete'
                            order.is_paid = True

                if not any(line.is_preorder and line.product_id.payment_type == 'percent' for line in order.website_order_line):
                    order.preorder_payment_state = 'complete'

                    # if line.product_id.is_preorder_type and line.product_id.payment_type == 'complete':
                    #     order.is_paid = True
        return res

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        res = super(WebsiteSale, self).confirm_order(**post)
        sale_order_id = request.session.get('sale_order_id')
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        for line in order.website_order_line:
            if line.product_id.is_preorder_type and not order.is_paid and order.fully_paid:
                line.price_unit = line.product_id.website_price - line.preorder_amount
        return res
