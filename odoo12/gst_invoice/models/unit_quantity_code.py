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

from odoo import api, fields, models

class UnitQuantityCode(models.Model):
    _name = "unit.quantity.code"
    _description = "Unit Quantity Code"

    name = fields.Char(string="Unit", help="UQC (Unit of Measure) of goods sold")
    code = fields.Char(string="Code", help="Code for UQC (Unit of Measure)")
