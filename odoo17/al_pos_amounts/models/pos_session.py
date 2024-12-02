from odoo import models, fields, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    cash_total = fields.Monetary(
        'Cash Total (by user)'
    )
    visa_total = fields.Monetary(
        'Visa Total (by user)'
    )
    session_cash_total = fields.Monetary(
        string='Cash Total (Payment)',
        compute="_compute_total_value_bank_cash",
        store=True
    )
    session_bank_total = fields.Monetary(
        string='Bank Total(Payment)',
        compute="_compute_total_value_bank_cash",
        store=True
    )
    cash_diff = fields.Monetary(
        string='Cash Diff',
        compute="_compute_manual_compute_diff",
        store=True
    )
    visa_diff = fields.Monetary(
        string='Visa Diff',
        compute="_compute_manual_compute_diff",
        store=True
    )
    total_diff = fields.Monetary(
        string='Total Diff',
        compute="_compute_total_diff",
        store=True
    )

    @api.depends('session_cash_total', 'cash_total', 'session_bank_total', 'visa_total')
    def _compute_manual_compute_diff(self):
        for rec in self:
            rec.cash_diff = -(rec.session_cash_total - rec.cash_total)
            rec.visa_diff = -(rec.session_bank_total - rec.visa_total)

    @api.depends('cash_diff', 'visa_diff')
    def _compute_total_diff(self):
        for rec in self:
            rec.total_diff = rec.cash_diff + rec.visa_diff

    def _compute_total_value_bank_cash(self):
        for rec in self:
            rec.session_cash_total = 0
            rec.session_bank_total = 0
            pos_payments = self.env['pos.payment'].search([('session_id', '=', rec.id)])
            cash_data = sum(
                payment.amount for payment in pos_payments if payment.payment_method_id.journal_id.type == 'cash')
            bank_data = sum(
                payment.amount for payment in pos_payments if payment.payment_method_id.journal_id.type == 'bank')
            rec.session_cash_total = cash_data
            rec.session_bank_total = bank_data

    def read(self, fields=None, load='_classic_read'):
        result = super(PosSession, self).read(fields, load)
        # if 'session_cash_total' in fields or 'session_bank_total' in fields:
        self._compute_total_value_bank_cash()
        self._compute_total_diff()
        return result

    def update_close_session_cash_value(self, cash_diff, visa_diff):
        self.write({
            'cash_total': cash_diff,
            'visa_total': visa_diff,
        })
