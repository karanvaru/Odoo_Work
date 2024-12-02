# -*- coding: utf-8 -*-

import calendar
import datetime
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, api, fields,_
from odoo.http import request


class DashBoard(models.Model):
    _inherit = 'account.move'

    # function to getting expenses

    # function to getting income of this year

    @api.model
    def _get_financial_year(self):
            date = fields.date.today()
            end_date = fields.Date.today()
            #initialize the current year
            year_of_date=date.year
            #initialize the current financial year start date
            financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()
            if date < financial_year_start_date:
                financial_year_start_date = financial_year_start_date + relativedelta(months=-12)

            financial_year_end_date = financial_year_start_date + relativedelta(months=12, days=-1)
            return financial_year_start_date, financial_year_end_date

    @api.model
    def get_year(self):
        date = fields.date.today()
        end_date = fields.Date.today()
        # initialize the current year
        year_of_date = date.year
        # initialize the current financial year start date
        financial_year_start_date = datetime.strptime(str(year_of_date) + "-04-01", "%Y-%m-%d").date()
        if date < financial_year_start_date:
            financial_year_start_date = financial_year_start_date + relativedelta(months=-12)

        financial_year_end_date = financial_year_start_date + relativedelta(months=12, days=-1)
        # date_list = []
        data_dct = {
            'start_date' : financial_year_start_date,
            'end_date' : financial_year_end_date,
        }
        return data_dct


    @api.model
    def get_income_this_year(self, *post):

        company_id = self.get_current_company_value()

        month_list = []
        for i in range(11, -1, -1):
            l_month = datetime.now() - relativedelta(months=i)
            text = format(l_month, '%B')
            month_list.append(text)

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,to_char(account_move_line.date, 'Month')  as month ,
                             internal_group from account_move_line ,account_account where 
                             account_move_line.account_id=account_account.id AND internal_group = 'income' 
                             AND to_char(DATE(NOW()), 'YY') = to_char(account_move_line.date, 'YY')
                             AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                             AND %s 
                             group by internal_group,month                  
                        ''') % (states_arg))
        record = self._cr.dictfetchall()
        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,to_char(account_move_line.date, 'Month')  as month ,
                            internal_group from account_move_line ,account_account where 
                            account_move_line.account_id=account_account.id AND internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null)
                            AND to_char(DATE(NOW()), 'YY') = to_char(account_move_line.date, 'YY')
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                            AND %s 
                            group by internal_group,month                  
                        ''') % (states_arg))

        result = self._cr.dictfetchall()
        records = []
        for month in month_list:
            last_month_inc = list(filter(lambda m: m['month'].strip() == month, record))
            last_month_exp = list(filter(lambda m: m['month'].strip() == month, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'month': month,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0,
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        month = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            month.append(rec['month'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'month': month,
            'profit': profit,
        }

    # function to getting income of last year

    @api.model
    def get_income_last_year(self, *post):
        company_id = self.get_current_company_value()

        month_list = []
        for i in range(11, -1, -1):
            l_month = datetime.now() - relativedelta(months=i)
            text = format(l_month, '%B')
            month_list.append(text)

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,to_char(account_move_line.date, 'Month')  as month ,
                            internal_group from account_move_line ,account_account
                            where account_move_line.account_id=account_account.id AND internal_group = 'income' 
                            AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) -1 
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                            AND %s
                            group by internal_group,month                  
                 ''') % (states_arg))
        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,to_char(account_move_line.date, 'Month')  as month ,
                            internal_group from account_move_line , account_account where 
                            account_move_line.account_id=account_account.id AND internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null)
                            AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) -1 
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                            AND %s 
                            group by internal_group,month                  
                         ''') % (states_arg))

        result = self._cr.dictfetchall()
        records = []
        for month in month_list:
            last_month_inc = list(filter(lambda m: m['month'].strip() == month, record))
            last_month_exp = list(filter(lambda m: m['month'].strip() == month, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'month': month,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0,
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        month = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            month.append(rec['month'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'month': month,
            'profit': profit,
        }

    # function to getting income of last month

    @api.model
    def get_income_last_month(self, *post):

        company_id = self.get_current_company_value()
        day_list = []
        now = datetime.now()
        day = \
            calendar.monthrange(now.year - 1 if now.month == 1 else now.year,
                                now.month - 1 if not now.month == 1 else 12)[
                1]

        for x in range(1, day + 1):
            day_list.append(x)

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

#         states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date , internal_group from account_move_line , account_account where   
                            Extract(month FROM account_move_line.date) in ''' + str(tuple(company_id)) + ''' 
                            AND %s
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 
                            AND account_move_line.account_id=account_account.id AND internal_group='income'   
                            group by internal_group,date                 
                             ''') % (states_arg))

        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date ,internal_group from account_move_line ,account_account where  
                            Extract(month FROM account_move_line.date) in ''' + str(tuple(company_id)) + ''' 
                            AND %s
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 
                            AND account_move_line.account_id=account_account.id AND internal_group='expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null)
                            group by internal_group,date                 
                                 ''') % (states_arg))
        result = self._cr.dictfetchall()
        records = []
        for date in day_list:
            last_month_inc = list(filter(lambda m: m['date'] == date, record))
            last_month_exp = list(filter(lambda m: m['date'] == date, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'date': date,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        date = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            date.append(rec['date'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'date': date,
            'profit': profit

        }

    # function to getting income of this month

    @api.model
    def get_income_this_month(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        day_list = []
        now = datetime.now()
        day = calendar.monthrange(now.year, now.month)[1]
        for x in range(1, day + 1):
            day_list.append(x)

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date , internal_group from account_move_line , account_account
                            where   Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW()))  
                            AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW()))  
                            AND %s
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 
                            AND account_move_line.account_id=account_account.id AND internal_group='income'
                            group by internal_group,date                 
                        ''') % (states_arg))

        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date , internal_group from account_move_line , account_account where  
                            Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW()))  
                            AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW()))  
                            AND %s
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 
                            AND account_move_line.account_id=account_account.id AND internal_group='expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null)
                            group by internal_group,date                 
                         ''') % (states_arg))
        result = self._cr.dictfetchall()
        records = []
        for date in day_list:
            last_month_inc = list(filter(lambda m: m['date'] == date, record))
            last_month_exp = list(filter(lambda m: m['date'] == date, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'date': date,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        date = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            date.append(rec['date'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'date': date,
            'profit': profit

        }

    # function to getting late bills

    @api.model
    def get_latebills(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""

        self._cr.execute(('''  select res_partner.name as partner, res_partner.commercial_partner_id as res  ,
                            account_move.commercial_partner_id as parent, sum(account_move.amount_total) as amount
                            from account_move,res_partner where 
                            account_move.partner_id=res_partner.id AND account_move.move_type = 'in_invoice' AND
                            payment_state = 'not_paid' AND 
                              account_move.company_id in ''' + str(tuple(company_id)) + ''' AND
                            %s 
                            AND  account_move.commercial_partner_id=res_partner.commercial_partner_id 
                            group by parent,partner,res
                            order by amount desc ''') % (states_arg))

        record = self._cr.dictfetchall()

        bill_partner = [item['partner'] for item in record]

        bill_amount = [item['amount'] for item in record]

        amounts = sum(bill_amount[9:])
        name = bill_partner[9:]
        results = []
        pre_partner = []

        bill_amount = bill_amount[:9]
        bill_amount.append(amounts)
        bill_partner = bill_partner[:9]
        bill_partner.append("Others")
        records = {
            'bill_partner': bill_partner,
            'bill_amount': bill_amount,
            'result': results,

        }
        return records

        # return record

    # function to getting over dues

    @api.model
    def get_overdues(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""

        self._cr.execute((''' select res_partner.name as partner, res_partner.commercial_partner_id as res,
                             account_move.commercial_partner_id as parent, sum(account_move.amount_total) as amount
                            from account_move, account_move_line, res_partner, account_account where 
                            account_move.partner_id=res_partner.id AND account_move.move_type = 'out_invoice' 
                            AND payment_state = 'not_paid' 
                            AND %s
                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                            AND account_account.account_type = 'payable'
                            AND account_move.commercial_partner_id=res_partner.commercial_partner_id 
                            group by parent,partner,res
                            order by amount desc
                            ''') % (states_arg))
        record = self._cr.dictfetchall()
        due_partner = [item['partner'] for item in record]
        due_amount = [item['amount'] for item in record]

        amounts = sum(due_amount[9:])
        name = due_partner[9:]
        result = []
        pre_partner = []

        due_amount = due_amount[:9]
        due_amount.append(amounts)
        due_partner = due_partner[:9]
        due_partner.append("Others")
        records = {
            'due_partner': due_partner,
            'due_amount': due_amount,
            'result': result,

        }
        return records

    @api.model
    def get_overdues_this_month_and_year(self, *post):

        states_arg = [('state', '=', 'posted')]

        company_ids = self.get_current_company_value()

        if post[1] == 'this_month':
            current_month = datetime.now().month
            current_year = datetime.now().year
            domain = [
                         ('move_type', '=', 'out_invoice'),
                         ('payment_state', '=', 'not_paid'),
                         ('invoice_date_due', '>=', datetime(current_year, current_month, 1)),
                         ('invoice_date_due', '<=', datetime(current_year, current_month, 31)),
                         ('company_id', 'in', company_ids)
                     ] + states_arg
        else:
            current_year = datetime.now().year
            domain = [
                         ('move_type', '=', 'out_invoice'),
                         ('payment_state', '=', 'not_paid'),
                         ('invoice_date_due', '>=', datetime(current_year, 1, 1)),
                         ('invoice_date_due', '<=', datetime(current_year, 12, 31)),
                         ('company_id', 'in', company_ids)
                     ] + states_arg

        invoices = self.search(domain)

        result = {}
        for inv in invoices:
            if post[1] == 'this_month':
                month = inv.date.strftime('%B')
                key = (month, inv.partner_id.name, inv.id)
            else:
                key = (inv.partner_id.name, inv.id)

            if key not in result:
                result[key] = inv.amount_total
            else:
                result[key] += inv.amount_total

        if post[1] == 'this_month':
            final_result = [
                {
                    'month': key[0],
                    'due_partner': key[1],
                    'parent': key[2],
                    'amount': amount
                } for key, amount in result.items()
            ]
        else:
            final_result = [
                {
                    'due_partner': key[0],
                    'parent': key[1],
                    'amount': amount
                } for key, amount in result.items()
            ]

        final_result.sort(key=lambda x: x['amount'], reverse=True)

        due_partner = [item['due_partner'] for item in final_result]
        due_amount = [item['amount'] for item in final_result]

        amounts = sum(due_amount[9:])
        due_amount = due_amount[:9]
        due_amount.append(amounts)
        due_partner = due_partner[:9]
        due_partner.append("Others")

        records = {
            'due_partner': due_partner,
            'due_amount': due_amount,
            'result': final_result,
        }

        return final_result

#     @api.model
#     def get_overdues_this_month_and_year(self, *post):
#         print("_________________   over dueeeeeeeeeeeeeeeeee")
#         states_arg = ""
# #         if post[0] != 'posted':
# #             states_arg = """ account_move.state in ('posted', 'draft')"""
# #         else:
#         states_arg = """ account_move.state = 'posted'"""
#
#         company_id = self.get_current_company_value()
#         if post[1] == 'this_month':
#             self._cr.execute(('''
#                                select to_char(account_move.date, 'Month') as month, res_partner.name as due_partner, account_move.partner_id as parent,
#                                sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
#                                AND account_move.move_type = 'out_invoice'
#                                AND payment_state = 'not_paid'
#                                AND %s
#                                AND Extract(month FROM account_move.invoice_date_due) = Extract(month FROM DATE(NOW()))
#                                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
#                                AND account_move.partner_id = res_partner.commercial_partner_id
#                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
#                                group by parent, due_partner, month
#                                order by amount desc ''') % (states_arg))
#         else:
#             self._cr.execute((''' select  res_partner.name as due_partner, account_move.partner_id as parent,
#                                             sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
#                                             AND account_move.move_type = 'out_invoice'
#                                             AND payment_state = 'not_paid'
#                                             AND %s
#                                             AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
#                                             AND account_move.partner_id = res_partner.commercial_partner_id
#                                             AND account_move.company_id in ''' + str(tuple(company_id)) + '''
#
#                                             group by parent, due_partner
#                                             order by amount desc ''') % (states_arg))
#
#         record = self._cr.dictfetchall()
#         due_partner = [item['due_partner'] for item in record]
#         due_amount = [item['amount'] for item in record]
#
#         amounts = sum(due_amount[9:])
#         name = due_partner[9:]
#         result = []
#         pre_partner = []
#
#         due_amount = due_amount[:9]
#         due_amount.append(amounts)
#         due_partner = due_partner[:9]
#         due_partner.append("Others")
#         records = {
#             'due_partner': due_partner,
#             'due_amount': due_amount,
#             'result': result,
#
#         }
#         # print ("records -------------",records)
#         return record

    @api.model
    def get_overdues_this_month_and_year_range(self, *post):

        states_arg = [('state', '=', 'posted')]

        company_ids = self.get_current_company_value()

        start_date = False
        if len(post) > 2:
            start_date = post[2]
            end_date = post[3]


        domain = [
                     ('move_type', '=', 'out_invoice'),
                     ('payment_state', '=', 'not_paid'),
                     ('company_id', 'in', company_ids)
                 ] + states_arg

        if start_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            domain += [
                ('invoice_date_due', '>=', start_date_dt),
                ('invoice_date_due', '<=', end_date_dt),
                ('invoice_date_due', '>=', datetime(datetime.now().year, 1, 1)),
                ('invoice_date_due', '<=', datetime(datetime.now().year, 12, 31))
            ]
        else:
            domain += [
                ('invoice_date_due', '>=', datetime(datetime.now().year, 1, 1)),
                ('invoice_date_due', '<=', datetime(datetime.now().year, 12, 31))
            ]

        invoices = self.search(domain)

        result = {}
        for inv in invoices:
            month = inv.date.strftime('%B')
            partner_name = inv.partner_id.name
            parent_id = inv.id
            amount = inv.amount_total

            if start_date:
                key = (month, partner_name, parent_id)
            else:
                key = (partner_name, parent_id)

            if key not in result:
                result[key] = amount
            else:
                result[key] += amount

        if start_date:
            final_result = [
                {
                    'month': month,
                    'due_partner': partner_name,
                    'parent': parent_id,
                    'amount': amount
                } for (month, partner_name, parent_id), amount in result.items()
            ]
        else:
            final_result = [
                {
                    'due_partner': partner_name,
                    'parent': parent_id,
                    'amount': amount
                } for (partner_name, parent_id), amount in result.items()
            ]

        final_result.sort(key=lambda x: x['amount'], reverse=True)

        due_partner = [item['due_partner'] for item in final_result]
        due_amount = [item['amount'] for item in final_result]

        amounts = sum(due_amount[9:])
        name = due_partner[9:]
        result = []

        due_amount = due_amount[:9]
        due_amount.append(amounts)
        due_partner = due_partner[:9]
        due_partner.append("Others")

        records = {
            'due_partner': due_partner,
            'due_amount': due_amount,
            'result': final_result,
        }

        return final_result


#     @api.model
#     def get_overdues_this_month_and_year_range(self, *post):
#         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#         states_arg = ""
# #         if post[0] != 'posted':
# #             states_arg = """ account_move.state in ('posted', 'draft')"""
# #         else:
#         states_arg = """ account_move.state = 'posted'"""
#
#         company_id = self.get_current_company_value()
#
#         start_date = False
#         if len(post) > 2:
#             start_date = post[2]
#             end_date = post[3]
#
#         print ("start_date -----------",start_date)
#         if start_date:
#             self._cr.execute(('''
#                                select to_char(account_move.date, 'Month') as month, res_partner.name as due_partner, account_move.partner_id as parent,
#                                sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
#                                AND account_move.move_type = 'out_invoice'
#                                AND payment_state = 'not_paid'
#                                AND %s
#                                AND account_move.invoice_date_due >= '%s' AND  account_move.invoice_date_due <= '%s'
#                                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
#                                AND account_move.partner_id = res_partner.commercial_partner_id
#                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
#                                group by parent, due_partner, month
#                                order by amount desc ''') % (states_arg, start_date, end_date))
#         else:
#             self._cr.execute((''' select  res_partner.name as due_partner, account_move.partner_id as parent,
#                                             sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
#                                             AND account_move.move_type = 'out_invoice'
#                                             AND payment_state = 'not_paid'
#                                             AND %s
#                                             AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
#                                             AND account_move.partner_id = res_partner.commercial_partner_id
#                                             AND account_move.company_id in ''' + str(tuple(company_id)) + '''
#
#                                             group by parent, due_partner
#                                             order by amount desc ''') % (states_arg))
#
#         record = self._cr.dictfetchall()
#         print("!!!!!!!!!!!!!   rocorddd",record)
#         due_partner = [item['due_partner'] for item in record]
#         due_amount = [item['amount'] for item in record]
#
#         amounts = sum(due_amount[9:])
#         name = due_partner[9:]
#         result = []
#         pre_partner = []
#
#         due_amount = due_amount[:9]
#         due_amount.append(amounts)
#         due_partner = due_partner[:9]
#         due_partner.append("Others")
#         # records = {
#         #     'due_partner': due_partner,
#         #     'due_amount': due_amount,
#         #     'result': result,
#         #
#         # }
#         # print ("records -------------",records)
#         return record



    @api.model
    def get_latebillss(self, *post):
        company_id = self.get_current_company_value()

        partners = self.env['res.partner'].search([('active', '=', True)])

        states_arg = ""
#         if post[0] != 'posted':
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        
        start_date = False
        if len(post) > 2:
            start_date = post[2]
            end_date = post[3]
        
        if start_date:
            self._cr.execute((''' 
                        select to_char(account_move.date, 'Month') as month, res_partner.name as bill_partner, account_move.id as parent,
                        sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                        AND account_move.move_type = 'in_invoice'
                        AND payment_state = 'not_paid'
                        AND %s 
                        AND account_move.invoice_date_due >= '%s' AND account_move.invoice_date_due <= '%s'
                        AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                        AND account_move.partner_id = res_partner.commercial_partner_id
                        group by parent, bill_partner, month
                        order by amount desc ''') % (states_arg, start_date, end_date))

        elif post[1] == 'this_month':
            self._cr.execute((''' 
                                select to_char(account_move.date, 'Month') as month, res_partner.name as bill_partner, account_move.id as parent,
                                sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                AND account_move.move_type = 'in_invoice'
                                AND payment_state = 'not_paid'
                                AND %s 
                                AND Extract(month FROM account_move.invoice_date_due) = Extract(month FROM DATE(NOW()))
                                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                AND account_move.partner_id = res_partner.commercial_partner_id
                                group by parent, bill_partner, month
                                order by amount desc ''') % (states_arg))
        else:
            self._cr.execute((''' select res_partner.name as bill_partner, account_move.id as parent,
                                            sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                            AND account_move.move_type = 'in_invoice'
                                            AND payment_state = 'not_paid'
                                            AND %s
                                            AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.partner_id = res_partner.commercial_partner_id
                                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                            group by parent, bill_partner
                                            order by amount desc ''') % (states_arg))

        result = self._cr.dictfetchall()
        bill_partner = [item['bill_partner'] for item in result]

        bill_amount = [item['amount'] for item in result]

        amounts = sum(bill_amount[9:])
        name = bill_partner[9:]
        results = []
        pre_partner = []

        bill_amount = bill_amount[:9]
        bill_amount.append(amounts)
        bill_partner = bill_partner[:9]
        bill_partner.append("Others")
        records = {
            'bill_partner': bill_partner,
            'bill_amount': bill_amount,
            'result': results,

        }
        return result

    @api.model
    def get_top_10_customers_month(self, *post):
        record_invoice = {}
        record_refund = {}
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post[0] != 'posted':
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        if post[1] == 'this_month':

            start_date = False
            if len(post) > 2:
                start_date = post[2]
                end_date = post[3]

            if start_date:
                self._cr.execute((''' select res_partner.name as customers, account_move.commercial_partner_id as parent, 
                                        sum(account_move.amount_total) as amount from account_move, res_partner
                                        where account_move.commercial_partner_id = res_partner.id
                                        AND account_move.company_id in %s 
                                        AND account_move.move_type = 'out_invoice' 
                                        AND %s   
                                        AND account_move.invoice_date >= '%s' AND account_move.invoice_date <= '%s' 
                                        group by parent, customers
                                        order by amount desc 
                                        limit 10
                                        ''') % (tuple(company_id), states_arg, start_date, end_date))
                record_invoice = self._cr.dictfetchall()
                self._cr.execute((''' select res_partner.name as customers, account_move.commercial_partner_id as parent, 
                                        sum(account_move.amount_total) as amount from account_move, res_partner
                                        where account_move.commercial_partner_id = res_partner.id
                                        AND account_move.company_id in %s
                                        AND account_move.move_type = 'out_refund' 
                                        AND %s      
                                        AND account_move.invoice_date >= '%s' AND account_move.invoice_date <= '%s' 
                                        group by parent, customers
                                        order by amount desc 
                                        limit 10
                                        ''') % (tuple(company_id), states_arg, start_date, end_date))
                record_refund = self._cr.dictfetchall()
            else:
                self._cr.execute((''' select res_partner.name as customers, account_move.commercial_partner_id as parent, 
                                        sum(account_move.amount_total) as amount from account_move, res_partner
                                        where account_move.commercial_partner_id = res_partner.id
                                        AND account_move.company_id in %s 
                                        AND account_move.move_type = 'out_invoice' 
                                        AND %s   
                                        AND Extract(month FROM account_move.invoice_date) = Extract(month FROM DATE(NOW()))
                                        AND Extract(YEAR FROM account_move.invoice_date) = Extract(YEAR FROM DATE(NOW()))                      
                                        group by parent, customers
                                        order by amount desc 
                                        limit 10
                                        ''') % (tuple(company_id), states_arg))
                record_invoice = self._cr.dictfetchall()
                self._cr.execute((''' select res_partner.name as customers, account_move.commercial_partner_id as parent, 
                                        sum(account_move.amount_total) as amount from account_move, res_partner
                                        where account_move.commercial_partner_id = res_partner.id
                                        AND account_move.company_id in %s
                                        AND account_move.move_type = 'out_refund' 
                                        AND %s      
                                        AND Extract(month FROM account_move.invoice_date) = Extract(month FROM DATE(NOW()))
                                        AND Extract(YEAR FROM account_move.invoice_date) = Extract(YEAR FROM DATE(NOW()))                   
                                        group by parent, customers
                                        order by amount desc 
                                        limit 10
                                        ''') % (tuple(company_id), states_arg))
                record_refund = self._cr.dictfetchall()

        else:
            one_month_ago = (datetime.now() - relativedelta(months=1)).month
            self._cr.execute((''' select res_partner.name as customers, account_move.commercial_partner_id as parent, 
                                            sum(account_move.amount_total) as amount from account_move, res_partner
                                            where account_move.commercial_partner_id = res_partner.id
                                            AND account_move.company_id in %s
                                            AND account_move.move_type = 'out_invoice' 
                                            AND %s            
                                            AND Extract(month FROM account_move.invoice_date) = ''' + str(
                one_month_ago) + '''
                                            group by parent, customers
                                            order by amount desc 
                                            limit 10
                                            ''') % (tuple(company_id), states_arg))
            record_invoice = self._cr.dictfetchall()
            self._cr.execute((''' select res_partner.name as customers, account_move.commercial_partner_id as parent, 
                                            sum(account_move.amount_total) as amount from account_move, res_partner
                                            where account_move.commercial_partner_id = res_partner.id
                                            AND account_move.company_id in %s 
                                            AND account_move.move_type = 'out_refund' 
                                            AND %s       
                                            AND Extract(month FROM account_move.invoice_date) = ''' + str(
                one_month_ago) + '''                  
                                            group by parent, customers
                                            order by amount desc 
                                            limit 10
                                            ''') % (tuple(company_id), states_arg))
            record_refund = self._cr.dictfetchall()
        summed = []
        for out_sum in record_invoice:
            parent = out_sum['parent']
            su = out_sum['amount'] - \
                 (list(filter(lambda refund: refund['parent'] == out_sum['parent'], record_refund))[0][
                      'amount'] if len(
                     list(filter(lambda refund: refund['parent'] == out_sum['parent'], record_refund))) > 0 else 0.0)
            summed.append({
                'customers': out_sum['customers'],
                'amount': su,
                'parent': parent
            })
        return summed

    # function to get total invoice

    @api.model
    def get_total_invoice(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""

        self._cr.execute(('''select sum(amount_total) as customer_invoice from account_move where move_type ='out_invoice'
                            AND  %s  AND account_move.company_id in ''' + str(tuple(company_id)) + '''           
                        ''') % (states_arg))
        record_customer = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as supplier_invoice from account_move where move_type ='in_invoice' 
                          AND  %s  AND account_move.company_id in ''' + str(tuple(company_id)) + '''      
                        ''') % (states_arg))
        record_supplier = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as credit_note from account_move where move_type ='out_refund'
                          AND  %s  AND account_move.company_id in ''' + str(tuple(company_id)) + '''      
                        ''') % (states_arg))
        result_credit_note = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as refund from account_move where move_type ='in_refund'
                          AND  %s  AND account_move.company_id in ''' + str(tuple(company_id)) + '''   
                        ''') % (states_arg))
        result_refund = self._cr.dictfetchall()

        customer_invoice = [item['customer_invoice'] for item in record_customer]
        supplier_invoice = [item['supplier_invoice'] for item in record_supplier]
        credit_note = [item['credit_note'] for item in result_credit_note]
        refund = [item['refund'] for item in result_refund]

        return customer_invoice, credit_note, supplier_invoice, refund

    @api.model
    def get_total_invoice_current_year(self, *post):

        company_id = self.get_current_company_value()

#         states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""

        self._cr.execute(('''select sum(amount_total_signed) as customer_invoice from account_move where move_type ='out_invoice'
                            AND   %s                               
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''           
                        ''') % (states_arg))
        record_customer_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as supplier_invoice from account_move where move_type ='in_invoice'
                            AND  %s                              
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''      
                        ''') % (states_arg))
        record_supplier_current_year = self._cr.dictfetchall()
        result_credit_note_current_year = [{'credit_note': 0.0}]
        result_refund_current_year = [{'refund': 0.0}]
        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as customer_invoice_paid from account_move where move_type ='out_invoice'
                                    AND   %s
                                    AND payment_state = 'paid'
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                    AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                ''') % (states_arg))
        record_paid_customer_invoice_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as supplier_invoice_paid from account_move where move_type ='in_invoice'
                                    AND   %s
                                    AND  payment_state = 'paid'
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                    AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                ''') % (states_arg))
        result_paid_supplier_invoice_current_year = self._cr.dictfetchall()
        record_paid_customer_credit_current_year = [{'customer_credit_paid': 0.0}]
        result_paid_supplier_refund_current_year = [{'supplier_refund_paid': 0.0}]
        customer_invoice_current_year = [item['customer_invoice'] for item in record_customer_current_year]
        supplier_invoice_current_year = [item['supplier_invoice'] for item in record_supplier_current_year]

        credit_note_current_year = [item['credit_note'] for item in result_credit_note_current_year]
        refund_current_year = [item['refund'] for item in result_refund_current_year]

        paid_customer_invoice_current_year = [item['customer_invoice_paid'] for item in
                                              record_paid_customer_invoice_current_year]
        paid_supplier_invoice_current_year = [item['supplier_invoice_paid'] for item in
                                              result_paid_supplier_invoice_current_year]

        paid_customer_credit_current_year = [item['customer_credit_paid'] for item in
                                             record_paid_customer_credit_current_year]
        paid_supplier_refund_current_year = [item['supplier_refund_paid'] for item in
                                             result_paid_supplier_refund_current_year]

        return customer_invoice_current_year, credit_note_current_year, supplier_invoice_current_year, refund_current_year, paid_customer_invoice_current_year, paid_supplier_invoice_current_year, paid_customer_credit_current_year, paid_supplier_refund_current_year

    @api.model
    def get_total_invoice_current_month(self, *post):

        company_id = self.get_current_company_value()
        
        
        

