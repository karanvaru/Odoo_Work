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
class AffiliateProgramInherit(models.Model):

    _inherit = "affiliate.program"

    parent_commision = fields.Float(string="Parent Commission",default=0, required=True)



    @api.model
    def set_parent_commission(self):
        self.sudo().search([],limit=1).parent_commision = 10
