# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import time
from odoo import fields, models, api, _

import io
import json
from odoo.exceptions import AccessError, UserError, AccessDenied

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class GeneralView(models.TransientModel):
    _inherit = "account.general.ledger"


    def get_accounts_line(self, account_id, title):
        # to get the english translation of the title
        record_id = self.env['ir.actions.client'].with_context(
            lang=self.env.user.lang). \
            search([('name', '=', title)]).id
        trans_title = self.env['ir.actions.client'].with_context(
            lang='en_US').search([('id', '=', record_id)]).name
        company_id = self.env.companies.ids
        # Journal based account lines
        if self.journal_ids:
            journals = self.journal_ids
        else:
            journals = self.env['account.journal'].search(
                [('company_id', 'in', company_id)])
        if title == 'General Ledger' or trans_title == 'General Ledger':
            if self.journal_ids:
                journals = self.journal_ids
            else:
                journals = self.env['account.journal'].search(
                    [('company_id', 'in', company_id)])
        if title == 'Bank Book' or trans_title == 'Bank Book':
            journals = self.env['account.journal'].search(
                [('type', '=', 'bank'), ('company_id', 'in', company_id)])
        if title == 'Cash Book' or trans_title == 'Cash Book':
            journals = self.env['account.journal'].search(
                [('type', '=', 'cash'), ('company_id', 'in', company_id)])
        # account based move lines
        if account_id:
            accounts = self.env['account.account'].search(
                [('id', '=', account_id)])
        else:
            company_id = self.env.companies
            company_domain = [('company_id', 'in', company_id.ids)]
            accounts = self.env['account.account'].search(company_domain)
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Prepare initial sql query and Get the initial move lines
        if self.date_from:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(
                date_from=self.env.context.get('date_from'), date_to=False,
                initial_bal=True)._query_get()
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        final_filters = " AND ".join(wheres)
        final_filters = final_filters.replace('account_move_line__move_id',
                                              'm').replace(
            'account_move_line', 'l')
        new_final_filter = final_filters
        if self.target_move == 'posted':
            new_final_filter += " AND m.state = 'posted'"
        else:
            new_final_filter += " AND m.state in ('draft','posted')"
        if self.date_from:
            new_final_filter += " AND l.date >= '%s'" % self.date_from
        if self.date_to:
            new_final_filter += " AND l.date <= '%s'" % self.date_to
        if journals:
            new_final_filter += ' AND j.id IN %s' % str(
                tuple(journals.ids) + tuple([0]))
        if accounts:
            WHERE = "WHERE l.account_id IN %s" % str(
                tuple(accounts.ids) + tuple([0]))
        else:
            WHERE = "WHERE l.account_id IN %s"
        if self.analytic_ids:
            WHERE += ' AND an.id IN %s' % str(
                tuple(self.analytic_ids.ids) + tuple([0]))

        # Get move lines base on sql query and Calculate the total balance of
        # move lines
        sql = ('''SELECT l.id AS lid,m.id AS move_id, l.account_id AS account_id,
                to_char(l.date, 'DD/MM/YYYY')AS ldate, j.code AS lcode, l.currency_id, l.amount_currency,
                l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, 
                COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.balance),0) AS balance,
                m.name AS move_name, c.symbol AS currency_code, 
                p.name AS partner_name, anl.keys
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                LEFT JOIN LATERAL (
                SELECT jsonb_object_keys(l.analytic_distribution)::INT 
                AS keys) anl ON true
                LEFT JOIN account_analytic_account an ON (anl.keys = an.id)                
                JOIN account_journal j ON (l.journal_id=j.id)
                JOIN account_account a ON (l.account_id = a.id) '''
               + WHERE + new_final_filter + ''' GROUP BY l.id, m.id,  
               l.account_id, l.date, j.code, l.currency_id, l.amount_currency,
               l.ref, l.name, m.name, c.symbol, c.position, p.name, anl.keys ORDER BY l.date desc''')
        params = tuple(where_params)
        cr.execute(sql, params)
        account_ress = cr.dictfetchall()
        i = 0
        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = (account.currency_id and account.currency_id or
                        account.company_id.currency_id)
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['id'] = account.id
            res['move_lines'] = account_ress
            account_res.append(res)
        currency = self._get_currency()
        return {
            'report_lines': account_res,
            'currency': currency,
        }
