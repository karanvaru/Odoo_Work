# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models



class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_warranty = fields.Boolean(string='Allow Warranty')
    warranty_type = fields.Selection([
        ('free', 'Free'),
        ('paid', 'Paid')], default="free", string='Warranty Type')
    warranty_auto_confirm = fields.Boolean(
        string="Auto Warranty Confirm",
        help="If set 'True' then warranty will get auto confirm")
    warranty_fee = fields.Float(string="Warranty Fee")
    warranty_period = fields.Integer(string="Period", default=6)
    warranty_unit = fields.Selection([
        ('days', 'Days'),
        ('months', 'Month'),
        ('years', 'Year')], default="months", string="Unit")
    allow_renewal = fields.Boolean(string="Can Be Renew")
    renewal_period = fields.Integer(string="Renewal Period", default=6)
    renewal_unit = fields.Selection([
        ('days', 'Days'),
        ('months', 'Month'),
        ('years', 'Year')], default="months", string="Unit")
    max_renewal_times = fields.Integer(string="Max. Renewal Times", default=1)
    renewal_cost = fields.Float(string="Renewal Cost")




    @api.model
    def create(self, vals):
        _ = dict(self._context or {})
        return super().create(vals)

    @api.multi
    def write(self, vals):
        _ = dict(self._context or {})
        return super().write(vals)

