# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class RepairOrder(models.Model):
    _inherit = "repair.order"

    rma_id = fields.Many2one("rma.rma", string="RMA ID")
    location_dest_id = fields.Many2one('stock.location', 'Delivery Location')
