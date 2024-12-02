# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    foc_qty = fields.Float(string="FOC Qty")

    # @api.multi
    # def _prepare_stock_moves(self, picking):
    #     res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
    #     for re in res:
    #         re['product_uom_qty'] += self.foc_qty
    #     return res

    # @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    # def _compute_qty_invoiced(self):
    #     for line in self:
    #         qty = 0.0
    #         for inv_line in line.invoice_lines:
    #             if inv_line.invoice_id.state not in ['cancel']:
    #                 if inv_line.invoice_id.type == 'in_invoice':
    #                     qty += inv_line.uom_id._compute_quantity(inv_line.quantity + inv_line.foc_qty, line.product_uom)
    #                 elif inv_line.invoice_id.type == 'in_refund':
    #                     qty -= inv_line.uom_id._compute_quantity(inv_line.quantity + inv_line.foc_qty, line.product_uom)
    #         line.qty_invoiced = qty