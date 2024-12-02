# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import  UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    receipts_sequence = fields.Boolean(string='Receipts Sequence', default=False)


class AccountMove(models.Model):
    _inherit = "account.move"


    @api.model
    def _search_default_journal(self, journal_types):
        company_id = self._context.get('default_company_id', self.env.company.id)
        domain = [('company_id', '=', company_id), ('type', 'in', journal_types)]
        move_type = self._context.get('default_move_type', 'entry')
        if move_type == 'out_receipt':
            domain += [('receipts_sequence', '=', True)]

        journal = None
        if self._context.get('default_currency_id'):
            currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
            journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)
        return journal

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
            if m.move_type == 'out_receipt':
                domain += [('receipts_sequence', '=', True)]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)
