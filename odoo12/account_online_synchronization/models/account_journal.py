# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def _get_statement_creation_possible_values(self):
        return [('none', 'Create one statement per synchronization'),
                ('day', 'Create daily statements'),
                ('week', 'Create weekly statements'),
                ('bimonthly', 'Create bi-monthly statements'),
                ('month', 'Create monthly statements')]

    next_link_synchronization = fields.Datetime("Online Link Next synchronization", related='account_online_link_id.next_refresh')
    account_online_account_id = fields.Many2one('account.online.account', ondelete='set null')
    account_online_link_id = fields.Many2one('account.online.link', related='account_online_account_id.account_online_link_id', readonly=True, store=True)
    account_online_link_state = fields.Selection(related="account_online_link_id.state", readonly=True)
    bank_statement_creation_groupby = fields.Selection(selection=_get_statement_creation_possible_values,
                                               help="Defines when a new bank statement will be created when fetching "
                                                    "new transactions from your bank account.",
                                               default='month',
                                               string='Bank Statements Group By')

    @api.model
    def _cron_fetch_online_transactions(self):
        for journal in self.search([('account_online_account_id', '!=', False)]):
            if journal.account_online_link_id.auto_sync:
                try:
                    journal.with_context(cron=True).manual_sync()
                    # for cron jobs it is usually recommended to commit after each iteration, so that a later error or job timeout doesn't discard previous work
                    self.env.cr.commit()
                except UserError:
                    pass

    def manual_sync(self):
        self.ensure_one()
        if self.account_online_link_id:
            account = self.account_online_account_id
            return self.account_online_link_id.with_context(dont_show_transactions=True)._fetch_transactions(accounts=account)

    def unlink(self):
        '''
        Override of the unlink method.\n
        That's usefull to unlink account.online.account too.\n
        '''
        self.mapped('account_online_account_id').unlink()
        return super(AccountJournal, self).unlink()

    def action_configure_bank_journal(self):
        '''
        Override the "action_configure_bank_journal" and change the flow for the
        "Configure" button in dashboard.
        '''
        return self.env['account.online.link'].action_new_synchronization()
