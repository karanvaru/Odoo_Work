# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, tools, _
from odoo import models
from odoo.http import request
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        test = super(Website,self).sale_get_order(force_create, code, update_pricelist, force_pricelist)
        return test

    @api.model
    def get_preorder_config_settings_values(self):
        """ this function retrn all configuration value for website Preorder module."""
        irmodule_obj = self.env['ir.module.module']
        result = irmodule_obj.sudo().search(
            [('name', 'in', ['website_preorder']), ('state', 'in', ['installed'])])
        res = {}
        if result:
            preorder_config_values = self.env['website.preorder.config.settings'].sudo(
            ).search([('is_active', '=', True)], limit=1)
            if preorder_config_values:
                res = {
                    'payment_type': preorder_config_values.payment_type,
                    'percentage': preorder_config_values.percentage,
                    'button_text': preorder_config_values.button_text,
                    'warning_message': preorder_config_values.warning_message,
                    'custom_message': preorder_config_values.custom_message,
                    'send_email': preorder_config_values.send_email,
                    'preorder_email_tempalte': preorder_config_values.preorder_email_tempalte,
                    'pre_order_amount_visible': preorder_config_values.pre_order_amount_visible,
                    'avaliable_date': preorder_config_values.avaliable_date,
                    'max_order_qty': preorder_config_values.max_order_qty,
                    'min_order_qty': preorder_config_values.min_order_qty,
                    'minimum_qty': preorder_config_values.minimum_qty,
                    'display_max_order_qty': preorder_config_values.display_max_order_qty,
                    'add_pre_order_msg' : preorder_config_values.add_pre_order_msg
                }
        return res


    @api.model
    def get_product_stock_qty(self, product_obj, type_stock):
        quantity = super(Website, self).get_product_stock_qty(
            product_obj, type_stock)
        if product_obj and product_obj.type != 'service':
            if self.get_pre_order(product_obj) and product_obj.minimum_qty:
                quantity = quantity - product_obj.minimum_qty
        return quantity

    @api.model
    def get_preorder_product_stock_qty(self,product_obj):
        stock_config_vals = self.get_config_settings_values()
        stock_type = stock_config_vals.get('wk_stock_type','on_hand')
        stock_value = self.get_product_stock_qty(product_obj.sudo(),stock_type)
        return stock_value

    @api.model
    def get_pre_order_stock_qty(self,product_obj):
        stock_value = self.get_preorder_product_stock_qty(product_obj)
        return str(stock_value)

    @api.multi
    def check_if_allowed(self, product_id=False):
        if product_id:
            product_obj = self.env['product.product'].browse(product_id)
            stock_value = self.get_preorder_product_stock_qty(product_obj)
            if product_obj and self.get_pre_order(product_obj):
                return 1
            else:
                return super(Website, self).check_if_allowed(product_id)

    @api.model
    def stock_qty_validate(self, product_id):
        """ this is main function that is called by the controller this fuction mainlly use in stock validation."""
        quantity = 0
        if product_id:
            product_obj = self.env['product.product'].sudo().browse(product_id)
            stock_value = self.get_preorder_product_stock_qty(product_obj)
            if self.get_pre_order(product_obj) and stock_value<=0 :
                return product_obj.max_order_qty
            else:
                res = super(Website, self).stock_qty_validate(product_id)
                return res

    @api.model
    def cart_line_stock_validate(self, product_id=False, added_qty=0.0):
        if product_id and added_qty > 0.0:
            product_obj = self.env['product.product'].sudo().browse(product_id)
            if product_obj.type == 'service':
                return True
            if product_obj.is_preorder_type:
                return True
            quantity = self.stock_qty_validate(product_obj.id)
            allowed = -1 if product_obj.wk_order_allow == 'deny' else 1
            if allowed == 1 or quantity >= added_qty:
                return True
        return False

    @api.model
    def min_preorder_checkout_validate(self):
        order = self.sale_get_order()
        if order:
            order_lines = order.website_order_line
            for line in order_lines:
                stock_value = self.get_preorder_product_stock_qty(line.product_id)
                vals2 = False if self.get_pre_order(line.product_id) and line.product_uom_qty > stock_value and line.product_uom_qty < self.get_preorder_min_qty(line.product_id) else True
                if not vals2:
                    break
            else:
                return True
        return False

    @api.model
    def get_preorder_button_text(self):
        button_text = 'Pre-order'
        res = self.get_preorder_config_settings_values()
        if res:
            button_text = res.get('button_text')
        return button_text

    @api.model
    def get_preorder_min_qty(self, product_obj):
        stock_value = self.get_preorder_product_stock_qty(product_obj)
        return (stock_value + product_obj.min_order_qty) if stock_value > 0 else product_obj.min_order_qty

    @api.model
    def get_pre_order(self, product):
        res = self.get_preorder_config_settings_values()
        if res and product.is_preorder_type and product.pre_order_date >= datetime.today().date():
            return True
        return False

    @api.model
    def get_product_preorder_type(self, product):
        order = self.sale_get_order()
        stock_value = self.get_preorder_product_stock_qty(product)
        if order:
            for line in order.order_line:
                if line.product_id.id == product.id and self.get_pre_order(product):
                    total_qty = float(stock_value) - int(line.product_uom_qty)
                    if total_qty <= 0:
                        return True
        if self.get_pre_order(product) and stock_value <= 0:
            return True
        return False

    @api.model
    def get_public_user(self):
        ir_model_data = self.env['ir.model.data']
        public_user = ir_model_data.get_object_reference(
            'base', 'public_user')[1]
        if public_user == request.uid:
            return False
        return True

    @api.model
    def get_preorder_product_price_message(self, product, config_setting=False):
        if self.get_pre_order(product):
            if product.is_preorder_type:
                payment_type = product.payment_type
                if not self.get_public_user():
                    return False
                if payment_type == 'percent':
                    percentage = product.percentage
                    return (product.price * percentage / 100)
        return False

    @api.model
    def get_custom_message(self, product, config_setting=False):
        if self.get_pre_order(product):
            return self.get_preorder_config_settings_values().get('custom_message')
        return False

    @api.model
    def get_warning_message(self, config_setting=False):
        return self.get_preorder_config_settings_values().get('warning_message') or False

    @api.model
    def get_avaliable_date(self, product):
        if self.get_pre_order(product):
            if self.get_preorder_config_settings_values().get('avaliable_date'):
                if product.pre_order_date and product.pre_order_date >= datetime.today().date():
                    return product.pre_order_date
        return False

    @api.model
    def get_maximum_order_quantity_message(self, product):
        if self.get_pre_order(product):
            if self.get_preorder_config_settings_values().get('display_max_order_qty'):
                return True
        return False
