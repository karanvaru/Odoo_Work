# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
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
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields,api,_


class AffiliateRequestInherit(models.Model):
    _inherit = "affiliate.request"


    parent_aff_key = fields.Char(String="Parent Affiliate Key")

    def action_aproove(self):
        result = super(AffiliateRequestInherit, self).action_aproove()
        if result and self.parent_aff_key:
            parentAff = self.env['res.partner'].sudo().search([('res_affiliate_key','=',self.parent_aff_key)],limit=1)
            if parentAff:
                self.partner_id.sudo().parent_affiliate= parentAff.id
        return result