# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, date_utils
from odoo.tools.misc import format_date

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_confirm_bank(self):
        super(AccountBankStatement, self).button_confirm_bank()
        for statement in self:
            for line in statement.line_ids:
                if line.partner_id and line.online_partner_information:
                    # write value for account and merchant on partner only if partner has no value, in case value are different write False
                    value_merchant = line.partner_id.online_partner_information or line.online_partner_information
                    value_merchant = value_merchant if value_merchant == line.online_partner_information else False
                    line.partner_id.online_partner_information = value_merchant

    @api.model
    def _online_sync_bank_statement(self, transactions, online_account):
        """
         build a bank statement from a list of transaction and post messages is also post in the online_account of the journal.
         :param transactions: A list of transactions that will be created in the new bank statement.
             The format is : [{
                 'id': online id,                  (unique ID for the transaction)
                 'date': transaction date,         (The date of the transaction)
                 'name': transaction description,  (The description)
                 'amount': transaction amount,     (The amount of the transaction. Negative for debit, positive for credit)
                 'online_partner_information': optional field used to store information on the statement line under the
                    online_partner_information field (typically information coming from plaid/yodlee). This is use to find partner
                    for next statements
             }, ...]
         :param online_account: The online account for this statement
         Return: The number of imported transaction for the journal
        """
        # Since the synchronization succeeded, set it as the bank_statements_source of the journal
        created_stmt = self.env['account.bank.statement']
        created_stmt_lines = self.env['account.bank.statement.line']
        for journal in online_account.journal_ids:
            journal.sudo().write({'bank_statements_source': 'online_sync'})
            if not transactions:
                continue

            total = 0
            lines = []
            end_amount = 0

            sorted_transactions = sorted(transactions, key=lambda l: l['date'])
            # Get the last transaction date to set the last_sync date
            last_date = sorted_transactions[-1]['date']

            transactions_identifiers = [transaction['online_transaction_identifier'] for transaction in transactions] # Fetched transaction identifiers
            existing_transactions_ids = self.env['account.bank.statement.line'].search([('online_transaction_identifier', 'in', transactions_identifiers), ('journal_id', '=', journal.id)])
            existing_transactions_identifiers = existing_transactions_ids.mapped('online_transaction_identifier')

            transactions_partner_information = []
            for transaction in transactions:
                if transaction['online_transaction_identifier'] in existing_transactions_identifiers or transaction['amount'] == 0.0:
                    continue
                line = transaction.copy()
                line['date'] = fields.Date.from_string(transaction['date'])
                if transaction.get('online_partner_information'):
                    transactions_partner_information.append(transaction['online_partner_information'])
                total += line['amount']
                end_amount = online_account.balance
                lines.append((0, 0, line))

            if transactions_partner_information:
                self._cr.execute("""
                    SELECT p.online_partner_information, p.id FROM res_partner p
                    WHERE p.online_partner_information IN %s AND p.company_id = %s
                """, [tuple(transactions_partner_information), journal.company_id.id])
                partner_id_per_information = dict(self._cr.fetchall())
            else:
                partner_id_per_information = {}

            # Search for previous transaction end amount
            previous_statement = self.search([('journal_id', '=', journal.id)], order="date desc, id desc", limit=1)
            # For first synchronization, an opening bank statement line is created to fill the missing bank statements
            all_statement = self.search_count([('journal_id', '=', journal.id)])
            digits_rounding_precision = journal.currency_id.rounding if journal.currency_id else journal.company_id.currency_id.rounding
            if all_statement == 0 and not float_is_zero(end_amount - total, precision_rounding=digits_rounding_precision):
                lines.append((0, 0, {
                    'date': transactions and (transactions[0]['date']) or fields.Datetime.now(),
                    'name': _("Opening statement: first synchronization"),
                    'amount': end_amount - total,
                }))
                total = end_amount

            # If there is no new transaction, the bank statement is not created
            if lines:
                to_create = []
                # Depending on the option selected on the journal, either create a new bank statement or add lines to existing bank statement.
                previous_amount_to_report = 0
                for line in lines:
                    create = False
                    if not previous_statement or previous_statement.state == 'confirm':
                        to_create = lines
                        break
                    line_date = line[2]['date']
                    p_stmt = previous_statement.date
                    if journal.bank_statement_creation_groupby == 'day' and previous_statement.date != line[2]['date']:
                        create = True
                    elif journal.bank_statement_creation_groupby == 'week' and line_date.isocalendar()[1] != p_stmt.isocalendar()[1]:
                        create = True
                    elif journal.bank_statement_creation_groupby == 'bimonthly':
                        if (line_date.month != p_stmt.month or line_date.year != p_stmt.year):
                            create = True
                        elif line_date.day > 15 and p_stmt.day <= 15:
                            create = True
                    elif journal.bank_statement_creation_groupby == 'month' and (line_date.month != p_stmt.month or line_date.year != p_stmt.year):
                        create = True
                    elif not journal.bank_statement_creation_groupby or journal.bank_statement_creation_groupby == 'none':
                        create = True

                    if create:
                        to_create.append(line)
                    else:
                        previous_amount_to_report += line[2]['amount']
                        # Find partner id if exists
                        if line[2].get('online_partner_information'):
                            partner_info = line[2]['online_partner_information']
                            if partner_id_per_information.get(partner_info):
                                line[2]['partner_id'] = partner_id_per_information[partner_info]
                        line[2].update({
                            'journal_id': previous_statement.journal_id.id or journal.id,
                            'statement_id': previous_statement.id,
                            'company_id': previous_statement.company_id.id or self.env.company.id,
                        })
                        created_stmt_lines += self.env['account.bank.statement.line'].create(line[2])

                if not float_is_zero(previous_amount_to_report, precision_rounding=digits_rounding_precision):
                    previous_statement.write({'balance_end_real': previous_statement.balance_end_real + previous_amount_to_report})

                if to_create:
                    balance_start = None
                    if previous_statement:
                        balance_start = previous_statement.balance_end_real
                    sum_lines = sum([l[2]['amount'] for l in to_create])
                    for l in to_create:
                        # Find partner id if exists
                        if l[2].get('online_partner_information'):
                            partner_info = l[2]['online_partner_information']
                            if partner_id_per_information.get(partner_info):
                                l[2]['partner_id'] = partner_id_per_information[partner_info]
                        l[2]['journal_id'] = journal.id
                        l[2]['company_id'] = journal.company_id.id
                    created_stmt = self.create({
                        'name': _('online sync'),
                        'journal_id': journal.id,
                        'line_ids': to_create,
                        'balance_end_real': end_amount if balance_start is None else balance_start + sum_lines,
                        'balance_start': (end_amount - total) if balance_start is None else balance_start
                    })

            journal.account_online_account_id.sudo().write({'last_sync': last_date})
        created_stmt_lines += created_stmt.line_ids
        return created_stmt_lines


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    online_transaction_identifier = fields.Char("Online Transaction Identifier", readonly=True)
    online_partner_information = fields.Char(readonly=True)
    online_account_id = fields.Many2one(comodel_name='account.online.account', readonly=True)
    online_link_id = fields.Many2one(comodel_name='account.online.link', related='online_account_id.account_online_link_id', store=True, readonly=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    online_partner_information = fields.Char(readonly=True)
