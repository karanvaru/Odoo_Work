# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = 'product.template'

    @api.depends('pre_order_date')
    def expired_text_vissible(self):
        for record in self:
            if record.pre_order_date and record.pre_order_date >= datetime.today().date():
                record.visible = False
            else:
                record.visible = True

    @api.model
    def get_default_percentage_value(self):
        return self.env["website"].sudo().get_preorder_config_settings_values().get('percentage') or 1

    @api.model
    def get_default_max_order_qty(self):
        return self.env["website"].sudo().get_preorder_config_settings_values().get('max_order_qty') or 1

    @api.model
    def get_default_min_order_qty(self):
        return self.env["website"].sudo().get_preorder_config_settings_values().get('min_order_qty') or 1

    @api.model
    def get_default_minimum_qty(self):
        return self.env["website"].sudo().get_preorder_config_settings_values().get('minimum_qty') or 1

    is_preorder_type = fields.Boolean(string="Available for Pre-order",
                                      help="Enabled the field to display the product as pre-order once it is below the specified minimum quantity.")
    pre_order_date = fields.Date(
        string="Pre-order Date", help="Date untill which product will be available as pre-order product.")
    visible = fields.Boolean(compute=expired_text_vissible, readonly=True,
                             store=False, string="Exipred Text", default=True)
    payment_type = fields.Selection([('complete', 'Complete Payment'), ('percent', 'Percent Payment')], string="Pre-order Payment Type", default="complete", required=True,
                                    help="Payment can be either full payment- customer need to pay full amount at the time of pre-order or percent payment- customer can pay percentage amount of the pre-order.")
    percentage = fields.Integer(string="Percent Payment For Pre-order",
                                help="If 'payment Method Type' is 'Percent Payment' then set the percentage for percent Payment.", default=get_default_percentage_value)
    minimum_qty = fields.Float(string="Allow preorder when quantity Less than or Equal",
                               help="Set the minimum quantity of the product when it goes to the pre-order product.", default=get_default_minimum_qty)
    max_order_qty = fields.Float(string="Pre-order Maximum Quantity",
                                 help="Set maximum quantity will be pre-ordered.", default=get_default_max_order_qty)
    wk_override_pre_order_default = fields.Boolean(
        string="Override Default Pre-order Configuration", help="Set the maximum quantity of pre-order that can be ordered.")
    min_order_qty = fields.Float(string="Pre-order Minimum Quantity",
                                 help="Set minimum quantity will be pre-ordered.", default=get_default_min_order_qty)

    @api.multi
    def write(self, vals):
        default_config = self.env["website"].sudo(
        ).get_preorder_config_settings_values()
        for res in self:
            if vals.get('is_preorder_type') or (not vals.get('is_preorder_type') and res.is_preorder_type):
                if (not vals.get('wk_override_pre_order_default',True)) or (not vals.get('wk_override_pre_order_default') and not res.wk_override_pre_order_default):
                    vals.update({
                        'minimum_qty': default_config.get('minimum_qty') or 1,
                        'max_order_qty': default_config.get('max_order_qty') or 1,
                        'min_order_qty' : default_config.get('min_order_qty') or 1,
                        'payment_type': default_config.get('payment_type') or 'complete',
                        'percentage': default_config.get('percentage') or 1,
                    })
            if vals.get('payment_type'):
                if vals.get('payment_type') == 'percent':
                    if vals.get('percentage',False):
                        if (vals.get('percentage') > 99 or vals.get('percentage') < 1):
                            raise UserError(
                                _("Percent value lies between 1 to 100"))
                    elif (res.percentage > 99 or res.percentage < 1):
                        raise UserError(
                            _("Percent value lies between 1 to 100"))
            elif res.payment_type == 'percent' and vals.get('percentage',False) and (vals.get('percentage') > 99 or vals.get('percentage') < 1):
                raise UserError(_("Percent value lies between 1 to 100"))

            if vals.get("minimum_qty",False) and vals.get("minimum_qty") < 0:
                raise UserError(
                    _("Please enter a positive stock value for pre order condition"))

            if vals.get("min_order_qty",False) and vals.get("min_order_qty") < 1:
                raise UserError(
                    _("Minimum order quantity of a pre-order product must be greater than zero"))

            if vals.get("max_order_qty",False) and vals.get("max_order_qty") < 1:
                raise UserError(
                    _("Maximum order quantity of a pre-order product must be greater than zero"))

            if vals.get("max_order_qty"):
                if vals.get("min_order_qty"):
                    if vals.get("min_order_qty") > vals.get("max_order_qty"):
                        raise UserError(
                            _("Minimum order quantity of a pre-order product must be less than maximum order quantity"))
                elif res.min_order_qty > vals.get("max_order_qty"):
                    raise UserError(
                        _("Minimum order quantity of a pre-order product must be less than maximum order quantity"))

            elif vals.get("min_order_qty") and vals.get("min_order_qty") > res.max_order_qty:
                raise UserError(
                    _("Minimum order quantity of a pre-order product must be less than maximum order quantity"))

        return super(product_template, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get("wk_override_pre_order_default"):
            if vals.get('payment_type',False) and vals.get('payment_type') == 'percent' and (vals.get('percentage') > 99 or vals.get('percentage') < 1):
                raise UserError(_("Percent value lies between 1 to 100"))
            if vals.get("minimum_qty",False) and vals.get("minimum_qty") < 0:
                raise UserError(
                    _("Please enter a positive stock value for pre order condition"))
            if vals.get("max_order_qty",False) and vals.get("max_order_qty") < 1:
                raise UserError(
                    _("Maximum order quantity of a pre-order product must be greater than zero"))
            if vals.get("min_order_qty",False) and vals.get("min_order_qty") < 1:
                raise UserError(
                    _("Minimum order quantity of a pre-order product must be greater than zero"))
            if vals.get("min_order_qty",False) and vals.get("max_order_qty") and vals.get("min_order_qty") > vals.get("max_order_qty"):
                raise UserError(
                    _("Minimum order quantity of a pre-order product must be less than maximum order quantity"))
        return super(product_template, self).create(vals)

    @api.onchange('is_preorder_type', 'wk_override_pre_order_default')
    def onchange_is_perorder_product(self):
        if self.is_preorder_type and not self.wk_override_pre_order_default:
            self.max_order_qty = self.env["website"].sudo(
            ).get_preorder_config_settings_values().get('max_order_qty')
            self.min_order_qty = self.env["website"].sudo(
            ).get_preorder_config_settings_values().get('min_order_qty')
            self.minimum_qty = self.env["website"].sudo(
            ).get_preorder_config_settings_values().get('minimum_qty')
            self.payment_type = self.env["website"].sudo(
            ).get_preorder_config_settings_values().get('payment_type')
            self.percentage = self.env["website"].sudo(
            ).get_preorder_config_settings_values().get('percentage')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.is_preorder')
    def _get_preorder_order(self):
        for order in self:
            if any(line.is_preorder for line in order.order_line):
                order.is_preorder = True
            else:
                order.is_preorder = False

    @api.depends('order_line.preorder_notify')
    def set_sale_order_preorder_notify(self):
        for order in self:
            if any(line.is_preorder and not line.preorder_notify for line in order.order_line):
                order.preorder_notify = False
            else:
                order.preorder_notify = True

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = preorder_amount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                preorder_amount += line.preorder_amount
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'preorder_amount': order.pricelist_id.currency_id.round(preorder_amount)
            })

    @api.depends("order_line.product_id")
    def _total_order_line_all(self):
        """
        Compute full amount of the Pre-order.
        """
        for order in self:
            amount = 0.0
            for line in order.order_line:
                if line.product_id.price:
                    amount += line.product_id.price * line.product_uom_qty
                else:
                    amount += line.product_id.list_price * line.product_uom_qty
            order.update({
                'full_amount': amount,
            })

    full_amount = fields.Monetary(string='Pre-Order Amount', store=True,
                                  readonly=True, compute='_total_order_line_all', track_visibility='always')
    is_paid = fields.Boolean(string="Order Fully Paid", default=False)
    is_preorder = fields.Boolean(
        string="Pre-Order", compute=_get_preorder_order, store=True, readonly=True, default=False)
    preorder_amount = fields.Monetary(
        string='Pre-Order Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    fully_paid = fields.Boolean(string="Paid")
    preorder_payment_state = fields.Selection([
        ('draft','Draft'),
        ('partial','Partial'),
        ('complete','Complete'),
    ],default="draft",string="Preorder Payment Status")
    preorder_notify = fields.Boolean(string="Pre-Order Notification", compute=set_sale_order_preorder_notify, store=True, readonly=True, default=False)


    @api.multi
    def action_confirm(self):
        for order in self:
            if order.preorder_payment_state == 'partial':
                raise UserError(_("You cannot confirm this sale order as it contains a partial pre order product whose complete payment is not done."))
        return super(SaleOrder,self).action_confirm

    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        res = super(SaleOrder, self)._website_product_id_change(
            order_id, product_id, qty)
        order = self.env['sale.order'].browse(order_id)
        product_obj = self.env['product.product'].browse(product_id)

        stock_value = self.env['website'].get_preorder_product_stock_qty(product_obj)
        if self.env['website'].get_pre_order(product_obj):
            price_unit = self.get_preorder_product_price(
                product_obj, res['price_unit'])
            res['price_unit'] = price_unit
            if res.get('product_uom_qty') > stock_value:
                res['preorder_amount'] = price_unit
                res['pre_order_qty'] = (res.get('product_uom_qty') - stock_value) if stock_value > 0 else res.get('product_uom_qty')
                res['is_preorder'] = True
            else:
                res['is_preorder'] = False
                res['pre_order_qty'] = 0
        return res

    @api.model
    def get_preorder_config_settings_values(self):
        """ this function retrn all configuration value for website stock module."""
        preorder_config_values = self.env['website.preorder.config.settings'].search([
                                                                                     ('is_active', '=', True)])
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
        }
        return res

    @api.multi
    def get_preorder_product_price(self, product, price_unit):
        stock_value = self.env['website'].get_preorder_product_stock_qty(product)
        if product.is_preorder_type:
            res = self.env['website'].get_public_user()
            if not self.env['website'].get_public_user():
                return price_unit
            if product.payment_type == 'percent' and stock_value <= 0:
                percentage = product.percentage
                return (price_unit * percentage / 100)
            else:
                return price_unit

    @api.multi
    def stock_qty_validate(self):
        """ this is main function that is called by the controller this fuction mainlly use in stock validation."""
        self.ensure_one()
        quantity = 0
        required = 0
        for line in self.website_order_line.sudo():
            if line.product_id:
                stock_value = self.env['website'].get_preorder_product_stock_qty(line.product_id)
                if line.is_preorder and line.product_id.payment_type == 'percent' and stock_value > 0:
                    return True
        return False

    @api.multi
    def config_setting(self):
        return self.get_preorder_config_settings_values().get('pre_order_amount_visible')

    @api.multi
    def send_notification_of_preorder(self):
        for rec in self:
            context = dict(rec._context) or {}
            context['active_id'] = rec.id
            return {
                'name':'Pre-Order Notification',
                'type':'ir.actions.act_window',
                'res_model':'preorder.notification.wizard',
                'view_mode':'form',
                'view_type':'form',
                'view_id':rec.env.ref('website_preorder.preorder_line_notify_wizard_form_view').id,
                'context' : context,
                'target':'new',
            }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def get_product_available_qty(self):
        for line in self:
            line.available_product_qty = line.product_id.qty_available

    preorder_amount = fields.Float(
        'Pre-Order Amount', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    is_preorder = fields.Boolean(string="Pre-Order")
    pre_order_qty = fields.Float(string="Pre-Order Quantity")
    preorder_notify = fields.Boolean(string="Pre-Order Notification", track_visibility='always')
    available_product_qty = fields.Float(string="Available Quantity",compute=get_product_available_qty)


    @api.multi
    def _get_display_price(self, product):
        if self.env['website'].get_pre_order(product):
            return self.order_id.get_preorder_product_price(product, product.price)
        else:
            return super(SaleOrderLine, self)._get_display_price(product)
