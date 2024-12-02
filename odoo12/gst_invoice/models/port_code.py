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

class PortCode(models.Model):
    _name = "port.code"
    _description = "Port Code"

    name = fields.Char(string="Location Code", required=True)
    location_desc = fields.Char(string="Location Desc", required=True)
    country_code = fields.Char(string="Country Code", required=True)
    state = fields.Char(string="State", required=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            names = [record.state, record.location_desc, record.name]
            res.append((record.id, ' - '.join(reversed(names))))
        return res