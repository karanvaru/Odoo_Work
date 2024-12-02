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

class Partner(models.Model):
    _inherit = "res.partner"

    @api.one
    @api.depends('vat')
    def _compute_partner_type(self):
        if self.country_id.code == 'IN':
            if self.vat:
                self.partner_type = 'B2B'
            else:
                self.partner_type = 'B2BUR'
        else:
            self.partner_type = 'IMPORT'

    partner_type = fields.Selection([
                                ('B2B', 'B2B'),
                                ('B2BUR', 'B2BUR'),
                                ('IMPORT', 'IMPS/IMPG')
                            ],
                            string='Partner Type',
                            copy=False,
                            compute='_compute_partner_type',
                            help="""
                                * B2B : B2B Supplies.
                                * B2BUR : Inward supplies from unregistered Supplier.
                                * IMPORT : Import of Services/Goods.
                            """
            )
