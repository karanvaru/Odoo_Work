# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models



class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrderInherit, self).button_confirm()
        self.picking_ids.write({'transaction_type_id': self.transaction_type_id.id})
        return res
