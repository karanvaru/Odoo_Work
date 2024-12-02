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

from odoo import api, fields, models, _


class WebsiteStockConfigSettings(models.Model):
    _name = 'website.stock.config.settings'
    _description = "Website Stock Config Settings"

    is_active = fields.Boolean(string="Active on website")
    name = fields.Char(string="Name", required=True)
    wk_display_qty = fields.Boolean(string="Display Quantity on Product Page", default=False)

    wk_in_stock_msg = fields.Char(string="In Stock Message", translate=True, help="""Out of Stock Message.""", default='In Stock!!!')
    in_stock_color = fields.Char(string="In stock message color", size=7,  help="Enter Hexa Decimal Value of Color", default="#008A00")
    in_stock_text = fields.Char(string="Text color", size=7, default="#FFFFFF")

    wk_out_of_stock_msg = fields.Char(string="Out of Stock Message", translate=True, help="""Out of Stock Message.""", default="Out of Stock!!!")

    out_stock_color = fields.Char(string="Out of stock message color", size=7,  help="Enter Hexa Decimal Value of Color", default="#FF0000")
    out_stock_text = fields.Char(string="Text color", size=7, default="#FFFFFF")

    wk_stock_type = fields.Selection([('on_hand', 'Quantity on Hand'), ('forecasted', 'Forecasted Quantity'), (
        'outgoing', 'Quantity On Hand - Outgoing Quantity')], string='Stock Type', required="1", default="on_hand")

    wk_warehouse_type = fields.Selection([('all', 'ALL'), ('specific', 'SPECIFIC')], string="Default Stock Location", required="1", default="all")

    wk_stock_location = fields.Many2one("stock.location", string="Stock Location", domain="[('usage', '=', 'internal')]")

    wk_warehouse_name = fields.Many2one('stock.warehouse', compute="_get_warehouse_id", string="Warehouse Name", readonly=True)

    wk_extra_msg = fields.Boolean(string="Extra Custom Message")

    wk_minimum_qty = fields.Float(string="Show When Quantity Less Than")

    wk_custom_message = fields.Char(string="Custom Message", translate=True, default="Last in Stock!!.")

    custome_stock_color = fields.Char(string="Custom Message Color", size=7,  help="Enter Hexa Decimal Value of Color", default="#FF6600")
    custom_stock_text = fields.Char(string="Text color", size=7, default="#FFFFFF")

    wk_deny_order = fields.Boolean(string="Deny Order", default=True)
    save_setting_on_product = fields.Boolean(string="Save Current Setting on Product", help="True value of this field save 'allow/deny order' and show 'stock quantity' setting on the product variants if you uncheck this box then product variants setting not overwrite by the main setting.", default=True)

    @api.one
    @api.depends('wk_stock_location')
    def _get_warehouse_id(self):
        if self.wk_stock_location:
            self.wk_warehouse_name = self.wk_stock_location.get_warehouse().id

    @api.model
    def create_wizard(self):
        wizard_id = self.env['website.message.wizard'].create({'message': _("Currently a Configuration Setting for Website Stock is active. You can not active other Configuration Setting. So, If you want to deactive the previous active configuration setting and active new configuration then click on 'Deactive Previous And Active New' button else click on 'cancel'.")})
        return {
            'name': _("Message"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'website.message.wizard',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new'
        }

    @api.multi
    def toggle_is_active(self):
        active_ids = self.search(
            [('is_active', '=', True), ('id', 'not in', [self.id])])
        for record in self:
            if active_ids:
                return self.create_wizard()
            record.is_active = not record.is_active

    @api.multi
    def set_product_default_value(self):
        product = self.env['product.product'].search([])
        record = self.search([('is_active', '=', True)])
        if record.wk_deny_order:
            product.write({'wk_order_allow': 'deny'})
        else:
            product.write({'wk_order_allow': 'allow'})

    @api.multi
    def write(self, vals):
        res = super(WebsiteStockConfigSettings, self).write(vals)
        for rec in self:
            if rec.is_active and rec.save_setting_on_product:
                rec.set_product_default_value()
        return res

# Responsible Developer:- Sunny Kumar Yadav #