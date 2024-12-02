# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class PurchaseOrderLineWizard(models.Model):
    _name = 'purchase.order.line.wizard'
    _description = 'Purchase Order Line Wizard'

    additional_fee_ids = fields.One2many(
        'additional.fee.line',
        'purchase_order_line_wizard_id',
        string="Additional Fee"
    )
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')

    @api.model
    def default_get(self, fields):
        rec = super(PurchaseOrderLineWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_browse_id = self.env['purchase.order.line'].browse(active_id)
        rec.update({
            'additional_fee_ids': active_browse_id.additional_fee_ids,
            'state': active_browse_id.order_id.state
        })
        return rec

    def add_additional_fee(self):
        purchase_line_id = self.env['purchase.order.line'].browse(self._context.get('active_id'))
        # amount = 0
        # for rec in self.additional_fee_ids:
        #     amount += rec.amount
        # price_unit = purchase_line_id.product_id.standard_price + amount
        purchase_line_id.update({
            'additional_fee_ids': self.additional_fee_ids,
            # 'price_unit': price_unit
        })
