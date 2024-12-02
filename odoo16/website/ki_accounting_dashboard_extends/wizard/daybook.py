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

from datetime import date
from datetime import timedelta, datetime
from odoo import fields, models, api, _
import io
import json
from odoo.exceptions import AccessError, UserError, AccessDenied

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AgeingView(models.TransientModel):
    _inherit = 'account.day.book'


    def _get_account_move_entry(self, accounts, form_data,journals, pass_date):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        tables, where_clause, where_params = move_line._query_get()
        wheres = [""]
        companies = self.env.companies.ids
        companies.append(0)
        target_move = "AND l.company_id in %s" % str(tuple(companies))
        if where_clause.strip():
            wheres.append(where_clause.strip())
        if form_data['target_move'] == 'posted':
            target_move += " AND m.state = 'posted'"
        else:
            target_move += """AND m.state in ('draft','posted') """
        sql = ('''
                SELECT l.id AS lid,m.id AS move_id, acc.name as accname, l.account_id AS account_id,to_char(l.date, 'DD/MM/YYYY')AS ldate, j.code AS lcode, l.currency_id, 
                l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
                m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                JOIN account_account acc ON (l.account_id = acc.id) 
                WHERE l.account_id IN %s AND l.journal_id IN %s ''' + target_move + ''' AND l.date = %s
                GROUP BY l.id,m.id, l.account_id, l.date,
                     j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name , acc.name
                     ORDER BY l.date DESC
        ''')
        params = (
        tuple(accounts.ids), tuple(journals.ids), pass_date)
        cr.execute(sql, params)
        data = cr.dictfetchall()

        res = {}
        debit = credit = balance = 0.00
        id = ''
        for line in data:
            debit += line['debit']
            credit += line['credit']
            balance += line['balance']
            id = line['move_id']
        res['debit'] = debit
        res['credit'] = credit
        res['balance'] = balance
        res['lines'] = data
        res['move_id'] = id
        return res

