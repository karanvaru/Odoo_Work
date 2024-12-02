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


class PartnerView(models.TransientModel):
    _inherit = "account.partner.ledger"

    def _get_partners(self, partners, accounts, init_balance, display_account,
                      data, asset_receivable=None):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        move_lines = {x: [] for x in partners.ids}
        currency_id = self.env.company.currency_id
        account_list = {x.id: {'name': x.name, 'code': x.code} for x in
                        accounts}

        if data.get('date_from'):
            init_tables, init_where_clause, init_where_params = move_line.with_context(
                date_from=self.env.context.get('date_from'), date_to=False,
                initial_bal=True)._query_get()
            
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())

            init_filters = " AND ".join(init_wheres)
            init_filters = init_filters.replace('account_move_line__move_id','m').replace('account_move_line', 'l')

            new_init_filters = init_filters
            if data['target_move'] == 'posted':
                new_init_filters += " AND m.state = 'posted'"
            else:
                new_init_filters += " AND m.state in ('draft','posted')"
            if data.get('date_from'):
                new_init_filters += " AND l.date < '%s'" % data.get('date_from')
    
            if data['journals']:
                new_init_filters += ' AND j.id IN %s' % str(
                    tuple(data['journals'].ids) + tuple([0]))
            if data.get('accounts'):
                INIT_WHERE = "WHERE l.account_id IN %s" % str(
                    tuple(data.get('accounts').ids) + tuple([0]))
            else:
                INIT_WHERE = "WHERE l.account_id IN %s"
    
            if data.get('partners'):
                INIT_WHERE += ' AND p.id IN %s' % str(
                    tuple(data.get('partners').ids) + tuple([0]))
    
            if data.get('reconciled') == 'unreconciled':
                INIT_WHERE += ' AND l.full_reconcile_id is null AND' \
                         ' l.balance != 0 AND acc.reconcile is true'
    
            if data.get('account_type') == 'asset_receivable':
                INIT_WHERE += " AND acc.account_type = 'asset_receivable' "
    
            elif data.get('account_type') == 'liability_payable':
                INIT_WHERE += " AND acc.account_type = 'liability_payable' "
    
            init_sql = ('''SELECT '' AS lid,
                    l.partner_id AS partner_id,
                    '' AS move_id, 
                    '' AS account_id,
                    '' AS ldate, 
                    '' AS account_type,
                    '' AS lcode,
                    '' AS account_name,
                    20 AS currency_id,
                    'before' AS currency_position,
                    '' AS lref,
                    'Initial Balance' AS lname,
                    0 AS amount_currency,
                    COALESCE(SUM(l.debit),0.0) AS debit,
                    COALESCE(SUM(l.credit),0.0) AS credit, 
                    COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance,
                    '' AS move_name,
                    '₹' AS currency_code,
                    'Initial Balance' AS partner_name
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    JOIN account_account acc ON (l.account_id = acc.id)
                    ''' + INIT_WHERE + new_init_filters +
                   ''' GROUP BY l.partner_id
                    '''
                   )
            if data.get('accounts'):
                init_params = tuple(init_where_params)
            else:
                init_params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(init_sql, init_params)
            init_res = cr.dictfetchall()
            
            for i_res in init_res:
            
                if i_res['partner_id'] in move_lines:
                    move_lines[i_res['partner_id']] = [i_res]
        
        tables, where_clause, where_params = move_line._query_get()
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

        if data.get('partners'):
            WHERE += ' AND p.id IN %s' % str(
                tuple(data.get('partners').ids) + tuple([0]))

        if data.get('reconciled') == 'unreconciled':
            WHERE += ' AND l.full_reconcile_id is null AND' \
                     ' l.balance != 0 AND acc.reconcile is true'

        if data.get('account_type') == 'asset_receivable':
            WHERE += " AND acc.account_type = 'asset_receivable' "

        elif data.get('account_type') == 'liability_payable':
            WHERE += " AND acc.account_type = 'liability_payable' "

        sql = ('''SELECT l.id AS lid,l.partner_id AS partner_id,
                m.id AS move_id, 
                l.account_id AS account_id, to_char(l.date, 'DD/MM/YYYY')AS ldate, 
                acc.account_type AS account_type,
                j.code AS lcode, l.currency_id, 
                l.amount_currency, l.ref AS lref, l.name AS lname, 
                COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                COALESCE(SUM(l.balance),0) AS balance,
                m.name AS move_name, c.symbol AS currency_code,c.position
                AS currency_position, p.name AS partner_name
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                JOIN account_account acc ON (l.account_id = acc.id)
                ''' + WHERE + new_final_filter +
               ''' GROUP BY l.id, m.id,  
                l.account_id, l.date, j.code, l.currency_id, 
                l.amount_currency, l.ref, l.name, m.name, c.symbol, 
                c.position, p.name, acc.account_type ORDER BY l.date desc
                '''
               )
        if data.get('accounts'):
            params = tuple(where_params)
        else:
            params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)
        a=cr.dictfetchall()
        for row in a:
            balance = 0
            if row['partner_id'] in move_lines:
                for line in move_lines.get(row['partner_id']):
                    balance += round(line['debit'], 2) - round(line['credit'],
                                                               2)
                row['balance'] += (round(balance, 2))
                row['m_id'] = row['account_id']
                row['account_name'] = account_list[row['account_id']][
                                          'name'] + "(" + \
                                      account_list[row['account_id']][
                                          'code'] + ")"
                move_lines[row.pop('partner_id')].append(row)

        partner_res = []
        for partner in partners:
            company_id = self.env.company
            currency = company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['name'] = partner.name
            res['id'] = partner.id
            res['move_lines'] = move_lines[partner.id]
            for line in res.get('move_lines'):
                res['debit'] += round(line['debit'], 2)
                res['credit'] += round(line['credit'], 2)
                res['balance'] = round(line['balance'], 2)
            if display_account == 'all':
                partner_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                partner_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                partner_res.append(res)
        return partner_res

