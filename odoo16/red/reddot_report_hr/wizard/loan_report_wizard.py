import base64
import io
from odoo import models, fields, api, _
from odoo.tools.misc import xlwt


class LoanReportWizard(models.TransientModel):
    _name = "loan.report.wizard"
    _description = "Loan Report"

    start_period = fields.Date(
        string='Start Period:',
        required=True,
    )
    end_period = fields.Date(
        string='End Period',
        required=True,
    )
    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
    )

    department_ids = fields.Many2many(
        "hr.department",
        string="Departments",
    )
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employees",
    )

    loan_state = {
        'draft': 'Draft',
        'request': 'Submit Request',
        'ca_approval': 'Country Accountant Approval',
        'dep_approval': 'Manager Approval',
        'hr_approval': 'HR Approval',
        'cfo_approval': 'CFO Approval',
        'super_approval': 'CLHRO Approval',
        'paid': 'Paid',
        'done': 'Active',
        'close': 'Close',
        'reject': 'Rejected',
        'cancel': 'Cancel'}

    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Submit Request'),
        ('ca_approval', 'Country Accountant Approval'),
        ('dep_approval', 'Manager Approval'),
        ('hr_approval', 'HR Approval'),
        ('cfo_approval', 'CFO Approval'),
        ('super_approval', 'CLHRO Approval'),
        ('paid', 'Paid'),
        ('done', 'Active'),
        ('close', 'Close'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancel'),

    ], string='Status', )


    def action_print_report(self):
        today_date = fields.Date.context_today(self)

        filename = 'Loan_Report'
        filename = filename + '_' + today_date.strftime("%d/%m/%Y")

        workbook = xlwt.Workbook()
        header_style = xlwt.easyxf(
            "font: height 00,name Arial; align: horiz center, vert center;font: color black; font:bold True; ")

        title_style_left = xlwt.easyxf("""
                              font: name Times New Roman, height 200;align: horiz left;
                              borders:
                                  top_color black, bottom_color black, right_color black, left_color black,
                                  left thin, right thin, top thin, bottom thin;
                          """)

        title_style_right_date = xlwt.easyxf("""
                              font: name Times New Roman, height 200;align: horiz right;
                              borders:
                                  top_color black, bottom_color black, right_color black, left_color black,
                                  left thin, right thin, top thin, bottom thin;  
                              """, num_format_str='DD/MM/YYYY')
        title_style1_table_head_left = xlwt.easyxf("""
                              align: horiz left ;font: color black; font:bold True;font: name Times New Roman,italic off, height 200;
                                pattern: pattern solid, fore_color gray25;
                                
                              borders:
                                  top_color black, bottom_color black, right_color black, left_color black,
                                  left thin, right thin, top thin, bottom thin; 
                          """)

        sheet = workbook.add_sheet('sheet1')
        label = 'Loan Report'

        row = 0
        sheet.write_merge(row, row + 1, 0, 14, label, header_style)
        sheet.row(row).height = 300
        company_list = []
        department_list = []
        employee_list = []
        domain = [
            ('start_date', '>=', self.start_period),
            ('start_date', '<=', self.end_period),
        ]
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))

        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))

        if self.state:
            domain.append(('state', '=', self.state))

        emp_loan = self.env['employee.loan'].sudo().search(domain)
        row += 3

        # Filter Section
        sheet.write(row, 1, "Start Date", title_style1_table_head_left)
        sheet.write(row, 2, self.start_period, title_style_right_date)
        sheet.write(row, 5, "End Date", title_style1_table_head_left)
        sheet.write(row, 6, self.end_period, title_style_right_date)

        filter_company = 'All'
        filter_department = 'All'
        filter_employee = 'All'
        filter_status = 'All'

        if self.company_ids:
            filter_company = '\n'.join([i.name for i in self.company_ids])

        if self.department_ids:
            filter_department = '\n'.join([i.name for i in self.department_ids])

        if self.employee_ids:
            filter_employee = '\n'.join([i.name for i in self.employee_ids])

        if self.state:
            filter_status = self.loan_state[self.state]

        row += 1
        sheet.write(row, 1, "Companies", title_style1_table_head_left)
        sheet.write(row, 2, filter_company, title_style_right_date)
        sheet.row(row).height = 300

        row += 1
        sheet.write(row, 1, "Departments", title_style1_table_head_left)
        sheet.write(row, 2, filter_department, title_style_right_date)

        row += 1
        sheet.write(row, 1, "Employees", title_style1_table_head_left)
        sheet.write(row, 2, filter_employee, title_style_right_date)
        sheet.write(row, 5, "Status", title_style1_table_head_left)
        sheet.write(row, 6, filter_status, title_style_right_date)
        row += 1
        # Totals
        loan_given_row = 0
        loan_interest_row = 0
        loan_service_row = 0
        loan_paid_row = 0
        loan_balance_row = 0

        if len(self.company_ids.ids) == 1:
            row += 1
            loan_given_row = row

            sheet.write(row, 1, "Total Loans Given", title_style1_table_head_left)
            #             sheet.write(row, 2, '', title_style_left)

            row += 1
            loan_interest_row = row
            sheet.write(row, 1, "Total Interest", title_style1_table_head_left)
            #             sheet.write(row, 2, '', title_style_left)

            row += 1
            loan_service_row = row
            sheet.write(row, 1, "Total Service Charges", title_style1_table_head_left)
            #             sheet.write(row, 2, '', title_style_left)

            row += 1
            loan_paid_row = row
            sheet.write(row, 1, "Total Loans Paid", title_style1_table_head_left)
            #             sheet.write(row, 2, '', title_style_left)

            row += 1
            loan_balance_row = row
            sheet.write(row, 1, "Total Balance", title_style1_table_head_left)
        #             sheet.write(row, 2, '', title_style_left)

        # Headers
        head_col = 0
        row += 2
        sheet.write(row, head_col, "Company", title_style1_table_head_left)
        sheet.col(head_col).width = 7000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Department", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Employee Name", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Loan Type", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Currency", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Loan Requested Amount", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Loan Terms", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1

        sheet.write(row, head_col, "Start of Loan", title_style1_table_head_left)
        sheet.col(head_col).width = 4000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Planned End of Loan', title_style1_table_head_left)
        sheet.col(head_col).width = 4000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Interest Amount', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Service Charge', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Paid Amount', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Remaining Amount', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Installment Amount', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Last Payment Date', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'End of Loan', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Count of Skips', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Status', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1

        row += 1

        total_loan_given = 0
        total_loan_interest = 0
        total_loan_service = 0
        total_loan_paid = 0
        total_loan_balance = 0

        # Datas
        for loan in emp_loan:
            skip_count = sum(1 for rec in loan.mapped('installment_lines') if rec.is_skip)
            col = 0
            sheet.write(row, col, loan.company_id.name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1
            sheet.write(row, col, loan.department_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, loan.employee_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, loan.loan_type_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, loan.currency_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, loan.loan_amount, title_style_left)
            total_loan_given += loan.loan_amount
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, loan.loan_term, title_style_left)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, loan.start_date or '', title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, loan.end_date or '', title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, loan.interest_amount, title_style_left)
            total_loan_interest += loan.interest_amount
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, loan.service_charge_amount, title_style_left)
            total_loan_service += loan.service_charge_amount
            sheet.col(col).width = 4000
            col += 1

            sheet.write(row, col, loan.paid_amount, title_style_left)
            total_loan_paid += loan.paid_amount
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, loan.remaining_amount, title_style_left)
            total_loan_balance += loan.remaining_amount
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, loan.installment_amount, title_style_left)
            sheet.col(col).width = 4000
            col += 1

            last_payment_date = ''
            last_paid_line = loan.installment_lines.filtered(lambda i: i.payslip_id)
            if last_paid_line:
                last_payment_date = last_paid_line[-1].date

            sheet.write(row, col, last_payment_date,
                        title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, loan.installment_lines[-1].date if loan.installment_lines else '',
                        title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, skip_count, title_style_left)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, self.loan_state.get(loan.state) or '', title_style_left)
            sheet.col(col).width = 4000
            col += 1
            row += 1

        if len(self.company_ids.ids) == 1:
            sheet.write(loan_given_row, 2, total_loan_given, title_style_left)
            sheet.write(loan_interest_row, 2, total_loan_interest, title_style_left)
            sheet.write(loan_service_row, 2, total_loan_service, title_style_left)
            sheet.write(loan_paid_row, 2, total_loan_paid, title_style_left)
            sheet.write(loan_balance_row, 2, total_loan_balance, title_style_left)

        stream = io.BytesIO()

        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()
