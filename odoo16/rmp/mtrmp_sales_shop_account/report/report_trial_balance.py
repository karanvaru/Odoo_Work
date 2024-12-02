# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_trialbalance'


#     def _get_accounts(self, accounts, display_account):
#         """ compute the balance, debit and credit for the provided accounts
#             :Arguments:
#                 `accounts`: list of accounts record,
#                 `display_account`: it's used to display either all accounts or those accounts which balance is > 0
#             :Returns a list of dictionary of Accounts with following key and value
#                 `name`: Account name,
#                 `code`: Account code,
#                 `credit`: total amount of credit,
#                 `debit`: total amount of debit,
#                 `balance`: total amount of balance,
#         """
# 
#         account_result = {}
#         # Prepare sql query base on selected parameters from wizard
#         tables, where_clause, where_params = self.env['account.move.line']._query_get()
#         tables = tables.replace('"','')
#         if not tables:
#             tables = 'account_move_line'
#         wheres = [""]
#         if where_clause.strip():
#             wheres.append(where_clause.strip())
#         filters = " AND ".join(wheres)
#         # compute the balance, debit and credit for the provided accounts
#         request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, "
#                    "(SUM(debit) - SUM(credit)) AS balance" +\
#                    " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
#         params = (tuple(accounts.ids),) + tuple(where_params)
#         self.env.cr.execute(request, params)
#         for row in self.env.cr.dictfetchall():
#             account_result[row.pop('id')] = row
# 
#         initial_balance = self._get_initial_balance(accounts)
#         account_res = []
#         for account in accounts:
#             res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
#             currency = account.currency_id and account.currency_id or account.company_id.currency_id
#             res['code'] = account.code
#             res['name'] = account.name
#             if initial_balance.get(account.id):
#                 res['initial_balance'] = initial_balance[account.id]['balance']
#             else:
#                 res['initial_balance'] = 0
#             if account.id in account_result:
#                 res['debit'] = account_result[account.id].get('debit')
#                 res['credit'] = account_result[account.id].get('credit')
#                 res['balance'] = res['initial_balance'] + account_result[account.id].get('balance')
#             else:
#                 res['balance'] = res['initial_balance']
#             if display_account == 'all':
#                 account_res.append(res)
#             if display_account == 'not_zero' and not currency.is_zero(res['balance']):
#                 account_res.append(res)
#             if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
#                 account_res.append(res)
#         return account_res

    def _get_initial_balance(self, accounts):
        if not self.env.context.get('date_from'):
            return {}
        initial_balance = {}

        context = {
            'date_to': self.env.context['date_from'],
        }
        tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
        tables = tables.replace('"', '') if tables else 'account_move_line'

        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)

        request = (f"SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, "
                   f"(SUM(debit) - SUM(credit)) AS balance "
                   f"FROM {tables} WHERE account_id IN %s {filters} GROUP BY account_id")

        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            initial_balance[row.pop('id')] = row
        return initial_balance

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, "
                   "(SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        initial_balance = self._get_initial_balance(accounts)
        account_res = []
        
        account_group_dict = {
            0 : {
                'lines': [],
                'credit': 0.0,
                'debit': 0.0,
                'balance': 0,
                'code': '0000',
                'name': 'Undefined',
                'initial_balance': 0            }
        }
        
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if initial_balance.get(account.id):
                res['initial_balance'] = initial_balance[account.id]['balance']
            else:
                res['initial_balance'] = 0
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = res['initial_balance'] + account_result[account.id].get('balance')
            else:
                res['balance'] = res['initial_balance']
            
            if account.group_id:
                if account.group_id.id not in account_group_dict:
                    account_group_dict[account.group_id.id] = {
                        'lines': [],
                        'credit': 0.0,
                        'debit': 0.0,
                        'balance': 0,
                        'code': '0000',
                        'name': account.group_id.name,
                        'initial_balance': 0
                        }
                if not self._context.get('group_summary', False):
                    account_group_dict[account.group_id.id]['lines'].append(res)
                    
                account_group_dict[account.group_id.id]['credit'] += res['credit']
                account_group_dict[account.group_id.id]['debit'] += res['debit']
                account_group_dict[account.group_id.id]['balance'] += res['balance']
                account_group_dict[account.group_id.id]['initial_balance'] += res['initial_balance']
            else:
                if not self._context.get('group_summary', False):
                    account_group_dict[0]['lines'].append(res)

                account_group_dict[0]['credit'] += res['credit']
                account_group_dict[0]['debit'] += res['debit']
                account_group_dict[0]['balance'] += res['balance']
                account_group_dict[0]['initial_balance'] += res['initial_balance']
            
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                account_res.append(res)
        lines = []
        for accgrp in account_group_dict:
            accgrp_val = account_group_dict[accgrp]
            lines.append({
                'credit': accgrp_val['credit'],
                'debit': accgrp_val['debit'],
                'balance': accgrp_val['balance'],
                'code': accgrp_val['code'],
                'name': accgrp_val['name'],
                'initial_balance': accgrp_val['initial_balance'],
                'is_group': True
            })
            for l in accgrp_val['lines']:
                lines.append(l)
        return lines

