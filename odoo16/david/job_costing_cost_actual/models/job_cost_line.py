# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobCostLine(models.Model): 
    _inherit = 'job.cost.line'
    
    @api.depends('purchase_order_line_ids', 'purchase_order_line_ids.product_qty', 'purchase_order_line_ids.price_unit', 'purchase_order_line_ids.order_id.state')
    def _compute_actual_purchase_cost(self):
        for rec in self:
#             rec.actual_purchase_cost = sum([p.order_id.state in ['purchase', 'done'] and (p.product_qty * p.price_unit) for p in rec.purchase_order_line_ids])
            actual_purchase_cost = 0.0
            for line in rec.purchase_order_line_ids:
                if line.order_id.state in ['purchase', 'done']:
                    if line.currency_id != rec.currency_id:
                        from_currency = line.currency_id
                        to_currency = rec.currency_id
                        compute_currency = from_currency.compute((line.product_qty * line.price_unit), to_currency)
                        actual_purchase_cost += compute_currency
                    else:
                        actual_purchase_cost += line.product_qty * line.price_unit
            rec.actual_purchase_cost = actual_purchase_cost

#    @api.depends('account_invoice_line_ids', 'account_invoice_line_ids.quantity','account_invoice_line_ids.price_unit', 'account_invoice_line_ids.invoice_id.state')
    @api.depends('account_invoice_line_ids',
                'account_invoice_line_ids.quantity',
                'account_invoice_line_ids.price_unit',
                'account_invoice_line_ids.move_id.state',
                # 'account_invoice_line_ids.move_id.invoice_payment_state')
                'account_invoice_line_ids.move_id.payment_state')
    def _compute_actual_vendor_cost(self):
        for rec in self:
#             rec.actual_vendor_cost = sum([p.invoice_id.state in ['open', 'paid'] and (p.quantity * p.price_unit) or 0.0 for p in rec.account_invoice_line_ids])
            actual_vendor_cost = 0.0
            for line in rec.account_invoice_line_ids:
#                if line.invoice_id.state in ['open', 'paid']:
                # if line.move_id.state in ['posted'] or line.move_id.invoice_payment_state in ['paid']:
                if line.move_id.state in ['posted'] or line.move_id.payment_state in ['paid']:
                    if line.currency_id != rec.currency_id:
                        from_currency = line.currency_id
                        to_currency = rec.currency_id
                        compute_currency = from_currency.compute((line.quantity * line.price_unit), to_currency)
                        actual_vendor_cost += compute_currency
                    else:
                        actual_vendor_cost += line.quantity * line.price_unit
            rec.actual_vendor_cost = actual_vendor_cost

    @api.depends('timesheet_line_ids','timesheet_line_ids.unit_amount','timesheet_line_ids.amount')
    def _compute_actual_timesheet_cost(self):
        for rec in self:
#             rec.actual_timesheet_cost = abs(sum([p.amount for p in rec.timesheet_line_ids]))
            actual_timesheet_cost = 0.0
            for line in rec.timesheet_line_ids:
                if line.currency_id != rec.currency_id:
                    from_currency = line.currency_id
                    to_currency = rec.currency_id
                    compute_currency = from_currency.compute(abs(line.amount), to_currency)
                    actual_timesheet_cost += compute_currency
                else:
                    actual_timesheet_cost += abs(line.amount)
            rec.actual_timesheet_cost = actual_timesheet_cost

    actual_purchase_cost = fields.Float(
        string='Actual Purchased Cost',
        compute='_compute_actual_purchase_cost',
        store=True
    )
    actual_vendor_cost = fields.Float(
        string='Actual Vendor Bill Cost',
        compute='_compute_actual_vendor_cost',
        store=True
    )
    actual_timesheet_cost = fields.Float(
        string='Actual Timesheet Cost',
        compute='_compute_actual_timesheet_cost',
        store=True
    )
