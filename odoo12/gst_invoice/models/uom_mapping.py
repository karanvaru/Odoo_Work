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

class UomMapping(models.Model):
    _name = "uom.mapping"
    _description = "UOM Mapping"

    name = fields.Many2one("unit.quantity.code", string="Unit Quantity Code", help="UQC (Unit of Measure) of goods sold")
    uom = fields.Many2one("uom.uom", string="Units of Measure", help="Units of Measure use for all stock operation")
