# -*- coding: utf-8 -*-
from calendar import month

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import datetime
import calendar
import json
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class FundStatement(models.TransientModel):
    _inherit = 'fund.statement'


    def get_capex_cost_data(self, move_domain, cost_type, month_list):
        s_date = move_domain[1][2]
        e_date = move_domain[2][2]
        move_date_domain = [('move_id.state', '=', 'posted'),
                            ('move_id.date', '>=', s_date),
                            ('move_id.date', '<=', e_date), ]

        move_lines = self.env['account.move.line'].search(move_date_domain + [
            ('partner_id.report_head_type', '=', cost_type),
            ('account_id.account_type', 'in', ('asset_receivable', 'liability_payable')),
        ])
        move_lines_2 = self.env['account.move.line'].search(move_domain + [
            ('move_id.move_type', '=', 'in_invoice'),
            ('partner_id.report_head_type', '!=', cost_type),
            '|',
            #             ('account_id.report_head_type', '=', cost_type),
            ('product_id.report_head_type', '=', cost_type),
            ('product_id.categ_id.report_head_type', '=', cost_type),
        ])

        move_lines_exp = self.env['account.move.line'].search(move_date_domain + [
            ('expense_id', '!=', False),
            '|',
            ('product_id.report_head_type', '=', cost_type),
            ('product_id.categ_id.report_head_type', '=', cost_type),
        ])
        move_lines = move_lines + move_lines_2 + move_lines_exp

        move_lines_dct = {}
        capex_categ = self.env['capex.category'].search([('report_head_type', '=', cost_type)])
        capex_lst = []
        for capex in capex_categ:
            capex_dct = {}
            capex_dct['sequence'] = capex.sequence
            capex_dct['name'] = capex.name
            capex_lst.append(capex_dct)
        capex_sequence_data_sorted = sorted(capex_lst, key=lambda x: x['sequence'])
        for line in move_lines:
            if line.partner_id.report_head_type == cost_type:
                key = line.partner_id.capex_category_id or line.partner_id
            #             elif line.account_id.report_head_type == cost_type:
            #                 key = line.account_id
            elif line.product_id.categ_id.report_head_type == cost_type:
                key = line.product_id.capex_category_id
            else:
                key = line.product_id.capex_category_id
            #                 key = line.product_id.categ_id

            #             if not key:
            #                 if line.account_id.tag_ids:
            #                     key = line.account_id.tag_ids[0]
            #             if not key:
            #                 key = line.product_id.categ_id
            #             if not key:
            #                 key = line.account_id
            if key not in move_lines_dct:
                name = key.display_name
                move_lines_dct[key] = {'amount': 0.0, 'month': {}, 'name': name}
            for mo in month_list:
                if mo not in move_lines_dct[key]['month']:
                    move_lines_dct[key]['month'][mo] = {'amount': 0.0}
                if line.expense_id:
                    if mo == line.expense_id.date.strftime("%B-%Y"):
                        move_lines_dct[key]['month'][mo]['amount'] += round(abs(line.balance), 2)
                elif line.move_id.date:
                    if mo == line.move_id.date.strftime("%B-%Y"):
                        if line.price_total != 0:
                            move_lines_dct[key]['month'][mo]['amount'] += round(abs(line.price_total), 2)
                        else:
                            move_lines_dct[key]['month'][mo]['amount'] += round(abs(line.balance), 2)
            if line.price_total != 0:
                move_lines_dct[key]['amount'] += round(abs(line.price_total), 2)
            else:
                move_lines_dct[key]['amount'] += round(abs(line.balance), 2)
        final_dct = {}
        sum_total_dct = {'amount': 0.0}
        for mo in month_list:
            sum_total_dct[mo] = 0.0
        for account, details in move_lines_dct.items():
            sum_total_dct['amount'] += details['amount']
            for rec in details['month']:
                if rec not in sum_total_dct:
                    sum_total_dct[rec] = 0.0
                sum_total_dct[rec] += details['month'][rec]['amount']
        lines = []
        for account in move_lines_dct:
            a = move_lines_dct[account]
            a.update({
                'name': a.get('name', account.name),
                'id': account.id,
                'amount': self.formatINR(format(a['amount'], '.2f')),
                'month': {mo: {'amount': self.formatINR(format(details['amount'], '.2f'))} for mo, details in
                          a['month'].items()}
            })
            lines.append(a)

        sum_total_dct['amount'] = format(sum_total_dct['amount'], '.2f')
        for mo in month_list:
            sum_total_dct[mo] = format(sum_total_dct[mo], '.2f')

        final_dct['data'] = lines

        capex_ordered_data = []
        capex_sequence_names = {item['name'] for item in capex_sequence_data_sorted}
        for item in capex_sequence_data_sorted:
            dept = next((d for d in final_dct['data'] if d['name'] == item['name']), None)
            if dept:
                capex_ordered_data.append(dept)
        capex_unsequenced_data = [d for d in final_dct['data'] if d['name'] not in capex_sequence_names]
        capex_ordered_data.extend(capex_unsequenced_data)
        final_dct['data'] = capex_ordered_data
        final_dct['month_sum'] = sum_total_dct
        return final_dct
