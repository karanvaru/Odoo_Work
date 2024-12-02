import calendar
import datetime
from datetime import datetime
from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

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

    @api.model
    def profit_income_between_date(self,**kwargs):
        data_list = []
        if kwargs:
            start_date = kwargs['start_date']
            end_date = kwargs['end_date']
            company_id = self.get_current_company_value()

            states_arg = [('parent_state', 'in', ('posted', 'draft'))]

            domain = [
                ('account_id.internal_group', 'in', ['income', 'expense']),
                ('account_id.is_stock_account', '=', False),
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('company_id', 'in', company_id),
            ] + states_arg

            move_lines = self.env['account.move.line'].search(domain)
            net_profit = 0.0
            for rec in move_lines:
                net_profit += rec.credit
            data_list.append(net_profit)


            states_arg = [('parent_state', '=', 'posted')]  # Default states_arg for 'posted' parent_state
            domain = [
                         ('account_id.internal_group', '=', 'income'),
                         ('account_id.is_stock_account', '=', False),
                         ('date', '>=', start_date),
                         ('date', '<=', end_date),
                         ('company_id', 'in', company_id),
                     ] + states_arg

            move_lines = self.env['account.move.line'].search(domain)
            net_income = 0.0
            for rec in move_lines:
                net_income += rec.credit
            data_list.append(net_income)

            states_arg = [('parent_state', '=', 'posted')]  # Default states_arg for 'posted' parent_state

            domain = [
                         ('account_id.internal_group', '=', 'expense'),
                         ('account_id.is_stock_account', '=', False),
                         ('date', '>=', start_date),
                         ('date', '<=', end_date),
                         ('company_id', 'in', company_id),
                     ] + states_arg

            move_lines = self.env['account.move.line'].search(domain)

            net_expense = 0.0
            for rec in move_lines:
                net_expense += rec.debit
            data_list.append(net_expense)
            return data_list


    def get_financial_quarter_dates(self, year, quarter, fiscal_start_month):
        # Calculate the start month of the quarter
        start_month = (quarter - 1) * 3 + fiscal_start_month

        # Calculate the start and end dates of the quarter
        start_date = datetime(year, start_month, 1)
        end_date = datetime(year, start_month + 2, calendar.monthrange(year, start_month + 2)[1])

        return start_date, end_date

    def quartarly_data(self, post, start_date, end_date):
        company_id = self.get_current_company_value()
        states_arg = ""
        if post != ('posted',):
            states_arg = ('state', 'in', ['posted', 'draft'])
        else:
            states_arg = ('state', '=', 'posted')

        domain = [
            ('move_type', '=', 'out_invoice'),
            (states_arg),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id)
        ]
        customer_invoice_sum = self.search(domain).mapped('amount_total_signed')
        record_customer_q1 = [{'customer_invoice': sum(customer_invoice_sum)}]

        domain = [
            ('move_type', '=', 'in_invoice'),
            (states_arg),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id)
        ]

        supplier_invoice_sum = self.search(domain).mapped('amount_total_signed')
        record_supplier_q1 = [{'supplier_invoice': -sum(supplier_invoice_sum)}]

        invoices = self.search([
            ('move_type', '=', 'out_invoice'),
            ('payment_state', '=', 'paid'),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id)
        ])
        customer_invoice_paid = sum(
            invoice.amount_total_signed - invoice.amount_residual_signed for invoice in invoices)
        record_paid_customer_invoice_q1 = [{'customer_invoice_paid': customer_invoice_paid}]

        domain = [
            ('move_type', '=', 'in_invoice'),
            (states_arg),
            ('payment_state', '=', 'paid'),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id)
        ]
        supplier_invoice_paid_sum = sum(
            move.amount_total_signed - move.amount_residual_signed
            for move in self.env['account.move'].search(domain)
        )
        result_paid_supplier_invoice_q1 = [{'supplier_invoice_paid': supplier_invoice_paid_sum}]

        result_credit_note_q1 = [{'credit_note': 0.0}]
        result_refund_q1 = [{'refund': 0.0}]

        record_paid_customer_credit_q1 = [{'customer_credit_paid': 0.0}]
        result_paid_supplier_refund_q1 = [{'supplier_refund_paid': 0.0}]
        customer_invoice_q1 = [item['customer_invoice'] for item in record_customer_q1]
        supplier_invoice_q1 = [item['supplier_invoice'] for item in record_supplier_q1]
        credit_note_q1 = [item['credit_note'] for item in result_credit_note_q1]
        refund_q1 = [item['refund'] for item in result_refund_q1]

        paid_customer_invoice_q1 = [item['customer_invoice_paid'] for item in
                                    record_paid_customer_invoice_q1]
        paid_supplier_invoice_q1 = [item['supplier_invoice_paid'] for item in
                                    result_paid_supplier_invoice_q1]

        paid_customer_credit_q1 = [item['customer_credit_paid'] for item in
                                   record_paid_customer_credit_q1]
        paid_supplier_refund_q1 = [item['supplier_refund_paid'] for item in
                                   result_paid_supplier_refund_q1]

        return customer_invoice_q1, credit_note_q1, supplier_invoice_q1, refund_q1, paid_customer_invoice_q1, paid_supplier_invoice_q1, paid_customer_credit_q1, paid_supplier_refund_q1

    @api.model
    def get_total_invoice_q1(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 4  # Assuming the fiscal year starts in January

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")
        q1 = self.quartarly_data(post, start_date, end_date)
        return q1

    @api.model
    def get_total_invoice_q2(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 7  # Assuming the fiscal year starts in January

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")
        q2 = self.quartarly_data(post, start_date, end_date)
        return q2

    @api.model
    def get_total_invoice_q3(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 10  # Assuming the fiscal year starts in January

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")
        q3 = self.quartarly_data(post, start_date, end_date)
        return q3

    @api.model
    def get_total_invoice_q4(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 1  # Assuming the fiscal year starts in January

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")
        q4 = self.quartarly_data(post, start_date, end_date)
        return q4

    @api.model
    def invoice_total_paid(self, post, current_year, current_quarter, fiscal_start_month):
        company_id = self.get_current_company_value()
        states_arg = ""
        if post != ('posted',):
            states_arg = ('state', 'in', ['posted', 'draft'])
        else:
            states_arg = ('state', '=', 'posted')

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")

        domain = [
            ('move_type', '=', 'out_invoice'),
            ('payment_state', '=', 'paid'),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id),
            states_arg
        ]

        account_move_ids = self.env['account.move'].search(domain).ids
        record_paid_customer_invoice = [row for row in account_move_ids]

        return record_paid_customer_invoice

    @api.model
    def click_invoice_q1_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 4  # Assuming the fiscal year starts in January
        q1 = self.invoice_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q1

    @api.model
    def click_invoice_q2_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 7  # Assuming the fiscal year starts in January
        q2 = self.invoice_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q2

    @api.model
    def click_invoice_q3_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 10  # Assuming the fiscal year starts in January
        q3 = self.invoice_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q3

    @api.model
    def click_invoice_q4_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 1  # Assuming the fiscal year starts in January
        q4 = self.invoice_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q4

    @api.model
    def invoice_total_invoice(self, post, current_year, current_quarter, fiscal_start_month):
        company_id = self.get_current_company_value()
        states_arg = ""
        if post != ('posted',):
            states_arg = ('state', 'in', ['posted', 'draft'])
        else:
            states_arg = ('state', '=', 'posted')

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")

        domain = [
            ('move_type', '=', 'out_invoice'),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id),
            states_arg
        ]

        account_move_ids = self.env['account.move'].search(domain).ids
        record_customer_q1 = [row for row in account_move_ids]
        return record_customer_q1

    @api.model
    def click_invoice_q1(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 4  # Assuming the fiscal year starts in January
        q1 = self.invoice_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q1

    @api.model
    def click_invoice_q2(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 7  # Assuming the fiscal year starts in January
        q1 = self.invoice_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q1

    @api.model
    def click_invoice_q3(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 10  # Assuming the fiscal year starts in January
        q1 = self.invoice_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q1

    @api.model
    def click_invoice_q4(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 1  # Assuming the fiscal year starts in January
        q1 = self.invoice_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q1

    @api.model
    def supplier_total_paid(self, post, current_year, current_quarter, fiscal_start_month):
        company_id = self.get_current_company_value()
        states_arg = ""
        if post != ('posted',):
            states_arg = ('state', 'in', ['posted', 'draft'])
        else:
            states_arg = ('state', '=', 'posted')

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")
        domain = [
            ('move_type', '=', 'in_invoice'),
            ('payment_state', '=', 'paid'),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id),
            states_arg
        ]
        account_move_ids = self.env['account.move'].search(domain).ids
        result_paid_supplier_invoice_q1 = [row for row in account_move_ids]
        return result_paid_supplier_invoice_q1

    @api.model
    def click_bill_q1_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 4  # Assuming the fiscal year starts in January
        q1 = self.supplier_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q1

    @api.model
    def click_bill_q2_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 7  # Assuming the fiscal year starts in January
        q2 = self.supplier_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q2

    @api.model
    def click_bill_q3_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 10  # Assuming the fiscal year starts in January
        q3 = self.supplier_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q3

    @api.model
    def click_bill_q4_paid(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 1  # Assuming the fiscal year starts in January
        q4 = self.supplier_total_paid(post, current_year, current_quarter, fiscal_start_month)
        return q4

    @api.model
    def supplier_total_invoice(self, post, current_year, current_quarter, fiscal_start_month):
        company_id = self.get_current_company_value()
        states_arg = ""
        if post != ('posted',):
            states_arg = ('state', 'in', ['posted', 'draft'])
        else:
            states_arg = ('state', '=', 'posted')

        quarter_start_date, quarter_end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                                fiscal_start_month)
        start_date = quarter_start_date.strftime("%Y-%m-%d")
        end_date = quarter_end_date.strftime("%Y-%m-%d")

        domain = [
            ('move_type', '=', 'in_invoice'),
            states_arg,
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', 'in', company_id),
        ]

        account_move_ids = self.env['account.move'].search(domain).ids
        record_supplier_q1 = [row for row in account_move_ids]
        return record_supplier_q1

    @api.model
    def click_bill_q1(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 4  # Assuming the fiscal year starts in January
        q1 = self.supplier_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q1

    @api.model
    def click_bill_q2(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 7  # Assuming the fiscal year starts in January
        q2 = self.supplier_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q2

    @api.model
    def click_bill_q3(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 10  # Assuming the fiscal year starts in January
        q3 = self.supplier_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q3

    @api.model
    def click_bill_q4(self, *post):
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        fiscal_start_month = 1  # Assuming the fiscal year starts in January
        q4 = self.supplier_total_invoice(post, current_year, current_quarter, fiscal_start_month)
        return q4
