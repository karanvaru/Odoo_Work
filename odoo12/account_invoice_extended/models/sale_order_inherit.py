# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        res = super(SaleOrderLineInherit, self).action_confirm
        self.picking_ids.write({'transaction_type_id': self.transaction_type_id.id})
        return res