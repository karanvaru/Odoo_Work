# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from ast import literal_eval
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    prod_warranty_count = fields.Integer(compute='_compute_wrnty_count', string='Warranty Count')

    def _compute_wrnty_count(self):
        wrnty_data = self.env['warranty.registration'].read_group(domain=[('partner_id', 'child_of', self.ids)],
                                                      fields=['partner_id'], groupby=['partner_id'])
        # read to keep the child/parent relation while aggregating the read_group result in the loop
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict([(m['partner_id'][0], m['partner_id_count']) for m in wrnty_data])
        for partner in self:
            # let's obtain the partner id and all its child ids from the read up there
            item = next(p for p in partner_child_ids if p['id'] == partner.id)
            partner_ids = [partner.id] + item.get('child_ids')
            # then we can sum for all the partner's child
            partner.prod_warranty_count = sum(mapped_data.get(child, 0) for child in partner_ids)


    @api.multi
    def action_view_partner_warranty(self):
        self.ensure_one()
        action = self.env.ref('warranty_management.action_warranty_registration').read()[0]
        domain = action.get('domain') and literal_eval(action.get('domain')) or []
        action['domain'] = domain.append(('partner_id', 'child_of', self.id))
        return action