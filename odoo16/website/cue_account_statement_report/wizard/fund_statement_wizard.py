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
    _inherit = "account.report"
    _name = 'fund.statement'

    def formatINR(self, number):
        number = str(round(float(number), 2))
        s, *d = str(number).partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        amt = "".join([r] + d)
        return amt

    @api.model
    def create(self, vals):
        vals['target_move'] = 'posted'
        vals['name'] = 'test'
        res = super(FundStatement, self).create(vals)
        return res

    @api.model
    def get_year_financial(self, start_date, end_date):
        date1 = start_date
        date2 = end_date
        date1 = date1.replace(day=1)
        date2 = date2.replace(day=1)
        months = []
        while date1 <= date2:
            month = date1.month
            year = date1.year
            next_month = month + 1 if month != 12 else 1
            next_year = year + 1 if next_month == 1 else year
            date_list = [date1]
            date1 = date1.replace(month=next_month, year=next_year)
            end_date = date1 - timedelta(days=1)
            months.append(end_date.strftime("%B-%Y"))
        return months

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
        for line in move_lines:
            if line.partner_id.report_head_type == cost_type:
                key = line.partner_id
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
        final_dct['month_sum'] = sum_total_dct
        return final_dct

    def get_cost_data(self, move_domain, cost_type, month_list):
        move_lines = self.env['account.move.line'].search(move_domain + [
            '|',
            ('account_id.report_head_type', '=', cost_type),
            ('product_id.report_head_type', '=', cost_type),
        ])
        move_lines_dct = {}
        capex_categ_cost_type = self.env['capex.category'].search([('report_head_type', '=', cost_type)])
        cost_type_capex_lst = []
        for capex_type in capex_categ_cost_type:
            cost_type_capex_dct = {}
            cost_type_capex_dct['sequence'] = capex_type.sequence
            cost_type_capex_dct['name'] = capex_type.name
            cost_type_capex_lst.append(cost_type_capex_dct)
        sequence_data_sorted_cost_type = sorted(cost_type_capex_lst, key=lambda x: x['sequence'])
        for line in move_lines:

            key = line.product_id.capex_category_id
            if not key:
                if line.account_id.tag_ids:
                    key = line.account_id.tag_ids[0]
            if not key:
                key = line.account_id
            if key not in move_lines_dct:
                name = key.name

                move_lines_dct[key] = {'amount': 0.0, 'month': {}, 'name': name}

            for mo in month_list:
                if mo not in move_lines_dct[key]['month']:
                    move_lines_dct[key]['month'][mo] = {'amount': 0.0}
                if line.move_id.date:
                    if mo == line.move_id.date.strftime("%B-%Y"):
                        if line.price_total != 0:
                            move_lines_dct[key]['month'][mo]['amount'] += round(abs(line.price_total), 2)
                        else:
                            move_lines_dct[key]['month'][mo]['amount'] += round(abs(line.balance), 2)
            if line.price_total != 0:
                move_lines_dct[key]['amount'] += round(abs(line.price_total), 2)
            else:
                move_lines_dct[key]['amount'] += round(abs(line.balance), 2)
        if cost_type == 'overhead_cost':
            if self._context.get('start_date', False):
                move_domain = [
                    ('move_id.state', '=', 'posted'),
                    ('move_id.date', '>=', self._context.get('start_date', False)),
                    ('move_id.date', '<=', self._context.get('end_date', False))
                ]

            payment_line = self.env['account.payment'].search(move_domain + [
                ('is_internal_transfer', '=', False),
                ('payment_type', '=', 'outbound'),
                ('partner_id.report_head_type', '=', cost_type)
            ])

            for pline in payment_line:
                key = pline.partner_id.capex_category_id
                if not key:
                    key = pline.partner_id

                if key not in move_lines_dct:
                    name = key.name
                    move_lines_dct[key] = {'amount': 0.0, 'month': {}, 'name': name}
                for mo in month_list:
                    if mo not in move_lines_dct[key]['month']:
                        move_lines_dct[key]['month'][mo] = {'amount': 0.0}
                    if pline.move_id.date:
                        if mo == pline.move_id.date.strftime("%B-%Y"):
                            move_lines_dct[key]['month'][mo]['amount'] += round(abs(pline.amount), 2)
                move_lines_dct[key]['amount'] += round(abs(pline.amount), 2)
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
        cost_type_ordered_data = []
        cost_type_sequence_names = {item['name'] for item in sequence_data_sorted_cost_type}
        for item in sequence_data_sorted_cost_type:
            dept = next((d for d in final_dct['data'] if d['name'] == item['name']), None)
            if dept:
                cost_type_ordered_data.append(dept)
        unsequenced_data_cost_type = [d for d in final_dct['data'] if d['name'] not in cost_type_sequence_names]
        cost_type_ordered_data.extend(unsequenced_data_cost_type)
        final_dct['data'] = cost_type_ordered_data
        final_dct['month_sum'] = sum_total_dct
        return final_dct

    def get_wages_data(self, month_list, start_date, end_date):
        wages_final_dct = {}
        departments = self.env['hr.employee'].with_context(active_test=False).search([]).mapped('department_id')
        department_dict = {}

        capex_categ = self.env['capex.category'].search([('report_head_type', '=', 'wages_cost')])
        capex_lst = []
        for capex in capex_categ:
            capex_dct = {}
            capex_dct['sequence'] = capex.sequence
            capex_dct['name'] = capex.name
            capex_lst.append(capex_dct)
        sequence_data_sorted = sorted(capex_lst, key=lambda x: x['sequence'])
        for dept in departments:
            department_dict[dept.id] = {'name': dept.name, 'amount': 0.0, 'dept_id': dept.id, 'month': {}}
            payslip_lines = self.env['hr.payslip.line'].search([
                ('slip_id.date', '>=', start_date),
                ('slip_id.date', '<=', end_date),
                ('slip_id.state', 'in', ['done', 'paid']),
                ('employee_id.department_id', '=', dept.id),
                ('code', '=', 'NET')
            ])

            if payslip_lines:
                for salary_amount in payslip_lines:
                    department_dict[dept.id]['amount'] += salary_amount.total
                    for mo in month_list:
                        if mo not in department_dict[dept.id]['month']:
                            department_dict[dept.id]['month'][mo] = {'amount': 0.0}
                        if salary_amount.slip_id.date:
                            if mo == salary_amount.slip_id.date.strftime("%B-%Y"):
                                department_dict[dept.id]['month'][mo]['amount'] += salary_amount.total

            salary_move_lines = self.env['account.move.line'].search([
                ('move_id.date', '>=', start_date),
                ('move_id.date', '<=', end_date),
                ('move_id.state', '=', 'posted'),
                ('capex_category_id.department_id', '=', dept.id),
            ])
            if salary_move_lines:
                for move_line in salary_move_lines:
                    department_dict[dept.id]['amount'] += abs(move_line.balance)
                    for mo in month_list:
                        if mo not in department_dict[dept.id]['month']:
                            department_dict[dept.id]['month'][mo] = {'amount': 0.0}
                        if move_line.move_id.date:
                            if mo == move_line.move_id.date.strftime("%B-%Y"):
                                department_dict[dept.id]['month'][mo]['amount'] += abs(move_line.balance)

        lines = []
        month_total_salary = {}

        for dept in department_dict:
            lines.append(department_dict[dept])

        month_total_salary['amount'] = 0.0
        for month in month_list:
            month_total_salary[month] = 0.0

        for product, details in department_dict.items():
            month_total_salary['amount'] += round(details['amount'], 2)
            for rec in details['month']:
                if rec not in month_total_salary:
                    month_total_salary[rec] = 0.0
                month_total_salary[rec] += details['month'][rec]['amount']

        wages_final_dct['data'] = [{**dept, 'amount': self.formatINR(format(dept['amount'], '.2f')),
                                    'month': {mo: {'amount': self.formatINR(format(details['amount'], '.2f'))} for
                                              mo, details in
                                              dept['month'].items()}} for dept in lines]
        month_total_salary['amount'] = format(month_total_salary['amount'], '.2f')
        ordered_data = []
        sequence_names = {item['name'] for item in sequence_data_sorted}
        for item in sequence_data_sorted:
            dept = next((d for d in wages_final_dct['data'] if d['name'] == item['name']), None)
            if dept:
                ordered_data.append(dept)
        for month in month_list:
            month_total_salary[month] = format(month_total_salary[month], '.2f')
        unsequenced_data = [d for d in wages_final_dct['data'] if d['name'] not in sequence_names]
        ordered_data.extend(unsequenced_data)
        wages_final_dct['month_sum'] = month_total_salary
        wages_final_dct['data'] = ordered_data
        return wages_final_dct

    def convert_amount(self, amount):
        if isinstance(amount, str):
            amount = amount.replace(',', '')
            return float(amount)
        return amount

    def calculate_totals(self, move_type, payment_type, date_field, start_date):
        invoices = self.env['account.move'].search([
            ('move_type', '=', move_type), (date_field, '<', start_date)])
        payments = self.env['account.payment'].search([
            ('payment_type', '=', payment_type), (date_field, '<', start_date)])
        return sum(invoices.mapped('amount_total')), sum(payments.mapped('amount'))

    def read_group_data(self, model, domain, fields, group_by):
        return self.env[model].read_group(domain, fields, group_by)

    def get_working_capital_data(self, month_list, start_date, end_date):
        carried_forward_amount_total = 0.0
        payable_carried_forward_amount_total = 0.0
        invoice_sum = sum(self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'in_refund']),
            ('state', '=', 'posted'),
            ('invoice_date', '<', start_date)
        ]).mapped('amount_total'))

        payment_sum = sum(self.env['account.payment'].search([
            ('is_internal_transfer', '=', False),
            ('payment_type', '=', 'inbound'),
            ('date', '<', start_date),
            ('state', '=', 'posted'),
            ('partner_id.report_head_type', 'not in', ['exclude_fs', 'exclude_fs_revenue_in'])
        ]).mapped('amount_company_currency_signed'))
        #         invoice_sum, payment_sum = self.calculate_totals('out_invoice', 'inbound', 'invoice_date', start_date)
        #         payable_invoice_sum, payable_payment_sum = self.calculate_totals('in_invoice', 'outbound', 'invoice_date',
        #                                                                          start_date)
        payable_invoice_sum = sum(self.env['account.move'].search([
            ('move_type', 'in', ['in_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('invoice_date', '<', start_date)
        ]).mapped('amount_total'))

        payable_payment_sum = sum(self.env['account.payment'].search([
            ('is_internal_transfer', '=', False),
            ('payment_type', '=', 'outbound'),
            ('date', '<', start_date),
            ('state', '=', 'posted'),
            ('partner_id.report_head_type', 'not in', ['exclude_fs', 'exclude_fs_revenue_in'])
        ]).mapped('amount_company_currency_signed'))

        receivable_carried_forward = invoice_sum - payment_sum
        payable_carried_forward = payable_invoice_sum - payable_payment_sum

        carried_forward_amount_total += receivable_carried_forward
        payable_carried_forward_amount_total += payable_carried_forward
        month_dct = {}
        symbol = self.env.company.currency_id.symbol,
        change_in_accounts_receivables_inner_data = {
            'carried_forward': {
                'amount': 0.0,
                'name': 'Carried Forward',
                'month': {}
            },
            'new': {
                'amount': 0.0,
                'name': 'New',
                'month': {},
            },
            'received': {
                'amount': 0.0,
                'name': 'Received',
                'month': {}
            },
            'closing': {
                'amount': 0.0,
                'name': 'Closing',
                'month': {}
            },
        }
        change_in_accounts_payable_inner_data = {
            'carried_forward': {
                'amount': 0.0,
                'name': 'Carried Forward',
                'month': {}
            },
            'new': {
                'amount': 0.0,
                'name': 'New',
                'month': {}
            },
            'paid': {
                'amount': 0.0,
                'name': 'Paid',
                'month': {}
            },
            'closing': {
                'amount': 0.0,
                'name': 'Closing',
                'month': {}
            },
        }
        change_in_inventory_inner_data = {
            'inventory_at_hand': {
                'amount': 0.0,
                'name': 'Inventory At Hand',
                'month': {},
            },
            'inventories_in': {
                'amount': 0.0,
                'name': 'Inventories In',
                'month': {},
            },
            'inventory_out': {
                'amount': 0.0,
                'name': 'Inventory Out',
                'month': {},
            },
            'stock_in_hand': {
                'amount': 0.0,
                'name': 'Stock In Hand',
                'month': {},
            },
        }

        working_capital = {
            'change_in_accounts_receivables': {
                'amount': 0,
                'symbol': symbol,
                'name': 'Change in Accounts Receivables',
                'inner_data': [change_in_accounts_receivables_inner_data]
            },
            'change_in_accounts_payable': {
                'amount': 0,
                'symbol': symbol,
                'name': 'Change In Accounts Payable',
                'inner_data': [change_in_accounts_payable_inner_data]
            },
            'change_in_Inventory': {
                'amount': 0.0,
                'symbol': symbol,
                'name': 'Change in Inventory',
                'inner_data': [change_in_inventory_inner_data]
            },
        }
        working_data_dct = {}
        working_data_month_total = {}
        working_data_month_total['amount'] = 0.0
        lines = []

        for product in working_capital:
            a = working_capital[product]
            working_capital[product]['month'] = {}
            for month_data in month_list:
                month_dct.update({month_data: {'amount': 0.0}})
                for inner_month in change_in_accounts_receivables_inner_data:
                    change_in_accounts_receivables_inner_data[inner_month]['month'].update(
                        {month_data: {'amount': 0.0}})
                for inner_month in change_in_accounts_payable_inner_data:
                    change_in_accounts_payable_inner_data[inner_month]['month'].update(
                        {month_data: {'amount': 0.0}})
                for inner_month in change_in_inventory_inner_data:
                    change_in_inventory_inner_data[inner_month]['month'].update(
                        {month_data: {'amount': 0.0}})
                for month in month_list:
                    working_data_month_total[month] = 0.0

                working_capital[product]['month'].update({month_data: {'amount': 0.0}})
            a.update({
                'name': a['name'],
                'id': product,
                'amount': self.formatINR(format(a['amount'], '.2f')),
            })
            lines.append(a)

        first_month = change_in_accounts_receivables_inner_data['carried_forward']['month'][
            start_date.strftime("%B-%Y")]
        first_month['amount'] = self.formatINR(format(receivable_carried_forward, '.2f'))

        payable_first_month = change_in_accounts_payable_inner_data['carried_forward']['month'][
            start_date.strftime("%B-%Y")]
        payable_first_month['amount'] = self.formatINR(format(payable_carried_forward_amount_total, '.2f'))

        invoice_data = self.read_group_data(
            'account.move',
            [
                ('move_type', 'in', ['out_invoice', 'in_refund']),
                ('state', '=', 'posted')
            ],
            ['amount_total', 'invoice_date'], ['invoice_date']
        )
        payment_data = self.read_group_data(
            'account.payment',
            [
                ('payment_type', '=', 'inbound'),
                #                 ('partner_type', '=', 'customer'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('partner_id.report_head_type', 'not in', ['exclude_fs', 'exclude_fs_revenue_in'])
            ],
            ['amount', 'date'],
            ['date']
        )

        new_amount_total = 0.0
        new_amount_total_payable = 0.0
        received_amount_total = 0.0
        paid_amount_total_payable = 0.0
        close_amount_total = 0.0
        payable_close_amount_total = 0.0
        for invoice in invoice_data:
            if invoice['invoice_date'] != False:
                formatted_date = invoice['invoice_date'].replace(" ", "-")
                if formatted_date in change_in_accounts_receivables_inner_data['new']['month']:
                    change_in_accounts_receivables_inner_data['new']['month'][formatted_date]
                    change_in_accounts_receivables_inner_data['new']['month'][formatted_date]['amount'] = invoice[
                        'amount_total']
                    new_amount_total += invoice['amount_total']
        change_in_accounts_receivables_inner_data['new']['amount'] = self.formatINR(format(new_amount_total, '.2f'))
        for payment in payment_data:
            if payment['date'] != False:
                formatted_date = payment['date'].replace(" ", "-")
                if formatted_date in change_in_accounts_receivables_inner_data['received']['month']:
                    change_in_accounts_receivables_inner_data['received']['month'][formatted_date]['amount'] = \
                        payment['amount']
                    received_amount_total += payment['amount']
        change_in_accounts_receivables_inner_data['received']['amount'] = self.formatINR(
            format(received_amount_total, '.2f'))

        for close_data in change_in_accounts_receivables_inner_data['closing']['month']:
            invoice = change_in_accounts_receivables_inner_data['new']['month'][close_data]
            payment = change_in_accounts_receivables_inner_data['received']['month'][close_data]
            carried_forward = change_in_accounts_receivables_inner_data['carried_forward']['month'][close_data]

            if type(carried_forward['amount']) != float:
                cleaned_str = carried_forward['amount'].replace(',', '')
                value = float(cleaned_str)
            else:
                value = carried_forward['amount']
            close_amount = value + invoice['amount'] - payment['amount']
            month_name, year = close_data.split('-')
            month_number = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            date_object = datetime.datetime(int(year), month_number[month_name], 1)
            next_month_date = date_object + relativedelta(months=1)
            next_month_name = next_month_date.strftime("%B-%Y")
            if next_month_name in change_in_accounts_receivables_inner_data['carried_forward']['month']:
                change_in_accounts_receivables_inner_data['carried_forward']['month'][next_month_name][
                    'amount'] = self.formatINR(
                    format(close_amount, '.2f'))
                carried_forward_amount_total += close_amount
            close_amount_total += close_amount
            change_in_accounts_receivables_inner_data['closing']['month'][close_data]['amount'] = self.formatINR(
                format(close_amount, '.2f'))
            change_in_accounts_receivables_inner_data['closing']['amount'] = self.formatINR(
                format(close_amount_total, '.2f'))
            change_in_accounts_receivables_inner_data['carried_forward']['amount'] = self.formatINR(
                format(float(carried_forward_amount_total), '.2f'))

        payable_invoice_data = self.read_group_data(
            'account.move',
            [
                ('move_type', 'in', ['in_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ],
            [
                'amount_total',
                'invoice_date'
            ],
            ['invoice_date']
        )
        payable_payment_data = self.read_group_data(
            'account.payment',
            [
                ('payment_type', '=', 'outbound'),
                #                 ('partner_type', '=', 'supplier'),
                ('state', '=', 'posted'),
                ('is_internal_transfer', '=', False),
                ('partner_id.report_head_type', 'not in', ['exclude_fs', 'exclude_fs_revenue_in'])
            ],
            [
                'amount',
                'date'
            ],
            ['date']
        )
        for invoice_payable in payable_invoice_data:
            if invoice_payable['invoice_date'] != False:
                formatted_date = invoice_payable['invoice_date'].replace(" ", "-")
                if formatted_date in change_in_accounts_payable_inner_data['new']['month']:
                    change_in_accounts_payable_inner_data['new']['month'][formatted_date]
                    change_in_accounts_payable_inner_data['new']['month'][formatted_date]['amount'] = abs(
                        invoice_payable[
                            'amount_total'])
                    new_amount_total_payable += abs(invoice_payable['amount_total'])
        change_in_accounts_payable_inner_data['new']['amount'] = self.formatINR(format(new_amount_total_payable, '.2f'))

        for payment_payable in payable_payment_data:
            if payment_payable['date'] != False:
                formatted_date = payment_payable['date'].replace(" ", "-")
                if formatted_date in change_in_accounts_payable_inner_data['paid']['month']:
                    change_in_accounts_payable_inner_data['paid']['month'][formatted_date]['amount'] = \
                        payment_payable['amount']
                    paid_amount_total_payable += payment_payable['amount']
        change_in_accounts_payable_inner_data['paid']['amount'] = self.formatINR(
            format(paid_amount_total_payable, '.2f'))

        for close_data_payable in change_in_accounts_payable_inner_data['closing']['month']:
            payable_invoice = change_in_accounts_payable_inner_data['new']['month'][close_data_payable]
            payable_payment = change_in_accounts_payable_inner_data['paid']['month'][close_data_payable]
            carried_forward = change_in_accounts_payable_inner_data['carried_forward']['month'][close_data_payable]

            if type(carried_forward['amount']) != float:
                cleaned_str = carried_forward['amount'].replace(',', '')
                value = float(cleaned_str)
            else:
                value = carried_forward['amount']
            payable_close_amount = value + payable_invoice['amount'] - payable_payment['amount']
            month_name, year = close_data_payable.split('-')
            month_number = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            date_object = datetime.datetime(int(year), month_number[month_name], 1)
            next_month_date = date_object + relativedelta(months=1)
            next_month_name = next_month_date.strftime("%B-%Y")
            if next_month_name in change_in_accounts_payable_inner_data['carried_forward']['month']:
                change_in_accounts_payable_inner_data['carried_forward']['month'][next_month_name][
                    'amount'] = self.formatINR(
                    format(payable_close_amount, '.2f'))
                payable_carried_forward_amount_total += payable_close_amount
            payable_close_amount_total += payable_close_amount
            change_in_accounts_payable_inner_data['closing']['month'][close_data_payable]['amount'] = self.formatINR(
                format(payable_close_amount, '.2f'))
            change_in_accounts_payable_inner_data['closing']['amount'] = self.formatINR(
                format(payable_close_amount_total, '.2f'))
            change_in_accounts_payable_inner_data['carried_forward']['amount'] = self.formatINR(
                format(float(payable_carried_forward_amount_total), '.2f'))

        #         domain = [('report_revenue_type', 'in', ['1_cue_bridge', '2_cue_bridge_max', '3_cue_bridge_plus'])]
        domain = [('report_head_type', '=', 'working_capital_in')]

        product = self.env['product.product'].sudo().search(domain)
        #         bill_of_materials = product.mapped('bom_ids')
        #         raw_material_product_ids = bill_of_materials.mapped('bom_line_ids').mapped('product_id')

        raw_material_product_ids = product

        #         purchase_order_lines = self.env['purchase.order.line'].sudo().search([
        #             ('product_id', 'in', raw_material_product_ids.ids),
        #             ('order_id.date_order', '>=', start_date),
        #             ('order_id.date_order', '<=', end_date)
        #         ])

        purchase_order_lines = self.env['account.move.line'].sudo().search([
            ('product_id', 'in', raw_material_product_ids.ids),
            ('move_id.invoice_date', '>=', start_date),
            ('move_id.invoice_date', '<=', end_date),
            ('move_id.move_type', '=', 'in_invoice'),
            ('move_id.state', '=', 'posted'),
        ])

        for purchase in purchase_order_lines:
            change_in_inventory_inner_data['inventories_in']['amount'] += purchase.price_total
            for purchase_month in month_list:
                if purchase_month not in change_in_inventory_inner_data['inventories_in']['month']:
                    change_in_inventory_inner_data['inventories_in']['month'][purchase_month] = {'amount': 0.0}
            change_in_inventory_inner_data['inventories_in']['month'][
                purchase.move_id.invoice_date.strftime("%B-%Y")][
                'amount'] += purchase.price_total

        sum_amount = self.get_direct_cost_data(start_date, end_date, product, month_list)
        change_in_inventory_inner_data['inventory_out']['month'] = {}
        for month_amt in sum_amount['month_sum']:
            change_in_inventory_inner_data['inventory_out']['amount'] = self.formatINR(
                format(float(sum_amount['month_sum']['amount']), '.2f'))

            if month_amt != 'amount':
                change_in_inventory_inner_data['inventory_out']['month'][month_amt] = {'amount': self.formatINR(
                    format(float(sum_amount['month_sum'][month_amt]), '.2f'))}

        date1 = start_date
        date2 = end_date
        date1 = fields.Date.from_string(date1) if isinstance(date1, str) else date1
        date2 = fields.Date.from_string(date2) if isinstance(date2, str) else date2

        date1 = date1.replace(day=1)
        date2 = date2.replace(day=1)
        months = []
        while date1 <= date2:
            month = date1.month
            year = date1.year
            next_month = month + 1 if month != 12 else 1
            next_year = year + 1 if next_month == 1 else year
            date_list = [date1]
            date1 = date1.replace(month=next_month, year=next_year)
            end_date = date1 - timedelta(days=1)
            date_list.append(end_date)
            months.append(date_list)
        for rec in product:
            for product_month in months:
                qty_on_hand = rec.with_context(from_date=product_month[0],
                                               to_date=product_month[1]).qty_available * rec.list_price
                # if product_month[0].strftime("%B-%Y") not in change_in_inventory_inner_data['stock_in_hand']['month']:
                #     change_in_inventory_inner_data['stock_in_hand']['month'].update({
                #         product_month[0].strftime("%B-%Y"): {'amount': qty_on_hand}
                #     })
                # else:
                change_in_inventory_inner_data['stock_in_hand']['month'][product_month[0].strftime("%B-%Y")][
                    'amount'] += qty_on_hand
                change_in_inventory_inner_data['stock_in_hand']['amount'] += qty_on_hand
        i = 1
        for month_name, details in change_in_inventory_inner_data['stock_in_hand']['month'].items():
            if i == 1:
                if month_name not in change_in_inventory_inner_data['inventory_at_hand']['month']:
                    change_in_inventory_inner_data['inventory_at_hand']['month'][month_name] = {'amount': 0}
                change_in_inventory_inner_data['inventory_at_hand']['month'][month_name]['amount'] += details['amount']
                change_in_inventory_inner_data['inventory_at_hand']['amount'] += details['amount']
                i += 1
            month_name, year = month_name.split('-')
            month_number = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            date_object = datetime.datetime(int(year), month_number[month_name], 1)
            next_month_date = date_object + relativedelta(months=1)
            next_month_name = next_month_date.strftime("%B-%Y")
            last_month_name, year = next_month_name.split('-')

            last_date_object = datetime.datetime(int(year), month_number[last_month_name], 1)
            if last_date_object.date() <= end_date:
                if next_month_name not in change_in_inventory_inner_data['inventory_at_hand']['month']:
                    change_in_inventory_inner_data['inventory_at_hand']['month'][next_month_name] = {'amount': 0}
                change_in_inventory_inner_data['inventory_at_hand']['month'][next_month_name]['amount'] += details[
                    'amount']
                change_in_inventory_inner_data['inventory_at_hand']['amount'] += details['amount']
        for key, capital_data in working_capital.items():
            sum_amount = 0.0
            month_totals = {}
            for item in capital_data['inner_data']:
                keys = list(item.keys())
                first_key = keys[0]
                last_key = keys[-1]
                first_key_amount = 0
                last_key_amount = 0
                if isinstance(item[first_key]['amount'], str):
                    cleaned_str = item[first_key]['amount'].replace(',', '')
                    first_key_amount = float(cleaned_str)
                else:
                    first_key_amount = item[first_key]['amount']

                if isinstance(item[last_key]['amount'], str):
                    cleaned_str = item[last_key]['amount'].replace(',', '')
                    last_key_amount = float(cleaned_str)
                else:
                    last_key_amount = item[last_key]['amount']
                sum_amount = last_key_amount - first_key_amount
                first_amount_list = []
                last_amount_list = []
                for first in item[first_key]['month']:
                    first_amount_dct = {}
                    first_amount_dct.update({
                        first: item[first_key]['month'][first]['amount']
                    })
                    first_amount_list.append(first_amount_dct)

                for last in item[last_key]['month']:
                    last_amount_dct = {}
                    last_amount_dct.update({
                        last: item[last_key]['month'][last]['amount']
                    })
                    last_amount_list.append(last_amount_dct)
                for i in range(len(first_amount_list)):
                    month = list(first_amount_list[i].keys())[0]  # Get the month name (same for both lists)
                    first_amount = self.convert_amount(first_amount_list[i][month])
                    last_amount = self.convert_amount(last_amount_list[i][month])

                    difference = last_amount - first_amount
                    month_totals[month] = difference

            for rec in month_totals:
                month_totals[rec] = self.formatINR(format(month_totals[rec], '.2f'))
            working_capital[key]['month'] = month_totals
            working_capital[key]['amount'] = self.formatINR(format(sum_amount, '.2f'))

        for month_sum in working_capital:
            sum_amount = 0.0
            if isinstance(working_capital[month_sum]['amount'], str):
                cleaned_str = working_capital[month_sum]['amount'].replace(',', '')
                sum_amount += float(cleaned_str)
            working_data_month_total['amount'] += sum_amount
            for count in working_capital[month_sum]['month']:
                if isinstance(working_capital[month_sum]['month'][count], str):
                    cleaned_str = working_capital[month_sum]['month'][count].replace(',', '')
                    working_data_month_total[count] += float(cleaned_str)

        working_data_dct['data'] = lines
        working_data_dct['month_sum'] = working_data_month_total
        return working_data_dct

    def get_cash_flow_data(self, month_list, start_date, end_date):
        move_domain = [('move_id.state', '=', 'posted'),
                       ('move_id.date', '>=', start_date),
                       ('move_id.date', '<=', end_date), ]
        cash_flow_statement = {
            'cash_flow_from_operating_activities': {
                'amount': 0.0,
                'name': 'Cash Flow from Operating Activities',
            },
            'net_income': {
                'amount': 0.0,
                'name': 'Net Income',
            },
            'depreciation_and_mortisation': {
                'amount': 0.0,
                'name': 'Depreciation & Amortisation ( + )',
            },
            'net_accounts_receivable': {
                'amount': 0.0,
                'name': 'Net Accounts Receivable ( + )',
            },
            'capital_exp': {
                'amount': 0.0,
                'name': 'Capital Exp. ( - )',
            },
        }
        working_data_sum = self.get_working_capital_data(month_list, start_date, end_date)
        cash_flow_statement['net_accounts_receivable']['month'] = {}
        for month_amt in working_data_sum['month_sum']:
            cash_flow_statement['net_accounts_receivable']['amount'] = working_data_sum['month_sum']['amount']
            if month_amt != 'amount':
                cash_flow_statement['net_accounts_receivable']['month'][month_amt] = {
                    'amount': working_data_sum['month_sum'][month_amt]}

        #         capex_cost_data = self.get_cost_data(move_domain, 'capex', month_list)
        capex_cost_data = self.get_capex_cost_data(move_domain, 'capex', month_list)
        cash_flow_statement['capital_exp']['month'] = {}
        for capex_amt in capex_cost_data['month_sum']:
            cash_flow_statement['capital_exp']['amount'] = float(capex_cost_data['month_sum']['amount'])
            if capex_amt != 'amount':
                cash_flow_statement['capital_exp']['month'][capex_amt] = {
                    'amount': capex_cost_data['month_sum'][capex_amt]}

        net_income_data = self.get_net_income_data(month_list, start_date, end_date)
        cash_flow_statement['net_income']['month'] = {}
        for net_amt in net_income_data['month_sum']:
            cash_flow_statement['net_income']['amount'] = float(net_income_data['month_sum']['amount'])
            if net_amt != 'amount':
                cash_flow_statement['net_income']['month'][net_amt] = {
                    'amount': net_income_data['month_sum'][net_amt]}

        for dct in cash_flow_statement:
            if dct not in ['capital_exp', 'net_income', 'net_accounts_receivable']:  # net_accounts_receivable
                cash_flow_statement[dct]['month'] = {}
                for month in month_list:
                    cash_flow_statement[dct]['month'].update({month: {'amount': 0.0}})
        month_total_cash_flow = {}
        cash_flow_data_dct = {}
        month_total_cash_flow['amount'] = 0.0
        for month in month_list:
            month_total_cash_flow[month] = 0.0
        for product, details in cash_flow_statement.items():

            # month_total_cash_flow['amount'] += round(details['amount'], 2)
            for rec in details['month']:
                if rec not in month_total_cash_flow:
                    month_total_cash_flow[rec] = 0.0
                month_total_cash_flow['amount'] += round(float(details['month'][rec]['amount']), 2)
                month_total_cash_flow[rec] += float(details['month'][rec]['amount'])
        lines = []
        for product in cash_flow_statement:
            a = cash_flow_statement[product]
            a.update({
                'name': a['name'],
                'id': product,
                'amount': self.formatINR(format(a['amount'], '.2f')),
                'month': {mo: {'amount': self.formatINR(format(float(details['amount']), '.2f'))} for
                          mo, details in
                          a['month'].items()}
            })
            lines.append(a)
        cash_flow_data_dct['data'] = lines
        cash_flow_data_dct['month_sum'] = month_total_cash_flow
        return cash_flow_data_dct

    def get_cash_flow_activities_data(self, month_list, start_date, end_date):
        cash_flow_activity_statement = {
            'founder_equity': {
                'amount': 0.0,
                'name': 'Founder Equity',
            },
            'investors_equity': {
                'amount': 0.0,
                'name': 'Investors Equity',
            }
        }
        for dct in cash_flow_activity_statement:
            cash_flow_activity_statement[dct]['month'] = {}
            for month in month_list:
                cash_flow_activity_statement[dct]['month'].update({month: {'amount': 0.0}})

        month_total_cash_flow_activity = {}
        cash_flow_data_dct_activity = {}
        month_total_cash_flow_activity['amount'] = 0.0
        for month in month_list:
            month_total_cash_flow_activity[month] = 0.0
        for product, details in cash_flow_activity_statement.items():
            month_total_cash_flow_activity['amount'] += round(details['amount'], 2)
            for rec in details['month']:
                if rec not in month_total_cash_flow_activity:
                    month_total_cash_flow_activity[rec] = 0.0
                month_total_cash_flow_activity['amount'] += round(details['month'][rec]['amount'], 2)
                month_total_cash_flow_activity[rec] += details['month'][rec]['amount']

        lines = []
        for product in cash_flow_activity_statement:
            a = cash_flow_activity_statement[product]
            a.update({
                'name': a['name'],
                'id': product,
                'amount': self.formatINR(format(a['amount'], '.2f')),
                'month': {mo: {'amount': self.formatINR(format(details['amount'], '.2f'))} for
                          mo, details in
                          a['month'].items()}
            })
            lines.append(a)
        cash_flow_data_dct_activity['data'] = lines
        cash_flow_data_dct_activity['month_sum'] = month_total_cash_flow_activity
        return cash_flow_data_dct_activity

    def get_net_income_data(self, month_list, start_date, end_date):
        net_income_data = {
            'EBIT': {
                'amount': 0.0,
                'name': 'EBIT',
            },
            'interest_payments': {
                'amount': 0.0,
                'name': 'Interest Payments',
            },
            'tax_payments': {
                'amount': 0.0,
                'name': 'Tax Payments',
            }
        }
        domain = [('report_revenue_type', 'in', ['1_cue_bridge', '2_cue_bridge_max', '3_cue_bridge_plus'])]
        #         product = self.env['product.product'].sudo().search([('name', 'in', p_name)])
        product = self.env['product.product'].sudo().search(domain)

        move_domain = [('move_id.state', '=', 'posted'),
                       ('move_id.date', '>=', start_date),
                       ('move_id.date', '<=', end_date), ]
        move_lines = self.env['account.move.line'].search(move_domain + [
            ('move_id.move_type', '=', 'out_invoice'),
            ('product_id', 'in', product.ids),
        ])
        product_dct = self.get_revanue_data(start_date, end_date, product, month_list, move_lines)
        sum_amount = self.get_direct_cost_data(start_date, end_date, product, month_list)
        capex_cost_final_dct = self.get_cost_data(move_domain, 'capex', month_list)
        overhead_cost_final_dct = self.with_context(start_date=start_date, end_date=end_date).get_cost_data(move_domain,
                                                                                                            'overhead_cost',
                                                                                                            month_list)
        variable_cost_final_dct = self.get_cost_data(move_domain, 'variable_cost', month_list)
        wages_final_dct = self.get_wages_data(month_list, start_date, end_date)
        data_lst = [product_dct['month_sum'], sum_amount['month_sum'], capex_cost_final_dct['month_sum'],
                    overhead_cost_final_dct['month_sum'], variable_cost_final_dct['month_sum'],
                    wages_final_dct['month_sum']]
        net_income_data['EBIT']['month'] = {}
        for rec in data_lst:
            net_income_data['EBIT']['amount'] += float(rec['amount'])
            for income in rec:
                if income != 'amount':
                    if income not in net_income_data['EBIT']['month']:
                        net_income_data['EBIT']['month'][income] = {'amount': 0.0}
                    net_income_data['EBIT']['month'][income]['amount'] += round(float(rec[income]), 2)

        for dct in net_income_data:
            if dct != 'EBIT':
                net_income_data[dct]['month'] = {}
                for month in month_list:
                    net_income_data[dct]['month'].update({month: {'amount': 0.0}})
        net_income_data_final_dct = {}
        month_total_net_income = {}
        month_total_net_income['amount'] = 0.0
        for month in month_list:
            month_total_net_income[month] = 0.0
        for product, details in net_income_data.items():
            if details['name'] == 'EBIT':
                month_total_net_income['amount'] = round(details['amount'], 2)
            else:
                month_total_net_income['amount'] -= round(details['amount'], 2)
            for rec in details['month']:
                if details['name'] == 'EBIT':
                    month_total_net_income[rec] = details['month'][rec]['amount']
                else:
                    month_total_net_income[rec] -= details['month'][rec]['amount']

        lines = []
        for product in net_income_data:
            a = net_income_data[product]
            a.update({
                'name': a['name'],
                'id': product,
                'amount': self.formatINR(format(a['amount'], '.2f')),
                'month': {mo: {'amount': self.formatINR(format(float(details['amount']), '.2f'))} for
                          mo, details in
                          a['month'].items()}
            })
            lines.append(a)
        net_income_data_final_dct['data'] = lines
        net_income_data_final_dct['month_sum'] = month_total_net_income
        return net_income_data_final_dct

    def get_net_cash_flow_from_investing_activities_data(self, month_list, start_date, end_date):
        net_cash_flow_investing_activities = {
            'cash_flow_from_financing_activities': {
                'amount': 0.0,
                'name': 'Cash Flow from Financing Activities',
            },
            'debt': {
                'amount': 0.0,
                'name': 'Debt',
            },

            'old_debt': {
                'amount': 0.0,
                'name': 'Old Debt',
            },
            'directors_salary_accrued': {
                'amount': 0.0,
                'name': 'Director’s Salary ( Accrued )',
            },
            'new_debt': {
                'amount': 0.0,
                'name': 'New Debt',
            },
        }
        for dct in net_cash_flow_investing_activities:
            net_cash_flow_investing_activities[dct]['month'] = {}
            for month in month_list:
                net_cash_flow_investing_activities[dct]['month'].update({month: {'amount': 0.0}})

        month_total_net_cash_flow_investing_activity = {}
        net_cash_flow_investing_data_dct = {}
        month_total_net_cash_flow_investing_activity['amount'] = 0.0
        for month in month_list:
            month_total_net_cash_flow_investing_activity[month] = 0.0
        for product, details in net_cash_flow_investing_activities.items():
            month_total_net_cash_flow_investing_activity['amount'] += round(details['amount'], 2)
            for rec in details['month']:
                if rec not in month_total_net_cash_flow_investing_activity:
                    month_total_net_cash_flow_investing_activity[rec] = 0.0
                month_total_net_cash_flow_investing_activity['amount'] += round(details['month'][rec]['amount'], 2)
                month_total_net_cash_flow_investing_activity[rec] += details['month'][rec]['amount']

        lines = []
        for product in net_cash_flow_investing_activities:
            a = net_cash_flow_investing_activities[product]
            a.update({
                'name': a['name'],
                'id': product,
                'amount': self.formatINR(format(a['amount'], '.2f')),
                'month': {mo: {'amount': self.formatINR(format(details['amount'], '.2f'))} for
                          mo, details in
                          a['month'].items()}
            })
            lines.append(a)
        net_cash_flow_investing_data_dct['data'] = lines
        net_cash_flow_investing_data_dct['month_sum'] = month_total_net_cash_flow_investing_activity
        return net_cash_flow_investing_data_dct

    @api.model
    def get_direct_cost_data(self, start_date, end_date, product, month_list):
        #         order_line = self.env['sale.order.line'].search([
        #             # ('product_id', 'in', product.ids),
        #             ('order_id.date_order', '>=', start_date),
        #             ('order_id.date_order', '<=', end_date),
        #             ('order_id.state', 'in', ('done', 'sale')),
        # #             ('product_id.report_head_type', '=', 'direct_cost'),
        #         ])

        domain = [('report_revenue_type', 'in', ['1_cue_bridge', '2_cue_bridge_max', '3_cue_bridge_plus'])]
        #         product = self.env['product.product'].sudo().search([('name', 'in', p_name)])
        product = self.env['product.product'].sudo().search(domain)

        move_date_domain = [('move_id.state', '=', 'posted'),
                            ('move_id.invoice_date', '>=', start_date),
                            ('move_id.invoice_date', '<=', end_date)]

        move_lines = self.env['account.move.line'].search(move_date_domain + [
            ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
            ('product_id', 'in', product.ids),
        ])

        revenue_data = self.get_revanue_data(start_date, end_date, product, month_list, move_lines)

        order_line = self.env['account.move.line'].search(move_date_domain + [
            ('move_id.move_type', '=', 'in_invoice'),
            '|',
            ('product_id.report_head_type', '=', 'direct_cost'),
            ('product_id.categ_id.report_head_type', '=', 'direct_cost'),
        ])

        monthwise_cost = {}
        capex_categ_direct_cost = self.env['capex.category'].search([('report_head_type', '=', 'direct_cost')])
        capex_direct_cost_lst = []
        for capex_direct_cost in capex_categ_direct_cost:
            capex_direct_cost_dct = {}
            capex_direct_cost_dct['sequence'] = capex_direct_cost.sequence
            capex_direct_cost_dct['name'] = capex_direct_cost.name
            capex_direct_cost_lst.append(capex_direct_cost_dct)
        sequence_data_sorted_cost = sorted(capex_direct_cost_lst, key=lambda x: x['sequence'])

        sale_dct = {}
        sale_final_dct = {}
        for order in order_line:
            key = order.product_id.capex_category_id
            if key not in sale_dct:
                sale_dct[key] = {}
                sale_dct[key]['amount'] = 0.0
                sale_dct[key]['month'] = {}
            for sale_month in month_list:
                if sale_month not in sale_dct[key]['month']:
                    sale_dct[key]['month'][sale_month] = {'amount': 0.0}

            mkey = order.move_id.invoice_date.strftime("%B-%Y")
            sale_dct[key]['month'][mkey]['amount'] += order.price_total
            if key:
                if 'Cue' in key.name:
                    if mkey not in monthwise_cost:
                        monthwise_cost[mkey] = 0

                    #                 taxes_res = order.tax_ids.compute_all(
                    #                     order.price_unit,
                    #                     quantity=order.quantity,
                    #                     currency=order.currency_id,
                    #                     product=order.product_id,
                    #                     partner=order.partner_id,
                    #                     is_refund=order.is_refund,
                    #                 )

                    monthwise_cost[mkey] += (order.price_total) - ((order.price_total) / 1.18)
            sale_dct[key]['amount'] += order.price_total

        monthwise_revenue_cost = {}

        for rev in revenue_data['month_sum']:
            amt = revenue_data['month_sum'][rev]
            monthwise_revenue_cost[rev] = (amt) - ((amt) / 1.18)

        gst_key = 1111111
        gst_total = 0
        if gst_key not in sale_dct:
            sale_dct[gst_key] = {}
            sale_dct[gst_key]['amount'] = 0.0
            sale_dct[gst_key]['month'] = {}
        for sale_month in month_list:
            if sale_month not in sale_dct[gst_key]['month']:
                amt = monthwise_revenue_cost.get(sale_month, 0) - monthwise_cost.get(sale_month, 0)
                gst_total += amt
                sale_dct[gst_key]['month'][sale_month] = {'amount': amt}

        sale_dct[gst_key]['amount'] = gst_total

        #         mkey = order.move_id.invoice_date.strftime("%B-%Y")
        #         sale_dct[key]['month'][mkey]['amount'] += order.price_total

        sale_lines = []

        month_total_sale = {}
        month_total_sale['amount'] = 0.0
        for month in month_list:
            month_total_sale[month] = 0.0
        for product, details in sale_dct.items():
            month_total_sale['amount'] += details['amount']
            for rec in details['month']:
                if rec not in month_total_sale:
                    month_total_sale[rec] = 0.0
                month_total_sale[rec] += details['month'][rec]['amount']

        for sale in sale_dct:
            a = sale_dct[sale]
            if sale == 1111111:
                a.update({
                    'name': "GST Payable",
                    'id': 1111111,
                    'amount': self.formatINR(format(a['amount'], '.2f')),
                    'month': {mo: {'amount': self.formatINR(format(details['amount'], '.2f'))} for mo, details in
                              a['month'].items()}
                })

            else:
                a.update({
                    'name': sale.name,
                    'id': sale.id,
                    'amount': self.formatINR(format(a['amount'], '.2f')),
                    'month': {mo: {'amount': self.formatINR(format(details['amount'], '.2f'))} for mo, details in
                              a['month'].items()}
                })
            sale_lines.append(a)
        sale_final_dct['data'] = sale_lines
        ordered_data_cost = []
        sequence_names_cost = {item['name'] for item in sequence_data_sorted_cost}
        for item in sequence_data_sorted_cost:
            dept = next((d for d in sale_final_dct['data'] if d['name'] == item['name']), None)
            if dept:
                ordered_data_cost.append(dept)
        unsequenced_data_cost = [d for d in sale_final_dct['data'] if d['name'] not in sequence_names_cost]
        ordered_data_cost.extend(unsequenced_data_cost)
        sale_final_dct['data'] = ordered_data_cost
        sale_final_dct['month_sum'] = month_total_sale
        return sale_final_dct

    @api.model
    def get_revanue_data(self, start_date, end_date, product, month_list, move_lines):
        product_dict = {}
        customer_payment = self.env['account.payment'].search(
            [('payment_type', '=', 'inbound'),
             ('partner_id.report_head_type', 'in', ['revenue', 'exclude_fs_revenue_in'])])

        for line in move_lines:
            report_revenue_type = line.product_id.report_revenue_type
            if not report_revenue_type:
                report_revenue_type = '4_other'

            if report_revenue_type not in product_dict:
                product_dict[report_revenue_type] = {'qty': 0, 'amount': 0.0}
                product_dict[report_revenue_type]['month'] = {}
            for mo in month_list:
                if mo not in product_dict[report_revenue_type]['month']:
                    product_dict[report_revenue_type]['month'][mo] = {'qty': 0, 'amount': 0.0}
                if line.move_id.invoice_date:
                    if mo == line.move_id.invoice_date.strftime("%B-%Y"):

                        if line.move_id.move_type == 'out_refund':
                            product_dict[report_revenue_type]['month'][mo]['amount'] -= line.price_total
                            product_dict[report_revenue_type]['month'][mo]['qty'] -= line.quantity
                        else:
                            product_dict[report_revenue_type]['month'][mo]['amount'] += line.price_total
                            product_dict[report_revenue_type]['month'][mo]['qty'] += line.quantity

            if line.move_id.move_type == 'out_refund':
                product_dict[report_revenue_type]['qty'] -= line.quantity
                product_dict[report_revenue_type]['amount'] = product_dict[report_revenue_type]['amount'] - round(
                    line.price_total, 2)
            else:
                product_dict[report_revenue_type]['qty'] += line.quantity
                product_dict[report_revenue_type]['amount'] = product_dict[report_revenue_type]['amount'] + round(
                    line.price_total, 2)

        for payment in customer_payment:
            if '4_other' in product_dict and payment.date.strftime("%B-%Y") in product_dict['4_other']['month']:
                product_dict['4_other']['month'][payment.date.strftime("%B-%Y")]['amount'] += payment.amount
                product_dict['4_other']['amount'] += payment.amount

        month_total = {}
        product_dct = {}
        month_total['amount'] = 0.0
        for month in month_list:
            month_total[month] = 0.0
        for product, details in product_dict.items():
            month_total['amount'] += round(details['amount'], 2)
            for rec in details['month']:
                if rec not in month_total:
                    month_total[rec] = 0.0
                    # month_total['amount'] += round(details['month'][rec]['amount'], 2)
                month_total[rec] += details['month'][rec]['amount']
        lines = []
        count = 0
        myKeys = list(product_dict.keys())
        myKeys.sort()
        sorted_dict = {i: product_dict[i] for i in myKeys}

        selection_dict = {
            '1_cue_bridge': 'Cue Bridge',
            '2_cue_bridge_max': 'Cue Bridge Max',
            '3_cue_bridge_plus': 'Cue Bridge Plus',
            '4_other': 'Other'
        }
        for product in sorted_dict:
            a = product_dict[product]
            a.update({
                'name': selection_dict[product],
                'id': count,
                'amount': self.formatINR(format(a['amount'], '.2f')),
                'month': {mo: {'qty': details['qty'], 'amount': self.formatINR(format(details['amount'], '.2f'))} for
                          mo, details in
                          a['month'].items()}
            })
            count += 1
            lines.append(a)
        product_dct['data'] = lines  # sorted(lines, key=lambda d: d['qty'], reverse=True)
        product_dct['month_sum'] = month_total
        return product_dct

    @api.model
    def get_revenue_product_data(self, start_date, end_date, from_data):
        #         p_name = [
        #             'Cue Bridge',
        #             'Cue Bridge Demoe',
        #             'Cue Bridge Plus',
        #             'Cue Bridge Plus Demo',
        #             'Cue Bridge Max',
        #             'Cue Bridge Max Demo',
        #         ]
        #         product = self.env['product.product'].search([('name', 'in', p_name)])
        product = self.env['product.product'].search([])

        cue_product = product.filtered(lambda i: i.report_revenue_type != False and i.report_revenue_type != '4_other')

        if from_data == 'filter':
            if type(start_date) == str:
                start_date = fields.Date.from_string(start_date)
                end_date = fields.Date.from_string(end_date)
        else:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)

        month_list = self.get_year_financial(start_date, end_date)
        move_domain = [('move_id.state', '=', 'posted'),
                       ('move_id.invoice_date', '>=', start_date),
                       ('move_id.invoice_date', '<=', end_date), ]

        move_lines = self.env['account.move.line'].search(move_domain + [
            ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
            ('product_id', 'in', product.ids),
        ])
        # product_dict = {}

        #####################    Revanue    #####################

        product_dct = self.get_revanue_data(start_date, end_date, product, month_list, move_lines)

        #####################    direct cost    #####################

        sale_final_dct = self.get_direct_cost_data(start_date, end_date, cue_product, month_list)

        #####################    Variable Cost    #####################

        variable_cost_final_dct = self.get_cost_data(move_domain, 'variable_cost', month_list)

        #####################     Overhead Cost    #####################
        overhead_cost_final_dct = self.with_context(start_date=start_date, end_date=end_date).get_cost_data(move_domain,
                                                                                                            'overhead_cost',
                                                                                                            month_list)

        #####################    Capex    #####################
        capex_cost_final_dct = self.get_capex_cost_data(move_domain, 'capex', month_list)

        #####################    Wages & Related Cost    #####################

        wages_final_dct = self.get_wages_data(month_list, start_date, end_date)

        ####################    Working Capital    ####################

        working_data_dct = self.get_working_capital_data(month_list, start_date, end_date)

        ####################    Cash Flow Statement    ####################

        cash_flow_data_dct = self.get_cash_flow_data(month_list, start_date, end_date)

        ####################    Cash Flow from Investing Activities    ####################

        cash_flow_investing_activities_dct = self.get_cash_flow_activities_data(month_list, start_date, end_date)

        ####################    Net Income    ####################
        net_income = self.get_net_income_data(month_list, start_date, end_date)

        ####################    Net Cash Flow from Investing Activities    ####################

        net_cash_flow_from_investing_activities = self.get_net_cash_flow_from_investing_activities_data(month_list,
                                                                                                        start_date,
                                                                                                        end_date)
        ###############################################################

        return (
            product_dct, sale_final_dct, variable_cost_final_dct, overhead_cost_final_dct, capex_cost_final_dct,
            wages_final_dct, working_data_dct, cash_flow_data_dct, cash_flow_investing_activities_dct,
            net_cash_flow_from_investing_activities, net_income
        )

    @api.model
    def view_report(self, **kwargs):
        filtered_data_domain = {}
        symbol = self.env.company.currency_id.symbol,
        final_sum_revenue = {}

        # final_sum_working_cash_flow = {}

        def update_month_dct(data, month_dct):
            for key in data['month_sum']:
                if key not in month_dct:
                    month_dct[key] = []
                month_dct[key].append(self.formatINR(data['month_sum'][key]))

        month_dct = {}
        if 'date_from' and 'date_to' in kwargs['0']['data_dct']:
            start_date = kwargs['0']['data_dct']['date_from']
            filtered_data_domain['start_date'] = start_date
            end_date = kwargs['0']['data_dct']['date_to']
            filtered_data_domain['end_date'] = end_date
            from_data = "filter"

            product_list, sale_final_dct, variable_cost_final_dct, overhead_cost_final_dct, capex_cost_final_dct, wages_final_dct, working_data_dct, cash_flow_data_dct, cash_flow_investing_activities_dct, net_cash_flow_from_investing_activities, net_income = self.get_revenue_product_data(
                start_date, end_date, from_data)
        else:
            today = datetime.date.today()
            current_year = today.year
            end_date = datetime.date.today() + relativedelta(day=31)
            start_date = datetime.datetime(current_year, 4, 1).date()
            from_data = "default"
            product_list, sale_final_dct, variable_cost_final_dct, overhead_cost_final_dct, capex_cost_final_dct, wages_final_dct, working_data_dct, cash_flow_data_dct, cash_flow_investing_activities_dct, net_cash_flow_from_investing_activities, net_income = self.get_revenue_product_data(
                start_date, end_date, from_data)
        update_month_dct(product_list, month_dct)

        update_month_dct(sale_final_dct, month_dct)

        update_month_dct(variable_cost_final_dct, month_dct)

        update_month_dct(overhead_cost_final_dct, month_dct)

        update_month_dct(capex_cost_final_dct, month_dct)

        update_month_dct(wages_final_dct, month_dct)

        update_month_dct(working_data_dct, month_dct)

        update_month_dct(cash_flow_data_dct, month_dct)

        update_month_dct(cash_flow_investing_activities_dct, month_dct)

        update_month_dct(net_cash_flow_from_investing_activities, month_dct)

        data_list = []
        data_list_flow = []
        final_sum_dct = {}

        def update_dct(dct, final_sum_dct, sum_amount, key, data, name):
            dct['amount'] = 0
            dct['month'] = {}
            dct['name'] = name
            for var in data['month_sum']:
                if var != 'amount':
                    final_sum_dct[var] = final_sum_dct.get(var, 0.0) + float(data['month_sum'][var])
                    dct['month'][var] = {'amount': self.formatINR(format(float(data['month_sum'][var]), '.2f'))}
                dct['amount'] = float(data['month_sum']['amount'])

            sum_amount += dct['amount']
            return dct, sum_amount

        sum_amount = 0
        revanue_sum_amount = 0

        # Total Revenues
        revenue_dct, revanue_sum_amount = update_dct({}, final_sum_dct, sum_amount, 'revenue', product_list,
                                                     'Total Revenues')
        # revanue_sum_amount = sum_amount
        data_list.append(revenue_dct)
        revenue_dct['amount'] = self.formatINR(format(revanue_sum_amount, '.2f'))

        # Total Direct Costs
        sum_dct, sum_amount = update_dct({}, final_sum_dct, sum_amount, 'direct_costs', sale_final_dct,
                                         'Total Direct Costs')
        sum_amount = float(format(sum_amount, '.2f'))
        sum_dct['amount'] = self.formatINR(format(sum_amount, '.2f'))
        data_list.append(sum_dct)

        # Total Variable Costs
        variable_sum_dct, sum_amount = update_dct({}, final_sum_dct, sum_amount, 'variable_costs',
                                                  variable_cost_final_dct, 'Total Variable Costs')
        data_list.append(variable_sum_dct)
        variable_sum_dct['amount'] = self.formatINR(format(sum_amount, '.2f'))

        # Total Overhead Costs
        overhead_sum_dct, sum_amount = update_dct({}, final_sum_dct, sum_amount, 'overhead_costs',
                                                  overhead_cost_final_dct, 'Total Overhead Costs')
        data_list.append(overhead_sum_dct)
        overhead_sum_dct['amount'] = self.formatINR(format(sum_amount, '.2f'))

        # Total Capex Costs
        #         capex_sum_dct, sum_amount = update_dct({}, final_sum_dct, sum_amount, 'capex_costs', capex_cost_final_dct,
        #                                                'Total Capex Costs')
        #         data_list.append(capex_sum_dct)

        # Total Wages and Related Expenses
        wages_sum_dct, sum_amount = update_dct({}, final_sum_dct, sum_amount, 'wages', wages_final_dct,
                                               'Total Wages and Related Expenses')
        data_list.append(wages_sum_dct)
        wages_sum_dct['amount'] = self.formatINR(format(sum_amount, '.2f'))
        month_dct['amount'].append(self.formatINR(format(revanue_sum_amount - sum_amount, '.2f')))
        axy_dict = {}
        for item in data_list:
            for item_month in item['month']:
                if item_month not in axy_dict:
                    axy_dict[item_month] = {
                        'revanue_amount': 0,
                        'other_amount': 0
                    }
                if item['name'] == 'Total Revenues':
                    axy_dict[item_month]['revanue_amount'] += self.convert_amount(item['month'][item_month]['amount'])
                else:
                    axy_dict[item_month]['other_amount'] += self.convert_amount(item['month'][item_month]['amount'])
        for rec in axy_dict:
            amt_data = axy_dict[rec]['revanue_amount'] - axy_dict[rec]['other_amount']
            month_dct[rec].append(self.formatINR(amt_data))
        final_sum_revenue['data'] = data_list
        # for mo_data in final_sum_dct:
        #     if mo_data in month_dct:
        #         month_dct[mo_data].append(self.formatINR(format(final_sum_dct[mo_data], '.2f')))
        # update_month_dct(net_income, month_dct)
        net_income_dct = {'month_sum': {}}
        for key in data_list:

            net_income_dct['month_sum']['amount'] = revanue_sum_amount - sum_amount
            for rec in axy_dict:
                amt_data = axy_dict[rec]['revanue_amount'] - axy_dict[rec]['other_amount']
                net_income_dct['month_sum'][rec] = amt_data

                # month_dct[rec].append(self.formatINR(amt_data))
            # for net_mo in key['month']:
            #     if net_mo not in net_income_dct['month_sum']:
            #         float_amount = self.convert_amount(key['month'][net_mo]['amount'])
            #         net_income_dct['month_sum'][net_mo] = float_amount
            #     else:
            #         float_amount = self.convert_amount(key['month'][net_mo]['amount'])
            #         net_income_dct['month_sum'][net_mo] += float_amount
        update_month_dct(net_income_dct, month_dct)

        # for income in net_income_dct['month_sum'][key]:
        #     if income not in net_income_dct['month_sum']:
        # net_income_dct['month_sum'][key] = 0.0
        # month_dct[key].append(self.formatINR(data['month_sum'][key]))
        # month_dct['amount'].append(net_income_dct['month_sum']['amount'])
        # for rec in net_income_dct['month_sum']:
        #     month_dct[rec].append(self.formatINR(net_income_dct['month_sum'][rec]))

        blank_data_month_dct = {'month_sum': {}}
        for mo in month_dct:
            for rec in range(0, 7):
                month_dct[mo].append(self.formatINR(format(0.00, '.2f')))
                if mo not in blank_data_month_dct['month_sum']:
                    blank_data_month_dct['month_sum'][mo] = self.formatINR(format(0.00, '.2f'))
        data = {
            'symbol': symbol,
            'month_list': month_dct,
            'filtered_data_domain': filtered_data_domain,
            'header': {
                'Revenue': product_list,
                'Direct Cost': sale_final_dct,
                'Variable Cost': variable_cost_final_dct,
                'Overhead Cost': overhead_cost_final_dct,
                'Capex': capex_cost_final_dct,
                'Wages & Related Cost': wages_final_dct,
                'Working Capital': working_data_dct,
                'Cash Flow Statement': cash_flow_data_dct,
                'Net Cash Flow from Operating Activities': cash_flow_investing_activities_dct,
                'Net Cash Flow from Investing Activities': net_cash_flow_from_investing_activities,
                'Operating Income': final_sum_revenue,
                'Net Income': net_income_dct,
                'EBIT': blank_data_month_dct,
                'Interest Payments': blank_data_month_dct,
                'Tax Payments': blank_data_month_dct,
                'Cash Flow from Financing Activity': blank_data_month_dct,
                'Cash In Hand at the beginning': blank_data_month_dct,
                'Minimum Capital Required | Net Cash Flow': blank_data_month_dct,
                'Cumulative Net Cashflow': blank_data_month_dct,
            }
        }
        return data

    @api.model
    def get_working_capital_data_new(self, **kwargs):
        if 'date_from' and 'date_to' in kwargs['0']['data_dct']:
            start_date = kwargs['0']['data_dct']['date_from']
            end_date = kwargs['0']['data_dct']['date_to']
            if type(start_date) == str:
                start_date = fields.Date.from_string(start_date)
                end_date = fields.Date.from_string(end_date)
            month_list = self.get_year_financial(start_date, end_date)
        else:
            today = datetime.date.today()
            current_year = today.year
            end_date = datetime.date.today() + relativedelta(day=31)
            start_date = datetime.datetime(current_year, 4, 1).date()
            month_list = self.get_year_financial(start_date, end_date)
        data = self.get_working_capital_data(month_list, start_date, end_date)
        return data

    def get_dynamic_xlsx_report(self, data, response, report_data, dfr_data):
        report_data = json.loads(report_data)
        month_heading = json.loads(data)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'align': 'center', 'bold': True, 'border': 1})
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        txt_name = workbook.add_format({'font_size': '10px', 'border': 1})
        inner_txt_name = workbook.add_format({'align': 'center', 'font_size': '10px', 'border': 1})
        txt = workbook.add_format({'align': 'right', 'font_size': '10px', 'border': 1})
        sub_heading = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px', 'border': 1, 'border_color': 'black'})

        sheet.merge_range('A1:I2', self.env.user.company_id.name + ':' + 'Fund Statement', head)

        if "start_date" in dfr_data:
            sheet.write(3, 1, 'Start Date', sub_heading)
            sheet.write(3, 2, dfr_data['start_date'], sub_heading)

        if "end_date" in dfr_data:
            sheet.write(3, 4, 'End Date', sub_heading)
            sheet.write(3, 5, dfr_data['end_date'], sub_heading)
        sheet.merge_range('A6:C6', 'Period', sub_heading)
        sheet.write(5, 3, '', sub_heading)

        for rec in range(0, 12):
            sheet.set_column(rec, rec, 15)

        row, col = 5, 4
        for rec in month_heading:
            if rec != 'amount':
                sheet.write(row, col, rec, sub_heading)
                col += 1
        for period_name in report_data:
            sum_col = 3
            row += 1
            sheet.merge_range(row, 0, row, 2, period_name, cell_format)

            if 'month_sum' in report_data[period_name]:
                for sum in report_data[period_name]['month_sum']:
                    if period_name != 'Working Capital':
                        sheet.write(row, sum_col, self.formatINR(report_data[period_name]['month_sum'][sum]),
                                    sub_heading)
                        sum_col += 1
                    if period_name == 'Working Capital':
                        sheet.write(row, sum_col, '',
                                    sub_heading)
                        sum_col += 1
            if 'data' in report_data[period_name]:
                for month_sum in report_data[period_name]['data']:
                    col_amt_data = 3
                    row += 1
                    sheet.merge_range(row, 0, row, 2, month_sum['name'] or '', txt_name)
                    sheet.write(row, col_amt_data, month_sum['amount'], txt)
                    new_row = row
                    if 'qty' in month_sum:
                        row += 1
                        sheet.write(row, col_amt_data, month_sum['qty'], txt)
                        sheet.merge_range(row, 0, row, 2, '', txt_name)
                    if period_name != 'Working Capital':
                        for month_data in month_sum['month']:
                            col_amt_data += 1
                            sheet.write(new_row, col_amt_data, month_sum['month'][month_data]['amount'], txt)
                            if 'qty' in month_sum['month'][month_data]:
                                sheet.write(new_row + 1, col_amt_data, month_sum['month'][month_data]['qty'], txt)
                    if period_name == 'Working Capital':
                        for month_data in month_sum['month']:
                            col_amt_data += 1
                            sheet.write(new_row, col_amt_data, month_sum['month'][month_data], txt)

                        for inner_data in month_sum['inner_data']:
                            for rec in inner_data:
                                row += 1
                                new_col_amt_data = 4
                                sheet.merge_range(row, 0, row, 2, inner_data[rec]['name'] or '', inner_txt_name)
                                sheet.write(row, 3, inner_data[rec]['amount'], txt)
                                for inner_month_data in inner_data[rec]['month']:
                                    sheet.write(row, new_col_amt_data,
                                                inner_data[rec]['month'][inner_month_data]['amount'], txt)
                                    new_col_amt_data += 1
                        row += 1
                        sheet.merge_range(row, 0, row, new_col_amt_data, '')
            row += 1
            sheet.merge_range(row, 0, row, col_amt_data, '')
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
