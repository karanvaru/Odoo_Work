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

from odoo import api, models, fields, tools, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_default_order_type(self):
        ir_module_obj = self.env['ir.module.module']
        result = ir_module_obj.sudo().search([('name', 'in', ['website_stock']), ('state', 'in', ['installed'])])
        if result:
            stock_config_obj = self.env['website.stock.config.settings']
            active_ids = stock_config_obj.search(
                [('is_active', '=', True)], limit=1)
            if active_ids and not active_ids.wk_deny_order:
                return "allow"
        return "deny"

    wk_order_allow = fields.Selection([('allow', 'Allow Order'),
                                       ('deny', 'Deny Orders')
                                       ], 'When Product is out of Stock', default=get_default_order_type)

    wk_in_stock_msg = fields.Char(string='Message', translate=True, default="In Stock")
    wk_out_of_stock_msg = fields.Char(string='Message', translate=True, default='This product has gone out of Stock!')
    wk_override_default = fields.Boolean(string='Override Default Message')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def wk_get_product_vatiants(self):
        template_ids = self.mapped('product_variant_ids')
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('product.product_variant_action')
        list_view_id = imd.xmlid_to_res_id('product.product_product_tree_view')
        form_view_id = imd.xmlid_to_res_id('website_stock.Wk_website_stock_product')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(template_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % template_ids.ids
        elif len(template_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = template_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def get_config_settings_values(self):
        """ this function retrn all configuration value for website stock module."""
        res = {}
        stock_config_values = self.env['website.stock.config.settings'].sudo().search(
            [('is_active', '=', True)], limit=1)
        if stock_config_values:
            res = {
                'wk_display_qty': stock_config_values.wk_display_qty,
                'wk_in_stock_msg': stock_config_values.wk_in_stock_msg,
                'wk_out_of_stock_msg': stock_config_values.wk_out_of_stock_msg,
                'wk_stock_type': stock_config_values.wk_stock_type,
                'wk_warehouse_type': stock_config_values.wk_warehouse_type,
                'wk_stock_location': stock_config_values.wk_stock_location,
                'wk_warehouse_name': stock_config_values.wk_warehouse_name,
                'wk_extra_msg': stock_config_values.wk_extra_msg,
                'wk_minimum_qty': stock_config_values.wk_minimum_qty,
                'wk_custom_message': stock_config_values.wk_custom_message,
                'wk_deny_order': stock_config_values.wk_deny_order,
                'in_stock_color': stock_config_values.in_stock_color,
                'out_stock_color': stock_config_values.out_stock_color,
                'custome_stock_color': stock_config_values.custome_stock_color,
                'in_stock_text': stock_config_values.in_stock_text,
                'out_stock_text': stock_config_values.out_stock_text,
                'custom_stock_text': stock_config_values.custom_stock_text,
            }
        return res

    @api.model
    def stock_qty_validate(self, product_id):
        """ this is main function that is called by the controller this fuction mainlly use in stock validation."""
        quantity, copy_context = 0, self._context.copy() if self._context else {}
        if product_id:
            config_vals = self.get_config_settings_values()

            if config_vals.get('wk_warehouse_type') == 'specific':
                stock_location_id = config_vals.get('wk_stock_location')
                copy_context.update({'location': int(stock_location_id)})
            product_obj = self.with_context(copy_context).env['product.product'].sudo().browse(product_id)

            quantity = self.get_product_stock_qty(product_obj, config_vals.get('wk_stock_type'))
        return quantity

    @api.model
    def get_product_stock_qty(self, product_obj, type_stock):
        
        # CODE For Website Product Pack Compatibility
        product_obj = product_obj.product_tmpl_id if (hasattr(product_obj, 'is_pack') and product_obj.is_pack and hasattr(product_obj, 'product_tmpl_id')) else product_obj
        # CODE For Website Product Pack Compatibility
        
        if product_obj.type == 'service':
            return 10
        qty_hand, virtual, outgoing = product_obj.qty_available, product_obj.virtual_available, product_obj.outgoing_qty
        if type_stock == 'on_hand':
            return qty_hand
        elif type_stock == 'forecasted':
            return virtual
        else:
            return (qty_hand - outgoing)
 
    @api.model
    def cart_line_stock_validate(self, product_id=False, added_qty=0.0):
        if product_id and added_qty > 0.0:
            product_obj = self.env['product.product'].sudo().browse(int(product_id))
            if product_obj.type == 'service':
                return True
            quantity = self.stock_qty_validate(int(product_id))
            allowed = -1 if product_obj.wk_order_allow == 'deny' else 1
            if allowed == 1 or quantity >= added_qty:
                return True
        return False

    @api.model
    def shop_checkout_validate(self):
        order = self.sale_get_order()
        if order:
            order_lines = order.website_order_line
            for line in order_lines:
                vals = self.cart_line_stock_validate(int(line.product_id.id), float(line.product_uom_qty))
                if not vals:
                    break
            else:
                return True
        return False

    # this function called in main.py by the controllers
    @api.model
    def check_if_allowed(self,  product_id=False):
        if product_id:
            product_obj = self.env['product.product'].sudo().browse(product_id)
            if product_obj.type != 'service':
                check = product_obj.wk_order_allow
                if check == 'deny':
                    return -1
            return 1
        else:
            return 1

    @api.model
    def get_message_color(self, config={}):
        vals, i, result = ['#008A00', '#FF0000', '#FF6600'], 0, []
        for key1, key2 in zip(['in_stock_color', 'out_stock_color', 'custome_stock_color'], ['in_stock_text', 'out_stock_text', 'custom_stock_text']):
            result.append([])
            result[i].append(config[key1] if config.get(key1) else vals[i])
            result[i].append(config[key2] if config.get(key2) else '#FFFFFF')
            i+=1
        return result


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        """ set specfic warehouse in sale order when order is placed from website"""
        if self._context.get('website_id'):
            stock_config_vals = self.env['website'].get_config_settings_values()
            wk_warehouse_type = stock_config_vals.get('wk_warehouse_type')
            if wk_warehouse_type == 'specific':
                wk_warehouse_name = stock_config_vals.get('wk_warehouse_name')
                vals['warehouse_id'] = wk_warehouse_name.id
        return super(SaleOrder, self).create(vals)


# Responsible Developer:- Sunny Kumar Yadav #