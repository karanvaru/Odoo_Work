# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    days_before = fields.Integer("Before")
    renewal_prod = fields.Many2one(
        'product.product', string="Warranrt Renewal Product", required=True)
    warranty_expire_notification = fields.Boolean(
        string='Warranty Expire Notification',
        help='A notifcation mail will be sent to the customer before entered from warranty expire.')

    @api.multi
    def set_values(self):
        super().set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param(
            "warranty_management.warranty_expire_notification", self.warranty_expire_notification,
        )
        IrConfigPrmtr.set_param(
            "warranty_management.days_before", self.days_before,
        )
        IrConfigPrmtr.set_param(
            "warranty_management.renewal_prod", self.renewal_prod.id,
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        renewProdId = int(IrConfigPrmtr.get_param(
            'warranty_management.renewal_prod'))
        expireNotification = IrConfigPrmtr.get_param(
            'warranty_management.warranty_expire_notification')
        daysBefore = IrConfigPrmtr.get_param(
            'warranty_management.days_before')
        res.update({
            'warranty_expire_notification': expireNotification,
            'days_before': int(daysBefore),
            'renewal_prod': int(renewProdId),
        })
        return res
