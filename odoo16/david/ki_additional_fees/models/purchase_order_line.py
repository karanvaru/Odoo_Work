# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

# This file not in use
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    additional_fee_ids = fields.One2many(
        'additional.fee.line',
        'purchase_order_line_id',
        string="Additional Fee"
    )

    def action_show_details(self):
        act_read = self.env.ref('ki_additional_fees.purchase_order_line_wizard_action').read([])[0]
        act_read['view_mode'] = 'form'
        act_read['target'] = 'new'
        act_read['context'] = {}
        return act_read