#         states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        start_date = False

        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]


        if start_date:
            self._cr.execute(('''select sum(amount_total_signed) as customer_invoice from account_move where move_type ='out_invoice'
                                        AND   %s                               
                                        AND account_move.date >= '%s' AND account_move.date <= '%s' 
                                        AND account_move.company_id in ''' + str(tuple(company_id)) + '''           
                                    ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute(('''select sum(amount_total_signed) as customer_invoice from account_move where move_type ='out_invoice'
                                        AND   %s                               
                                        AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                        AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                        AND account_move.company_id in ''' + str(tuple(company_id)) + '''           
                                    ''') % (states_arg))

        record_customer_current_month = self._cr.dictfetchall()

        if start_date:
            self._cr.execute(('''select sum(-(amount_total_signed)) as supplier_invoice from account_move where move_type ='in_invoice'
                                        AND  %s                              
                                        AND account_move.date >= '%s' AND account_move.date <= '%s'
                                        AND account_move.company_id in ''' + str(tuple(company_id)) + '''      
                                    ''') % (states_arg, start_date, end_date))
        
        else:
            self._cr.execute(('''select sum(-(amount_total_signed)) as supplier_invoice from account_move where move_type ='in_invoice'
                                    AND  %s                              
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in ''' + str(tuple(company_id)) + '''      
                                ''') % (states_arg))

        
        record_supplier_current_month = self._cr.dictfetchall()
        result_credit_note_current_month = [{'credit_note': 0.0}]
        result_refund_current_month = [{'refund': 0.0}]
        if start_date:
            self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as customer_invoice_paid from account_move where move_type ='out_invoice'
                                                AND   %s
                                                AND payment_state = 'paid'
                                                AND account_move.date >= '%s' AND account_move.date <= '%s'
                                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                            ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as customer_invoice_paid from account_move where move_type ='out_invoice'
                                                AND   %s
                                                AND payment_state = 'paid'
                                                AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                                AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                            ''') % (states_arg))
            
        record_paid_customer_invoice_current_month = self._cr.dictfetchall()

        if start_date:
            self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as supplier_invoice_paid from account_move where move_type ='in_invoice'
                                                AND   %s
                                                AND payment_state = 'paid'
                                                AND account_move.date >= '%s' AND account_move.date <= '%s'
                                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                            ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as supplier_invoice_paid from account_move where move_type ='in_invoice'
                                                AND   %s
                                                AND payment_state = 'paid'
                                                AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                                AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                            ''') % (states_arg))
            
        result_paid_supplier_invoice_current_month = self._cr.dictfetchall()
        record_paid_customer_credit_current_month = [{'customer_credit_paid': 0.0}]
        result_paid_supplier_refund_current_month = [{'supplier_refund_paid': 0.0}]

        customer_invoice_current_month = [item['customer_invoice'] for item in record_customer_current_month]
        supplier_invoice_current_month = [item['supplier_invoice'] for item in record_supplier_current_month]
        credit_note_current_month = [item['credit_note'] for item in result_credit_note_current_month]
        refund_current_month = [item['refund'] for item in result_refund_current_month]
        paid_customer_invoice_current_month = [item['customer_invoice_paid'] for item in
                                               record_paid_customer_invoice_current_month]
        paid_supplier_invoice_current_month = [item['supplier_invoice_paid'] for item in
                                               result_paid_supplier_invoice_current_month]

        paid_customer_credit_current_month = [item['customer_credit_paid'] for item in
                                              record_paid_customer_credit_current_month]
        paid_supplier_refund_current_month = [item['supplier_refund_paid'] for item in
                                              result_paid_supplier_refund_current_month]

        currency = self.get_currency()
        return customer_invoice_current_month, credit_note_current_month, supplier_invoice_current_month, refund_current_month, paid_customer_invoice_current_month, paid_supplier_invoice_current_month, paid_customer_credit_current_month, paid_supplier_refund_current_month, currency

    @api.model
    def get_total_invoice_this_month(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""

        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            self._cr.execute(('''select sum(amount_total) from account_move where move_type = 'out_invoice' 
                                AND %s
                                AND account_move.date >= '%s' AND account_move.date <= '%s'       
                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute(('''select sum(amount_total) from account_move where move_type = 'out_invoice' 
                                AND %s
                                AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))      
                                AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))   
                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                ''') % (states_arg))
            
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice last month

    @api.model
    def get_total_invoice_last_month(self):

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        self._cr.execute('''select sum(amount_total) from account_move where move_type = 'out_invoice' AND
                               account_move.state = 'posted'
                            AND Extract(month FROM account_move.date) = ''' + str(one_month_ago) + ''' 
                            ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice last year

    @api.model
    def get_total_invoice_last_year(self):

        self._cr.execute(''' select sum(amount_total) from account_move where move_type = 'out_invoice' 
                            AND account_move.state = 'posted'
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW())) - 1    
                                ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice this year

    @api.model
    def get_total_invoice_this_year(self):

        company_id = self.get_current_company_value()

        self._cr.execute(''' select sum(amount_total) from account_move where move_type = 'out_invoice'
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW())) AND
                               account_move.state = 'posted'   AND
                                account_move.company_id in ''' + str(tuple(company_id)) + '''
                                    ''')
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items

    @api.model
    def unreconcile_items(self):
        self._cr.execute('''
                            select count(*) FROM account_move_line l,account_account a
                            where l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                            l.balance != 0 AND a.reconcile IS TRUE ''')
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items this month

    @api.model
    def unreconcile_items_this_month(self, *post):
        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        qry = ''' select count(*) FROM account_move_line l,account_account a
                              where Extract(month FROM l.date) = Extract(month FROM DATE(NOW())) AND
                              Extract(YEAR FROM l.date) = Extract(YEAR FROM DATE(NOW())) AND
                              l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                              l.product_id IS NULL AND
                              l.balance != 0 AND a.reconcile IS F 
                              AND l.''' + states_arg + '''
                              AND  l.company_id in ''' + str(tuple(company_id)) + '''                              
                               '''

        self._cr.execute((''' select count(*) FROM account_move_line l,account_account a
                              where Extract(month FROM l.date) = Extract(month FROM DATE(NOW())) AND
                              Extract(YEAR FROM l.date) = Extract(YEAR FROM DATE(NOW())) AND
                              l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                              l.product_id IS NULL AND
                              l.balance != 0 AND a.reconcile IS TRUE 
                              AND l.%s
                              AND  l.company_id in ''' + str(tuple(company_id)) + '''                              
                               ''') % (states_arg))
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items last month

    @api.model
    def unreconcile_items_last_month(self):

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        self._cr.execute('''  select count(*) FROM account_move_line l,account_account a 
                              where Extract(month FROM l.date) = ''' + str(one_month_ago) + ''' AND
                              l.account_id=a.id AND l.full_reconcile_id IS NULL AND l.balance != 0 AND a.reconcile IS TRUE 
                         ''')
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items this year

    @api.model
    def unreconcile_items_this_year(self, *post):
        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''  select count(*) FROM account_move_line l,account_account a
                                  where Extract(year FROM l.date) = Extract(year FROM DATE(NOW())) AND
                                  l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                                  l.product_id IS NULL AND
                                  l.balance != 0 AND a.reconcile IS TRUE  
                                  AND l.%s
                                  AND  l.company_id in ''' + str(tuple(company_id)) + '''       
                                  ''') % (states_arg))
        record = self._cr.dictfetchall()
        return record

    @api.model
    def click_expense_month(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]
        if start_date:
            self._cr.execute((''' select account_move_line.id from  account_account, account_move_line where 
                                account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null) AND  
                                %s                
                                AND account_move_line.date >= '%s' AND account_move_line.date <= '%s' 
                                AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                                     ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute((''' select account_move_line.id from  account_account, account_move_line where 
                                account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null) AND  
                                %s                
                                AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW()))
                                AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) 
                                AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                                     ''') % (states_arg))

        record = [row[0] for row in self._cr.fetchall()]
        return record

    @api.model
    def click_expense_year(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute((''' select account_move_line.id from  account_account, account_move_line where
                                account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense'  AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null) AND  
                                %s                         
                                AND date >= '%s' AND date <= '%s'                        
                                AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                                ''') %(states_arg, start_date, end_date))
        record = [row[0] for row in self._cr.fetchall()]
        return record

    @api.model
    def click_total_income_month(self, *post):
        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            self._cr.execute(('''select account_move_line.id from account_account, account_move_line where
                                    account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                                   AND %s
                                   AND account_move_line.date >= '%s' AND  account_move_line.date <= '%s' 
                                   AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 
    
                                         ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute(('''select account_move_line.id from account_account, account_move_line where
                                account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                               AND %s
                               AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW())) 
                               AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) 
                               AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 

                                     ''') % (states_arg))

        record = [row[0] for row in self._cr.fetchall()]
        return record

    @api.model
    def click_total_income_year(self, *post):

        company_id = self.get_current_company_value()

#         states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute((''' select account_move_line.id from account_account, account_move_line where                           
                             account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                             AND %s
                          AND  date >= '%s' AND date <= '%s'  
                          AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                        ''') %(states_arg, start_date, end_date))
        record = [row[0] for row in self._cr.fetchall()]
        return record

    @api.model
    def click_profit_income_month(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        
        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            self._cr.execute(('''select account_move_line.id from  account_account, account_move_line where 
                                           account_move_line.account_id = account_account.id AND
                                           %s AND
                                           (account_account.internal_group = 'income' or    
                                           (account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null)     )) 
                                           AND account_move_line.date >= '%s' AND account_move_line.date <= '%s' 
                                           AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''        
                                            ''') % (states_arg,start_date , end_date))
        else:
            self._cr.execute(('''select account_move_line.id from  account_account, account_move_line where 
                                           account_move_line.account_id = account_account.id AND
                                           %s AND
                                           (account_account.internal_group = 'income' or    
                                           (account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null)     )) 
                                           AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW())) 
                                           AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW()))   
                                           AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''        
                                            ''') % (states_arg))

        profit = [row[0] for row in self._cr.fetchall()]
        return profit

    @api.model
    def click_profit_income_year(self, *post):
        print("___________________________    ffffff",post)
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute(('''select account_move_line.id from  account_account, account_move_line where 
                                            account_move_line.account_id = account_account.id AND
                                            %s AND
                                           (account_account.internal_group = 'income' or    
                                           (account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null)))       
                                          AND  account_move_line.date >= '%s' AND account_move_line.date <= '%s'  
                                           AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''           
                                ''') %(states_arg, start_date, end_date))
        profit = [row[0] for row in self._cr.fetchall()]
        return profit

    @api.model
    def click_bill_year(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute(('''select account_move.id from account_move where move_type ='in_invoice'
                               AND  %s                              
                              AND  account_move_line.date >= '%s' AND account_move_line.date <= '%s'  
                               AND account_move.company_id in ''' + str(tuple(company_id)) + '''      
                                ''') %(states_arg, start_date, end_date))
        record_supplier_current_year = [row[0] for row in self._cr.fetchall()]
        return record_supplier_current_year

    @api.model
    def click_bill_year_paid(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute(('''select account_move.id from account_move where move_type ='in_invoice'
                                       AND   %s
                                       AND  payment_state = 'paid'
                                      AND  account_move_line.date >= '%s' AND account_move_line.date <= '%s'  
                                       AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                ''') %(states_arg, start_date, end_date))
        result_paid_supplier_invoice_current_year = [row[0] for row in self._cr.fetchall()]
        return result_paid_supplier_invoice_current_year

    @api.model
    def click_invoice_year_paid(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute(('''select account_move.id from account_move where move_type ='out_invoice'
                                       AND   %s
                                       AND payment_state = 'paid'
                              AND  account_move.invoice_date >= '%s' AND account_move.invoice_date <= '%s'  
                                       AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                ''') %(states_arg, start_date, end_date))
        record_paid_customer_invoice_current_year = [row[0] for row in self._cr.fetchall()]
        return record_paid_customer_invoice_current_year

    @api.model
    def click_invoice_year(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted' """
        start_date, end_date = self._get_financial_year()

        self._cr.execute(('''select account_move.id  from account_move where move_type ='out_invoice'
                               AND   %s                               
                              AND  account_move.invoice_date >= '%s' AND account_move.invoice_date <= '%s'  
                               AND account_move.company_id in ''' + str(tuple(company_id)) + '''           
                                ''') %(states_arg, start_date, end_date))
        record_customer_current_year = [row[0] for row in self._cr.fetchall()]
        return record_customer_current_year

    @api.model
    def click_bill_month(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        self._cr.execute(('''select account_move.id from account_move where move_type ='in_invoice'
                                            AND   %s
                                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                        ''') % (states_arg))
        bill_month = [row[0] for row in self._cr.fetchall()]
        return bill_month

    @api.model
    def click_bill_month_paid(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        self._cr.execute(('''select account_move.id from account_move where move_type ='in_invoice'
                                            AND   %s
                                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND payment_state = 'paid'
                                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                        ''') % (states_arg))
        result_paid_supplier_invoice_current_month = [row[0] for row in self._cr.fetchall()]
        return result_paid_supplier_invoice_current_month

    @api.model
    def click_invoice_month_paid(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        self._cr.execute(('''select account_move.id from account_move where move_type ='out_invoice'
                                            AND   %s
                                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND payment_state = 'paid'
                                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                        ''') % (states_arg))
        record_paid_customer_invoice_current_month = [row[0] for row in self._cr.fetchall()]
        return record_paid_customer_invoice_current_month

    @api.model
    def click_invoice_month(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ account_move.state in ('posted', 'draft')"""
#         else:
        states_arg = """ account_move.state = 'posted'"""
        self._cr.execute(('''select account_move.id from account_move where move_type ='out_invoice'
                                    AND   %s                               
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in ''' + str(tuple(company_id)) + '''           
                                ''') % (states_arg))
        record_customer_current_month = [row[0] for row in self._cr.fetchall()]
        return record_customer_current_month

    @api.model
    def click_unreconcile_month(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        qry = ''' select count(*) FROM account_move_line l,account_account a
                              where Extract(month FROM l.date) = Extract(month FROM DATE(NOW())) AND
                              Extract(YEAR FROM l.date) = Extract(YEAR FROM DATE(NOW())) AND
                              l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                              l.product_id IS NULL AND
                              l.balance != 0 AND a.reconcile IS F 
                              AND l.''' + states_arg + '''
                              AND  l.company_id in ''' + str(tuple(company_id)) + '''                              
                               '''

        self._cr.execute((''' select l.id FROM account_move_line l,account_account a
                              where Extract(month FROM l.date) = Extract(month FROM DATE(NOW())) AND
                              Extract(YEAR FROM l.date) = Extract(YEAR FROM DATE(NOW())) AND
                              l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                              l.product_id IS NULL AND
                              l.balance != 0 AND a.reconcile IS TRUE 
                              AND l.%s
                              AND  l.company_id in ''' + str(tuple(company_id)) + '''                              
                               ''') % (states_arg))
        record = [row[0] for row in self._cr.fetchall()]
        return record

    @api.model
    def click_unreconcile_year(self, *post):
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute(('''  select l.id FROM account_move_line l,account_account a
                                  where date >= '%s' AND date <= '%s' AND
                                  l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                                  l.product_id IS NULL AND
                                  l.balance != 0 AND a.reconcile IS TRUE  
                                  AND l.%s
                                  AND  l.company_id in ''' + str(tuple(company_id)) + '''       
                                  ''') %(start_date, end_date, states_arg))
        record = [row[0] for row in self._cr.fetchall()]
        return record

    # function to get unreconcile items last year

    @api.model
    def unreconcile_items_last_year(self):

        self._cr.execute('''  select count(*) FROM account_move_line l,account_account a
                                      where Extract(year FROM l.date) = Extract(year FROM DATE(NOW())) - 1 AND
                                      l.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                                      l.balance != 0 AND a.reconcile IS TRUE
                                      ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total income

    @api.model
    def month_income(self):

        self._cr.execute(''' select sum(debit) as debit , sum(credit) as credit  from account_move, account_account,account_move_line
                            where  account_move.move_type = 'entry'  AND account_move.state = 'posted' AND  account_move_line.account_id=account_account.id AND
                             account_account.internal_group='income'
                              AND to_char(DATE(NOW()), 'MM') = to_char(account_move_line.date, 'MM')
                              ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total income this month

    @api.model
    def month_income_this_month(self, *post):
        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            self._cr.execute(('''select sum(debit) as debit, sum(credit) as credit from account_account, account_move_line where
                            account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                           AND %s
                            AND account_move_line.date >= '%s' AND account_move_line.date <= '%s'  
                           AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 
                             ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute(('''select sum(debit) as debit, sum(credit) as credit from account_account, account_move_line where
                                account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                               AND %s
                               AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW())) 
                               AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) 
                               AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' 
    
                                     ''') % (states_arg))

        record = self._cr.dictfetchall()
        return record

    @api.model
    def profit_income_this_month(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            self._cr.execute(('''select sum(debit) - sum(credit) as profit, account_account.internal_group from  account_account, account_move_line where 
                                        account_move_line.account_id = account_account.id AND
                                        %s AND
                                        (account_account.internal_group = 'income' or    
                                        (account_account.internal_group = 'expense' AND (account_account.is_stock_account is false OR account_account.is_stock_account is null) )) 
                                        AND account_move_line.date >= '%s' AND account_move_line.date <= '%s'  
                                        AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''        
                                        group by internal_group 
                                         ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute(('''select sum(debit) - sum(credit) as profit, account_account.internal_group from  account_account, account_move_line where 
                                      
                                        account_move_line.account_id = account_account.id AND
                                        %s AND
                                        (account_account.internal_group = 'income' or    
                                        (account_account.internal_group = 'expense' AND (account_account.is_stock_account is false OR account_account.is_stock_account is null) )) 
                                        AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW())) 
                                        AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW()))   
                                        AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''        
                                        group by internal_group 
                                         ''') % (states_arg))

        income = self._cr.dictfetchall()
        profit = [item['profit'] for item in income]
        internal_group = [item['internal_group'] for item in income]
        net_profit = True
        loss = True
        if profit and profit == 0:
            if (-profit[1]) > (profit[0]):
                net_profit = -profit[1] - profit[0]
            elif (profit[1]) > (profit[0]):
                net_profit = -profit[1] - profit[0]
            else:
                net_profit = -profit[1] - profit[0]

        return profit

    def get_current_company_value(self):

        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]

        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids

    @api.model
    def profit_income_this_year(self, *post):
        print("_________________   inocmmeeeeee")
        company_id = self.get_current_company_value()
        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute(('''select sum(debit) - sum(credit) as profit, account_account.internal_group from  account_account, account_move_line where 
                                        
                                         account_move_line.account_id = account_account.id AND
                                         %s AND
                                        (account_account.internal_group = 'income' or    
                                        (account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null) ) )   
                                        AND account_move_line.date >= '%s' AND  account_move_line.date <= '%s'  
                                        AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''           
                                        group by internal_group 
                                         ''') % (states_arg, start_date, end_date ))
        income = self._cr.dictfetchall()
        profit = [item['profit'] for item in income]
        internal_group = [item['internal_group'] for item in income]
        net_profit = True
        loss = True

        if profit and profit == 0:
            if (-profit[1]) > (profit[0]):
                net_profit = -profit[1] - profit[0]
            elif (profit[1]) > (profit[0]):
                net_profit = -profit[1] - profit[0]
            else:
                net_profit = -profit[1] - profit[0]

        return profit

    # function to get total income last month

    @api.model
    def month_income_last_month(self):

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        self._cr.execute('''
                            select sum(debit) as debit, sum(credit) as credit from  account_account, 
        account_move_line where 
         account_move_line.account_id = account_account.id 
        AND account_account.internal_group = 'income' AND 
        account_move_line.parent_state = 'posted'  
        AND Extract(month FROM account_move_line.date) = ''' + str(one_month_ago) + '''
        ''')

        record = self._cr.dictfetchall()

        return record

    # function to get total income this year

    @api.model
    def month_income_this_year(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute((''' select sum(debit) as debit, sum(credit) as credit from account_account, account_move_line where                           
                             account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                             AND %s
                            AND account_move_line.date >= '%s' AND  account_move_line.date <= '%s'  
                          AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                         ''') % (states_arg, start_date, end_date ))
        record = self._cr.dictfetchall()
        return record

    # function to get total income last year

    @api.model
    def month_income_last_year(self):

        self._cr.execute(''' select sum(debit) as debit, sum(credit) as credit from  account_account, account_move_line where
                            account_move_line.parent_state = 'posted' 
                            AND  account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                            AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW())) - 1
                         ''')
        record = self._cr.dictfetchall()
        return record

    # function to get currency

    @api.model
    def get_currency(self):
        company_ids = self.get_current_company_value()
        if 0 in company_ids:
            company_ids.remove(0)
        current_company_id = company_ids[0]
        current_company = self.env['res.company'].browse(current_company_id)
        default = current_company.currency_id or self.env.ref('base.main_company').currency_id
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
        lang = lang.replace("_", '-')
        currency = {'position': default.position, 'symbol': default.symbol, 'language': lang}
        return currency

    # function to get total expense

    @api.model
    def month_expense(self):

        self._cr.execute(''' select sum(debit) as debit , sum(credit) as credit from account_move, account_account,account_move_line
                            where account_move.move_type = 'entry'  AND account_move.state = 'posted' AND   account_move_line.account_id=account_account.id AND
                             account_account.internal_group='expense' 
                             AND to_char(DATE(NOW()), 'MM') = to_char(account_move_line.date, 'MM')
                             ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total expense this month

    @api.model
    def month_expense_this_month(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""

        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            self._cr.execute((''' select sum(debit) as debit, sum(credit) as credit from  account_account, account_move_line where 
                            
                                account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null) AND   
                                %s                
                                AND account_move_line.date >= '%s' AND account_move_line.date <= '%s' 
                                AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                                     ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute((''' select sum(debit) as debit, sum(credit) as credit from  account_account, account_move_line where 
                            
                                account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null) AND   
                                %s                
                                AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW()))
                                AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) 
                                AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
    
    
                                     ''') % (states_arg))

        record = self._cr.dictfetchall()
        return record

    # function to get total expense this year

    @api.model
    def month_expense_this_year(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
#             states_arg = """ parent_state in ('posted', 'draft')"""
#         else:
        states_arg = """ parent_state = 'posted'"""
        start_date, end_date = self._get_financial_year()

        self._cr.execute((''' select sum(debit) as debit, sum(credit) as credit from  account_account, account_move_line where
                        
                            account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense' AND  (account_account.is_stock_account is false OR account_account.is_stock_account is null) AND  
                            %s                         
                            AND account_move_line.date >= '%s' AND  account_move_line.date <= '%s'  
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''



                         ''') % (states_arg, start_date, end_date ))
        record = self._cr.dictfetchall()
        return record

    @api.model
    def bank_balance(self, *post):

        company_id = self.get_current_company_value()

        states_arg = ""
#         if post != ('posted',):
        states_arg = """ parent_state = 'posted'"""
#         else:
#             states_arg = """ parent_state in ('posted', 'draft')"""

        start_date = False
        if len(post) > 1:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            self._cr.execute((''' select account_account.name as name, sum(balance) as balance,
                                min(account_account.id) as id from account_move_line left join
                                account_account on account_account.id = account_move_line.account_id where
                                account_account.account_type = 'asset_cash'
                                AND %s
                                AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' AND
                                account_move_line.date >= '%s' AND account_move_line.date <= '%s'  
                                group by account_account.name
                                                       
                                ''') % (states_arg, start_date, end_date))
        else:
            self._cr.execute((''' select account_account.name as name, sum(balance) as balance,
                            min(account_account.id) as id from account_move_line left join
                            account_account on account_account.id = account_move_line.account_id where
                            account_account.account_type = 'asset_cash'
                            AND %s
                            AND account_move_line.company_id in ''' + str(tuple(company_id)) + '''
                            group by account_account.name
                                                   
                            ''') % (states_arg))


        record = self._cr.dictfetchall()
        banks = [item['name'] for item in record]
        # bank_name = [rec['en_US'] for rec in banks]
        banking = [item['balance'] for item in record]

        bank_ids = [item['id'] for item in record]

        records = {
            'banks': banks,
            'banking': banking,
            'bank_ids': bank_ids
        }
        return records


    @api.model
    def get_salary_lines(self, *post):

        company_id = self.get_current_company_value()

        start_date = False
        if len(post) > 1:
            start_date = post[0]
            end_date = post[1]

        department_dict = {}
        
        departments = self.env['hr.employee'].search([]).mapped('department_id')

        if start_date:
#             self._cr.execute((''' select account_account.name as name, sum(balance) as balance,
#                                 min(account_account.id) as id from account_move_line left join
#                                 account_account on account_account.id = account_move_line.account_id where
#                                 account_account.account_type = 'asset_cash'
#                                 AND %s
#                                 AND account_move_line.company_id in ''' + str(tuple(company_id)) + ''' AND
#                                 account_move_line.date >= '%s' AND account_move_line.date <= '%s'  
#                                 group by account_account.name
#                                                        
#                                 ''') % (states_arg, start_date, end_date))

            
            for dept in departments:
                department_dict[dept.id] = {'name': dept.name, 'salary': 0.0, 'dept_id': dept.id}
                payslip_lines = self.env['hr.payslip.line'].search([
                    ('slip_id.date_to', '>=', start_date),
                    ('slip_id.date_to', '<=', end_date),
                    ('slip_id.state', 'in', ['done', 'paid']),
                    ('employee_id.department_id', '=', dept.id),
                    ('code', '=', 'NET')
                ])
                if payslip_lines:
                    department_dict[dept.id]['salary'] += sum(i.total for i in payslip_lines)

        else:
            for dept in departments:
                department_dict[dept.id] = {'name': dept.name, 'salary': 0.0, 'dept_id': dept.id}
                payslip_lines = self.env['hr.payslip.line'].search([
                    ('slip_id.state', 'in', ['done', 'paid']),
                    ('employee_id.department_id', '=', dept.id),
                    ('code', '=', 'NET')
                ])
                if payslip_lines:
                    department_dict[dept.id]['salary'] += sum(i.total for i in payslip_lines)

        lines = []
        
        for dept in department_dict:
            lines.append(department_dict[dept])
        return lines


    @api.model
    def click_salary_lines(self, *post):

        company_id = self.get_current_company_value()

        dept_id = int(post[0])

        start_date = False
        if len(post) > 2:
            start_date = post[1]
            end_date = post[2]
        if start_date:
                payslip_lines = self.env['hr.payslip.line'].search([
                    ('slip_id.date_to', '>=', start_date),
                    ('slip_id.date_to', '<=', end_date),
                    ('slip_id.state', 'in', ['done', 'paid']),
                    ('employee_id.department_id', '=', dept_id),
                    ('code', '=', 'NET')
                ])
        else:
                payslip_lines = self.env['hr.payslip.line'].search([
                    ('slip_id.state', 'in', ['done', 'paid']),
                    ('employee_id.department_id', '=', dept_id),
                    ('code', '=', 'NET')
                ])
                
                
        return {
            'type': 'ir.actions.act_window',
            'name': _("Payslip"),
            'res_model': 'hr.payslip.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', payslip_lines.ids)],
            'views': [(self.env.ref('ki_accounting_dashboard_extends.view_hr_payslip_line_tree_dashboard').id, 'tree'), (False, 'form')],
        }
        return payslip_lines.ids



    @api.model
    def get_product_counts(self, *post):

        company_id = self.get_current_company_value()

        start_date = False
        if len(post) > 1:
            start_date = post[0]
            end_date = post[1]

        products = self.env['product.product'].search([('name', 'ilike', 'Cue Bridge')])
        d_lines = []
        if start_date:
            main_order_lines = self.env['sale.order.line'].search([
                ('order_id.state', '=', 'done'),
                ('product_id', 'in', products.ids),
                ('order_id.date_order', '>=', start_date),
                ('order_id.date_order', '<=', end_date),
            ])
            partner_ids = main_order_lines.mapped('partner_id')
            product_ids = main_order_lines.mapped('product_id')
            p_name = []
            p_ids = []
            for partner in partner_ids:
                l = []
                l.append(partner.name)

                for product in product_ids:
                    if product.id not in p_ids:
                        p_name.append(product.name)
                        p_ids.append(product.id)
                    order_lines = main_order_lines.filtered(
                        lambda i: i.partner_id == partner and i.product_id == product
                    )
                    l.append(sum(i.product_uom_qty for i in order_lines))
                d_lines.append(l)
            d_lines.insert(0, ["Customer"] + p_name)
        else:
            main_order_lines = self.env['sale.order.line'].search([
                ('order_id.state', '=', 'done'),
                ('product_id', 'in', products.ids)
            ])
            partner_ids = main_order_lines.mapped('partner_id')
            product_ids = main_order_lines.mapped('product_id')
            p_name = []
            p_ids = []
            for partner in partner_ids:
                l = []
                l.append(partner.name)

                for product in product_ids:
                    if product.id not in p_ids:
                        p_name.append(product.name)
                        p_ids.append(product.id)
                    order_lines = main_order_lines.filtered(
                        lambda i: i.partner_id == partner and i.product_id == product
                    )
                    l.append(sum(i.product_uom_qty for i in order_lines))
                d_lines.append(l)
            d_lines.insert(0, ["Customer"] + p_name)
        return d_lines


    @api.model
    def get_cue_bridge_ul(self, *post):
        print("_______________________________    urrrrrrr")
        company_id = self.get_current_company_value()

        start_date = False
        if len(post) > 1:
            start_date = post[0]
            end_date = post[1]

        p_name = ['Cue Bridge', 'Cue Bridge Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])
        partner_dict = {}

        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
            for line in main_order_lines:
                if line.partner_id not in partner_dict:
                    partner_dict[line.partner_id] = {'qty': 0, 'amount': 0}
                
                partner_dict[line.partner_id]['qty'] += line.quantity
                partner_dict[line.partner_id]['amount'] = partner_dict[line.partner_id]['amount'] + round(line.price_subtotal, 2)
            

        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids)
            ])
            for line in main_order_lines:
                if line.partner_id not in partner_dict:
                    partner_dict[line.partner_id] = {'qty': 0, 'amount': 0}
                
                partner_dict[line.partner_id]['qty'] += line.quantity
                partner_dict[line.partner_id]['amount'] = partner_dict[line.partner_id]['amount'] + round(line.price_subtotal, 2)

        lines = []
        for partner in partner_dict:
            a = partner_dict[partner]
            a.update({'name': partner.name, 'id': partner.id, 'amount': round(a['amount'], 2)})
            lines.append(a)
        newlist = sorted(lines, key=lambda d: d['qty'], reverse=True)
        # newlist = newlist[:10]
        return newlist



    @api.model
    def click_cue_bridge(self, *post):

        company_id = self.get_current_company_value()

        partner_id = int(post[0])
        p_name = ['Cue Bridge', 'Cue Bridge Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])

        start_date = False
        if len(post) > 2:
            start_date = post[1]
            end_date = post[2]
            
            
        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                ('partner_id', '=', partner_id),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('partner_id', '=', partner_id),
                ('product_id', 'in', product.ids),
            ])
            
        return {
            'type': 'ir.actions.act_window',
            'name': _("Invoice Lines"),
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', main_order_lines.ids)],
            'views': [(self.env.ref('ki_accounting_dashboard_extends.view_move_line_tree_dashboard').id, 'tree'), (False, 'form')],
        }

    @api.model
    def click_cue_bridge_total(self, *post):

        company_id = self.get_current_company_value()
        print("_______________   posrttt ",post)
        # partner_id = int(post[0])
        p_name = ['Cue Bridge', 'Cue Bridge Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])
        print("_____________   priddddd0,p0",product)
        start_date = False
        if len(post) > 2:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                # ('partner_id', '=', partner_id),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])

        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                # ('partner_id', '=', partner_id),
                ('product_id', 'in', product.ids),
            ])
        return {
            'type': 'ir.actions.act_window',
            'name': _("Invoice Lines"),
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', main_order_lines.ids)],
            'views': [(self.env.ref('ki_accounting_dashboard_extends.view_move_line_tree_dashboard').id, 'tree'),
                      (False, 'form')],
        }

    @api.model
    def get_cue_bridge_plus_ul(self, *post):

        company_id = self.get_current_company_value()

        start_date = False
        if len(post) > 1:
            start_date = post[0]
            end_date = post[1]

        p_name = ['Cue Bridge Plus', 'Cue Bridge Plus Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])

        partner_dict = {}

        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
            for line in main_order_lines:
                if line.partner_id not in partner_dict:
                    partner_dict[line.partner_id] = {'qty': 0, 'amount': 0}
                
                partner_dict[line.partner_id]['qty'] += line.quantity
                partner_dict[line.partner_id]['amount'] = partner_dict[line.partner_id]['amount'] + round(line.price_subtotal, 2)
            

        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids)
            ])
            for line in main_order_lines:
                if line.partner_id not in partner_dict:
                    partner_dict[line.partner_id] = {'qty': 0, 'amount': 0}
                
                partner_dict[line.partner_id]['qty'] += line.quantity
                partner_dict[line.partner_id]['amount'] = partner_dict[line.partner_id]['amount'] + round(line.price_subtotal, 2)

        lines = []
        for dept in partner_dict:
            a = partner_dict[dept]
            a.update({'name': dept.name, 'id': dept.id, 'amount': round(a['amount'], 2)})
            lines.append(a)
        newlist = sorted(lines, key=lambda d: d['qty'], reverse=True)
        # newlist = newlist[:10]
        return newlist


    @api.model
    def click_cue_bridge_plus(self, *post):

        company_id = self.get_current_company_value()

        partner_id = int(post[0])
        p_name = ['Cue Bridge Plus', 'Cue Bridge Plus Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])

        start_date = False
        if len(post) > 2:
            start_date = post[1]
            end_date = post[2]
            
            
        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                ('partner_id', '=', partner_id),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('partner_id', '=', partner_id),
                ('product_id', 'in', product.ids),
            ])
            
        return {
            'type': 'ir.actions.act_window',
            'name': _("Invoice Lines"),
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', main_order_lines.ids)],
            'views': [(self.env.ref('ki_accounting_dashboard_extends.view_move_line_tree_dashboard').id, 'tree'), (False, 'form')],
        }



    @api.model
    def total_click_cue_bridge_plus(self, *post):

        company_id = self.get_current_company_value()

        # partner_id = int(post[0])
        p_name = ['Cue Bridge Plus', 'Cue Bridge Plus Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])

        start_date = False
        if len(post) > 2:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                # ('partner_id', '=', partner_id),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                # ('partner_id', '=', partner_id),
                ('product_id', 'in', product.ids),
            ])

        return {
            'type': 'ir.actions.act_window',
            'name': _("Invoice Lines"),
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', main_order_lines.ids)],
            'views': [(self.env.ref('ki_accounting_dashboard_extends.view_move_line_tree_dashboard').id, 'tree'),
                      (False, 'form')],
        }
    
    @api.model
    def get_cue_bridge_max_ul(self, *post):

        company_id = self.get_current_company_value()

        start_date = False
        if len(post) > 1:
            start_date = post[0]
            end_date = post[1]

        p_name = ['Cue Bridge Max', 'Cue Bridge Max Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])

        partner_dict = {}

        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
            for line in main_order_lines:
                if line.partner_id not in partner_dict:
                    partner_dict[line.partner_id] = {'qty': 0, 'amount': 0}
                
                partner_dict[line.partner_id]['qty'] += line.quantity
                partner_dict[line.partner_id]['amount'] = partner_dict[line.partner_id]['amount'] + round(line.price_subtotal, 2)
            

        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids)
            ])
            for line in main_order_lines:
                if line.partner_id not in partner_dict:
                    partner_dict[line.partner_id] = {'qty': 0, 'amount': 0}
                
                partner_dict[line.partner_id]['qty'] += line.quantity
                partner_dict[line.partner_id]['amount'] = partner_dict[line.partner_id]['amount'] + round(line.price_subtotal, 2)

        lines = []
        for dept in partner_dict:
            a = partner_dict[dept]
            a.update({'name': dept.name, 'id': dept.id, 'amount': round(a['amount'], 2)})
            lines.append(a)
        newlist = sorted(lines, key=lambda d: d['qty'], reverse=True)
        # newlist = newlist[:10]
        return newlist

    @api.model
    def click_cue_bridge_max(self, *post):

        company_id = self.get_current_company_value()

        partner_id = int(post[0])
        p_name = ['Cue Bridge Max', 'Cue Bridge Max Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])

        start_date = False
        if len(post) > 2:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                ('partner_id', '=', partner_id),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('partner_id', '=', partner_id),
                ('product_id', 'in', product.ids),
            ])
            
        return {
            'type': 'ir.actions.act_window',
            'name': _("Invoice Lines"),
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', main_order_lines.ids)],
            'views': [(self.env.ref('ki_accounting_dashboard_extends.view_move_line_tree_dashboard').id, 'tree'), (False, 'form')],
        }

    @api.model
    def total_click_cue_bridge_max(self, *post):
        print("__________________cccc maxx")
        company_id = self.get_current_company_value()

        # partner_id = int(post[0])
        p_name = ['Cue Bridge Max', 'Cue Bridge Max Demo']
        product = self.env['product.product'].search([('name', 'in', p_name)])

        start_date = False
        if len(post) > 2:
            start_date = post[1]
            end_date = post[2]

        if start_date:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                ('product_id', 'in', product.ids),
                # ('partner_id', '=', partner_id),
                ('move_id.invoice_date', '>=', start_date),
                ('move_id.invoice_date', '<=', end_date),
            ])
        else:
            main_order_lines = self.env['account.move.line'].search([
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', '=', 'out_invoice'),
                # ('partner_id', '=', partner_id),
                ('product_id', 'in', product.ids),
            ])

        return {
            'type': 'ir.actions.act_window',
            'name': _("Invoice Lines"),
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', main_order_lines.ids)],
            'views': [(self.env.ref('ki_accounting_dashboard_extends.view_move_line_tree_dashboard').id, 'tree'),
                      (False, 'form')],
        }
