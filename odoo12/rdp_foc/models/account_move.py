# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_compare


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    foc_qty = fields.Float(string="FOC Qty")


# class AccountInvoice(models.Model):
#     _inherit = 'account.invoice'

#     def _prepare_invoice_line_from_po_line(self, line):
#         vals = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
#         vals['foc_qty'] = line.foc_qty
#         vals['quantity'] = line.product_qty
#         return vals

#     def _prepare_invoice_line_from_po_line(self, line):
#         if line.product_id.purchase_method == 'purchase':
#             qty = line.product_qty - line.qty_invoiced
#         else:
#             qty = line.qty_received - line.qty_invoiced
#             qty = qty - line.foc_qty
#         if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
#             qty = 0.0
#         taxes = line.taxes_id
#         invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes, line.product_id,
#                                                                         line.order_id.partner_id)
#         invoice_line = self.env['account.invoice.line']
#         date = self.date or self.date_invoice
#         data = {
#             'purchase_line_id': line.id,
#             'name': line.order_id.name + ': ' + line.name,
#             'origin': line.order_id.origin,
#             'uom_id': line.product_uom.id,
#             'product_id': line.product_id.id,
#             'account_id': invoice_line.with_context(
#                 {'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
#             'price_unit': line.order_id.currency_id._convert(
#                 line.price_unit, self.currency_id, line.company_id, date or fields.Date.today(), round=False),
#             'quantity': qty,

#             'discount': 0.0,
#             'account_analytic_id': line.account_analytic_id.id,
#             'analytic_tag_ids': line.analytic_tag_ids.ids,
#             'invoice_line_tax_ids': invoice_line_tax_ids.ids
#         }
#         account = invoice_line.with_context(purchase_line_id=line.id).get_invoice_line_account('in_invoice',
#                                                                                                line.product_id,
#                                                                                                line.order_id.fiscal_position_id,
#                                                                                                self.env.user.company_id)
#         if account:
#             data['account_id'] = account.id
#         if line.foc_qty:
#             data['foc_qty'] = line.foc_qty
#         return data
