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
                
                
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            init_filters = init_filters.replace('account_move_line__move_id',
                                                  'm').replace(
                'account_move_line', 'l')
            new_init_filters = init_filters
            if self.target_move == 'posted':
                new_init_filters += " AND m.state = 'posted'"
            else:
                new_init_filters += " AND m.state in ('draft','posted')"
            if self.date_from:
                new_init_filters += " AND l.date < '%s'" % self.date_from
            if journals:
                new_init_filters += ' AND j.id IN %s' % str(
                    tuple(journals.ids) + tuple([0]))
            if accounts:
                INIT_WHERE = "WHERE l.account_id IN %s" % str(
                    tuple(accounts.ids) + tuple([0]))
            else:
                INIT_WHERE = "WHERE l.account_id IN %s"
            if self.analytic_ids:
                INIT_WHERE += ' AND an.id IN %s' % str(
                    tuple(self.analytic_ids.ids) + tuple([0]))
    
            # Get move lines base on sql query and Calculate the total balance of
            # move lines
            init_sql = ('''SELECT 0 AS lid, '' AS move_id, l.account_id AS account_id,
                    '' AS ldate, '' AS lcode, NULL AS currency_id, 0.0 AS amount_currency,
                    '' AS lref, 'Initial Balance' AS lname,
                    COALESCE(SUM(l.debit),0.0) AS debit,
                    COALESCE(SUM(l.credit),0.0) AS credit, 
                    COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance,
                    '' AS move_name, 'INR' AS currency_code, 
                    '' AS partner_name
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
                   + INIT_WHERE + new_init_filters + ''' GROUP BY 
                   l.account_id''')
            init_params = tuple(init_where_params)
            cr.execute(init_sql, init_params)
            init_account_ress = cr.dictfetchall()
            for row in init_account_ress:
                move_lines[row['account_id']].append(row)
                
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
            if move_lines.get(account.id):
                account_ress.insert(0, move_lines[account.id][0])

            res['move_lines'] = account_ress
            account_res.append(res)
        currency = self._get_currency()
        return {
            'report_lines': account_res,
            'currency': currency,
        }

    def _get_accounts(self, accounts, init_balance, display_account, data):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}
        # Prepare initial sql query and Get the initial move lines
        if init_balance and data.get('date_from'):
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(
                date_from=self.env.context.get('date_from'), date_to=False,
                initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id',
                                           'm').replace('account_move_line',
                                                        'l')
            new_filter = filters
            if data['target_move'] == 'posted':
                new_filter += " AND m.state = 'posted'"
            else:
                new_filter += " AND m.state in ('draft','posted')"
            if data.get('date_from'):
                new_filter += " AND l.date < '%s'" % data.get('date_from')
            if data['journals']:
                new_filter += ' AND j.id IN %s' % str(
                    tuple(data['journals'].ids) + tuple([0]))
            if data.get('accounts'):
                WHERE = "WHERE l.account_id IN %s" % str(
                    tuple(data.get('accounts').ids) + tuple([0]))
            else:
                WHERE = "WHERE l.account_id IN %s"
            if data.get('analytics'):
                WHERE += ' AND an.id IN %s' % str(
                    tuple(data.get('analytics').ids) + tuple([0]))
            if data['account_tags']:
                WHERE += ' AND tag IN %s' % str(data.get('account_tags'))
            sql = ('''SELECT
            l.account_id AS account_id,
            a.code AS code,
            a.id AS id,
            a.name AS name,
            ROUND(COALESCE(SUM(l.debit),0),2) AS debit,
            ROUND(COALESCE(SUM(l.credit),0),2) AS credit,
            ROUND(COALESCE(SUM(l.balance),0),2) AS balance,
            anl.keys,
            act.name AS tag
            FROM
                account_move_line l
            LEFT JOIN
                account_move m ON (l.move_id = m.id)
            LEFT JOIN
                res_currency c ON (l.currency_id = c.id)
            LEFT JOIN
                res_partner p ON (l.partner_id = p.id)
            JOIN
                account_journal j ON (l.journal_id = j.id)
            JOIN
                account_account a ON (l.account_id = a.id)
            LEFT JOIN
                account_account_account_tag acct ON (acct.account_account_id = l.account_id)
            LEFT JOIN
                account_account_tag act ON (act.id = acct.account_account_tag_id)
            LEFT JOIN LATERAL (
                SELECT jsonb_array_elements_text(l.analytic_distribution->'ids')::INT AS keys
            ) anl ON true
            LEFT JOIN
                account_analytic_account an ON (anl.keys = an.id) '''+ WHERE + new_filter + '''
            GROUP BY
                l.account_id, a.code, a.id, a.name, anl.keys, act.name''')

            if data.get('accounts'):
                params = tuple(init_where_params)
            else:
                params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                row['m_id'] = row['account_id']
#                 move_lines[row.pop('account_id')].append(row)
                move_lines[row['account_id']].append(row)
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        final_filters = " AND ".join(wheres)
        final_filters = final_filters.replace('account_move_line__move_id',
                                              'm').replace(
            'account_move_line', 'l')
        new_final_filter = final_filters
        if data['target_move'] == 'posted':
            new_final_filter += " AND m.state = 'posted'"
        else:
            new_final_filter += " AND m.state in ('draft','posted')"
        if data.get('date_from'):
            new_final_filter += " AND l.date >= '%s'" % data.get('date_from')
        if data.get('date_to'):
            new_final_filter += " AND l.date <= '%s'" % data.get('date_to')
        if data['journals']:
            new_final_filter += ' AND j.id IN %s' % str(
                tuple(data['journals'].ids) + tuple([0]))
        if data.get('accounts'):
            WHERE = "WHERE l.account_id IN %s" % str(
                tuple(data.get('accounts').ids) + tuple([0]))
        else:
            WHERE = "WHERE l.account_id IN %s"

        if self.analytic_ids:
            WHERE += ' AND an.id IN %s' % str(
                tuple(self.analytic_ids.ids) + tuple([0]))
        if data.get('account_tags'):
            WHERE += ' AND act.id IN %s' % str(
                tuple(data.get('account_tags').ids) + tuple([0]))

        # Get move lines base on sql query and Calculate the total balance
        # of move lines
        sql = ('''SELECT l.account_id AS account_id, a.code AS code, 
                    a.id AS id, a.name AS name,  l.id as line_id,
                    ROUND(COALESCE(SUM(l.debit),0),2) AS debit,
                    ROUND(COALESCE(SUM(l.credit),0),2) AS credit,
                    ROUND(COALESCE(SUM(l.balance),0),2) AS balance,
                    anl.keys, act.name as tag
                    FROM account_move_line l
                    LEFT JOIN account_move m ON (l.move_id = m.id)
                    LEFT JOIN res_currency c ON (l.currency_id = c.id)
                    LEFT JOIN res_partner p ON (l.partner_id = p.id)
                    JOIN account_journal j ON (l.journal_id = j.id)
                    JOIN account_account a ON (l.account_id = a.id)
                    LEFT JOIN account_account_account_tag acct ON 
                    (acct.account_account_id = l.account_id)
                    LEFT JOIN account_account_tag act ON 
                    (act.id = acct.account_account_tag_id)
                    LEFT JOIN LATERAL (
                    SELECT jsonb_object_keys(l.analytic_distribution)::INT 
                    AS keys) anl ON true
                    LEFT JOIN account_analytic_account an 
                    ON (anl.keys = an.id)'''
               + WHERE + new_final_filter + ''' GROUP BY l.account_id, 
                   a.code,a.id,a.name,anl.keys, act.name, l.id''')
        if data.get('accounts'):
            params = tuple(where_params)
        else:
            params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)
        account_res = cr.dictfetchall()
        unique_line_ids = set()
        filtered_records = []
        account_records = []
        for record in account_res:
            line_id = record['line_id']
            if line_id not in unique_line_ids:
                unique_line_ids.add(line_id)
                filtered_records.append(record)
            if record['account_id'] not in account_records:
                account_records.append(record['account_id'])
                if move_lines.get(record['account_id']) and len(move_lines[record['account_id']]) > 0:
                    filtered_records.insert(0, move_lines[record['account_id']][0])
        return filtered_records

    @api.model
    def view_report(self, option, title):
        result = super(GeneralView, self).view_report(option, title)
        result['debit_total'] = round(result['debit_total'], 2)
        result['credit_total'] = round(result['credit_total'], 2)
        result['debit_balance'] = round(result['debit_balance'], 2)
        return result
        
    def _get_report_value(self, data):
        result = super(GeneralView, self)._get_report_value(data)
        result['debit_total'] = round(result['debit_total'], 2)
        result['credit_total'] = round(result['credit_total'], 2)
        result['debit_balance'] = round(result['debit_balance'], 2)
        return result


