# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_
from datetime import timedelta
from datetime import datetime
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class CommissionHistory(models.Model):
    _name = 'commission.history'
    _description = "Commission History"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
        readonly=True
    )
    date_start = fields.Date(
        string="Start Date",
        required=True,
        default=fields.Date.today,
        readonly=True
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        default=fields.Date.today,
        readonly=True
    )

    commission_user_id = fields.Many2one(
        'hr.employee',
        string="Commission User",
        readonly=True
    )

    commission_line_ids = fields.One2many(
        'commission.history.line',
        'commission_history_id',
        string="Lines",
    )


    total_amount = fields.Float(
        string="Commission Amount",
        compute="_compute_amount",
        store=True,
        tracking=1,
    )
    total_commission = fields.Float(
        string="Total Commission Amount",
        compute="_compute_total_amount",
        store=True,
        tracking=1,
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related="company_id.currency_id",
        string="Currency",
        store=True,
        readonly=True
    )
    Confirmed_date = fields.Date(
        string="Confirm Date",
        readonly=True,
        # default=fields.Date.today
    )

    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('submit', 'Submitted'),
            ('exception', 'Exception'),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled'),
            ('invoiced', 'Invoiced'),
            ('reject', 'Rejecetd'),
            ('paid', 'Paid')
        ],
        string="Status",
        default='new',
        required=True,
        tracking=1,
    )
    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice",
        readonly=True
    )
    sale_id = fields.Many2one(
        'sale.order',
        string="Sale",
        readonly=True
    )
    amount_paid = fields.Float(
        compute="_compute_amount_paid",
        store=True,
        tracking=1,
        string="Commission Paid"
    )
    note = fields.Text(
        string="Notes"
    )
    exception_reason = fields.Text(
        string='Exception Reason',
    )
    payslip_id = fields.Many2one(
        'hr.payslip',
        string="Payslip",
        copy=False
    )

    def action_open_commission_bills(self):
        act = self.env.ref('account.action_move_in_invoice_type')
        act_read = act.read([])[0]
        act_read['domain'] = [('commission_sheet_id', '=', self.id)]
        return act_read

    def action_reset_draft(self):
        self.write({'state': 'new'})

    # def action_exception(self):
    #     self.write({'state': 'exception'})

    def action_mark_as_paid(self):
        self.write({'state': 'paid'})

    def action_submit(self):
        for rec in self:
            Confirmed_date = fields.Date.today()
            self.write({'state': 'submit'})

    def action_cancel(self):
        self.write({'state': 'cancel'})


    def view_source(self):
        self.ensure_one()
        if self.sale_id:
            act = self.env.ref('sale.action_quotations_with_onboarding')
            act_read = act.read([])[0]
            act_read['domain'] = [('id', '=', self.sale_id.id)]
            return act_read

    def refresh_commission(self):
        raise UserError("Refresh........")

    def action_approve(self):
        for rec in self:
            approval_date = fields.Date.today()
            rec.write({'state': "approve"})

    def action_reject(self):
        for rec in self:
            rec.write({'state': "reject"})

    def action_level_commission_history_line(self):
        act = self.env.ref('ki_agent_commission.action_level_commission_line')
        act_read = act.read([])[0]
        act_read['domain'] = [('commission_history_id', '=', self.id), ('commission_type', '=', 'level')]
        return act_read

    @api.depends(
        'commission_line_ids',
        'commission_line_ids.commission_amount',
        'commission_line_ids.state',
    )
    def _compute_amount(self):
        for record in self:
            record.total_amount = sum(
                l.commission_amount
                for l in record.commission_line_ids.filtered(
                    lambda i: i.filtered(
                        lambda l: l.state in ('approve', 'invoiced')
                    )
                )
            )

    @api.depends(
        'commission_line_ids',
        'commission_line_ids.commission_amount',
        'commission_line_ids.state',
    )
    def _compute_total_amount(self):
        for record in self:
            record.total_commission = sum(
                l.commission_amount
                for l in record.commission_line_ids.filtered(
                    lambda i: i.filtered(
                        lambda l: l.state in ('approve', 'invoiced', 'draft')
                    )
                )
            )

    @api.depends(
        'invoice_id',
        'invoice_id.amount_residual',
        'invoice_id.amount_total'
    )
    def _compute_amount_paid(self):
        for record in self:
            total_amount = 0.0
            for payment in record.invoice_id:
                total_amount += (payment.amount_total - payment.amount_residual)
            record.amount_paid = total_amount

    @api.model_create_multi
    def create(self, vals_list):
        seq_obj = self.env['ir.sequence']
        for vals in vals_list:
            if 'company_id' in vals:
                vals['name'] = seq_obj.with_company(vals['company_id']).next_by_code('commission.history')
            else:
                vals['name'] = seq_obj.next_by_code('commission.history')
        return super(CommissionHistory, self).create(vals_list)

    def _write(self, values):
        super_res = super(CommissionHistory, self)._write(values)
        if values.get('amount_paid', 0.0):
            for commission in self:
                if commission.total_amount == values['amount_paid']:
                    self._cr.execute("""
                            UPDATE
                                commission_history
                            SET
                                state = 'paid'
                            WHERE
                                id=%s

                        """ % (commission.id))
        return super_res

    def unlink(self):
        for commission in self:
            if commission.state not in ('new', 'cancel'):
                raise UserError(
                    _('You cannot delete an commission sheet which is not draft or cancelled.')
                )
        return super(CommissionHistory, self).unlink()

    @api.model
    def _prepare_invoice(self):
        invoice_obj = self.env['account.move'].sudo()
        ctx = self._context.copy()
        ctx.update({
            'default_move_type': 'in_invoice',
            'company_id': self.company_id.id,
            'default_currency_id': self.currency_id.id,
        })
        default_values = invoice_obj.with_context(ctx).default_get(invoice_obj._fields.keys())

        inv_values = default_values

        user = self.commission_user_id
        inv_values.update({
            'partner_id': self.commission_user_id.address_id.id,
            'name': self.name,
            'user_id': self.commission_user_id.id,
            'invoice_date': fields.Date.today(),
            'move_type': 'in_invoice',
            'commission_sheet_id': self.id,
            'ref': user.name + ':' + self.name,
        })
        bill = invoice_obj.new(inv_values)
        bill._onchange_partner_id()

        bill_values = bill._convert_to_write({
            name: bill[name] for name in bill._cache
        })
        return bill_values

    @api.model
    def _prepare_invoice_line(self, invoice_id):
        invoice_line_obj = self.env['account.move.line'].sudo()
        ctx = self._context.copy()

        product = self.company_id.commission_product_id
        if not product:
            raise ValidationError(
                _('Please define commission invoice product on company!')
            )
        default_values = invoice_line_obj.with_context(ctx).default_get(
            invoice_line_obj._fields.keys()
        )
        inv_line_values = default_values
        total_amount = sum(
            i.commission_amount for i in self.commission_line_ids.filtered(lambda l: l.state == 'approve'))
        inv_line_values.update({
            'product_id': product.id,
            'price_unit': total_amount,
            'quantity': 1.0,
            'move_id': invoice_id.id
        })
        bill_line = invoice_line_obj.new(inv_line_values)
        #         bill_line.tax_ids = [(6, 0, [])]
        bill_line_values = bill_line._convert_to_write({
            name: bill_line[name] for name in bill_line._cache
        })
        name = bill_line_values.get('name', '')
        name = name + ("[Commission For: %s To %s]" % (self.date_start, self.date_end))
        bill_line_values.update({
            'price_unit': total_amount,
            'name': name

        })
        return bill_line_values


    def action_invoice_create(self):
        invoices = []
        for commission in self:
            commission_lines = self.commission_line_ids.filtered(
                lambda l: l.state == 'approve'
            )
            total_amount = sum(
                i.commission_amount
                for i in commission_lines
            )
            if total_amount <= 0:
                raise ValidationError(
                    _('Not sufficiant amount to create bill!')
                )

            invoice_vals = commission._prepare_invoice()
            invoice_id = self.env['account.move'].sudo().create(invoice_vals)

            invoice_line_values = commission._prepare_invoice_line(invoice_id)
            invoice_id.write({
                'invoice_line_ids': [(0, 0, invoice_line_values)]
            })
            commission.sudo().write({
                'invoice_id': invoice_id.id,
                'state': 'invoiced',
            })
            commission_lines.update({'state': 'invoiced'})
            invoices.append(invoice_id.id)
        action = self.env.ref('account.action_move_in_invoice_type')
        action_read = action.read([])[0]
        action_read['domain'] = [('id', 'in', invoices), ('move_type', '=', 'in_invoice')]
        return action_read