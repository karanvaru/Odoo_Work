# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import logging
_logger = logging.getLogger(__name__)


class WebsitePreorderConfigSettings(models.Model):
    _name = 'website.preorder.config.settings'

    @api.model
    def default_template_id(self):
        ir_model_data = self.env['ir.model.data']
        return ir_model_data.get_object_reference('website_preorder', 'pre_order_email_template_edi_sale')[1]

    is_active = fields.Boolean(string="Active on website", readonly=False)
    name = fields.Char(string="Name", required=True, readonly=False, default="Pre Order")
    payment_type = fields.Selection([('complete', 'Complete Payment'), ('percent', 'Percent Payment')], string="Pre-order Payment Type", default="complete", required=True, readonly=False,
                                    help="Payment can be either full payment- customer need to pay full amount at the time of pre-order or percent payment- customer can pay percentage amount of the pre-order.")
    percentage = fields.Integer(string="Percent Payment For Pre-order", readonly=False)
    button_text = fields.Char(string="Add To Cart Button Text", required="True", readonly=False,
                              default="Pre-order", help="Customise the “Add to” button name for pre-order.")
    warning_message = fields.Text(
        string="Warning Message", readonly=False, help="Customised Warning message that will be displayed on your quotes.")
    custom_message = fields.Text(
        string="Custom Message", readonly=False, help="Customised message that will be displayed on pre-order product.")
    send_email = fields.Selection([('auto', 'Auto'), ('manual', 'Manual')], string="Send Email", default="auto", required=True, readonly=False,
                                  help="Notify the customer when product is back in stock, In that we also have two option First is Auto, mail will send automatic to notify the customer and other is Manual in which mail will send manually to notifiy the customer.")
    preorder_email_tempalte = fields.Many2one("mail.template", string="Pre-order Email Template", domain="[('model_id.model','=','sale.order')]", readonly=True, 
                                              default=default_template_id, help="Set to notify about the product availablity either through auto generated mails or through manually sent mails. ")
    pre_order_amount_visible = fields.Boolean(
        string='Pre-ordering Amount Visible on Website',readonly=False,  help="Enabled to display the pre-ordering amount in the order.")
    avaliable_date = fields.Boolean(string="Available Date Visible on Pre-order Product", readonly=False,
                                    help="Enabled to display avaibility date on the pre-product.")
    display_max_order_qty = fields.Boolean(string="Display Pre-ordered Quantity Range", readonly=False,
                                    help="Enabled to display the minimum and maximum pre-order quantity that can be ordered in one go.")
    minimum_qty = fields.Float(string="Allow preorder when quantity Less than or Equal", required="1", readonly=False, 
                               default="1", help="Set the minimum quantity of the product when it goes to the pre-order product.")
    max_order_qty = fields.Float(string="Pre-order Maximum Quantity", required="1", readonly=False,
                                 default="1", help="Set the maximum quantity of pre-order that can be ordered.")
    min_order_qty = fields.Float(string="Pre-order Minimum Quantity", required="1", readonly=False,
                                default="1", help="Set the minimum quantity of pre-order that can be ordered.")
    add_pre_order_msg = fields.Text(
        string="Pre-order conditional message", readonly=False, help="Customised message that will be displayed pre-order product with pertial payment add with normal product.")

    @api.model
    def create_wizard(self):
        wizard_id = self.env['website.message.wizard'].create(
            {'message': "Currently a Configuration Setting for Website Stock is active. You can not active other Configuration Setting. So, If you want to deactive the previous active configuration setting and active new configuration then click on 'Deactive Previous And Active New' button else click on 'cancel'."})
        return {
            'name': _("Message"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'website.message.wizard',
            'res_id': int(wizard_id.id),
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new'
        }

    @api.model
    def assign_preorder_to_user(self):
        preorder_group_id = self.env['ir.model.data'].get_object_reference(
            'website_preorder', 'website_preorder_group')[1]
        implied_group_id = self.env['ir.model.data'].get_object_reference(
            'base', 'group_user')[1]
        groups_obj = self.env["res.groups"].browse(preorder_group_id)
        implied_groups = self.env["res.groups"].browse(implied_group_id)
        implied_groups.sudo().write({'implied_ids': [(4, preorder_group_id)]})

    @api.model
    def remove_preorder_from_user(self):
        preorder_group_id = self.env['ir.model.data'].get_object_reference(
            'website_preorder', 'website_preorder_group')[1]
        implied_group_id = self.env['ir.model.data'].get_object_reference(
            'base', 'group_user')[1]
        groups_obj = self.env["res.groups"].browse(preorder_group_id)
        implied_groups = self.env["res.groups"].browse(implied_group_id)
        implied_groups.sudo().write({'implied_ids': [(3, preorder_group_id)]})
        groups_obj.sudo().write(
            {'users': [(3, user.id) for user in implied_groups.mapped('users')]})

    @api.multi
    def toggle_is_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        active_ids = self.search([('is_active', '=', True)])
        for record in self:
            if active_ids and record.id not in active_ids.ids:
                return self.create_wizard()
            record.is_active = not record.is_active

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('payment_type',False):
                if vals.get('payment_type') == 'percent':
                    if vals.get('percentage'):
                        if (vals.get('percentage') > 99 or vals.get('percentage') < 1):
                            raise UserError(
                                _("Percent value lies between 1 to 100"))
                    elif (rec.percentage > 99 or rec.percentage < 1):
                        raise UserError(
                            _("Percent value lies between 1 to 100"))
            elif vals.get('percentage',False) and rec.payment_type == 'percent' and (vals.get('percentage') > 99 or vals.get('percentage') < 1):
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
                elif rec.min_order_qty > vals.get("max_order_qty"):
                    raise UserError(
                        _("Minimum order quantity of a pre-order product must be less than maximum order quantity"))

            elif vals.get("min_order_qty") and vals.get("min_order_qty") > rec.max_order_qty:
                raise UserError(
                    _("Minimum order quantity of a pre-order product must be less than maximum order quantity"))
        res = super(WebsitePreorderConfigSettings, self).write(vals)

        active_ids = self.search([('is_active', '=', True)])
        for rec in self:
            if vals.get('is_active',False):
                rec.assign_preorder_to_user()
            elif len(active_ids) == 0:
                rec.remove_preorder_from_user()

        for current_rec in self:
            if current_rec.is_active:
                current_rec.set_product_value()
        return res

    @api.multi
    def set_product_value(self):
        product = self.env["product.template"].search([('is_preorder_type', '=', True), (
            'sale_ok', '=', True), ('wk_override_pre_order_default', '=', False)])
        for current_rec in self:
            product.write({'minimum_qty': current_rec.minimum_qty,
                           'max_order_qty': current_rec.max_order_qty,
                           'min_order_qty':current_rec.min_order_qty,
                           'payment_type': current_rec.payment_type,
                           'percentage': current_rec.percentage,
                           })

    @api.model
    def create(self, vals):
        if vals.get('is_active'):
            self.assign_preorder_to_user()
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
        if vals.get("min_order_qty",False) and vals.get("max_order_qty",False) and vals.get("min_order_qty") > vals.get("max_order_qty"):
            raise UserError(
                _("Minimum order quantity of a pre-order product must be less than maximum order quantity"))
        return super(WebsitePreorderConfigSettings, self).create(vals)

    @api.multi
    def unlink(self):
        current_rec = len(self.search([]))
        if current_rec == 1:
            raise UserError(_('You can not delete the last configuration.'))
        elif current_rec == len(self):
            raise UserError(
                _('You can not delete all website pre-order configuration.'))
        if len(self.filtered('is_active')) == 1:
            res = super(WebsitePreorderConfigSettings, self).unlink()
            self.remove_preorder_from_user()
            return res
        return super(WebsitePreorderConfigSettings, self).unlink()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        user_obj = super(WebsitePreorderConfigSettings,
                         self).copy(default=default)
        if self.is_active:
            user_obj.is_active = False
        return user_obj
