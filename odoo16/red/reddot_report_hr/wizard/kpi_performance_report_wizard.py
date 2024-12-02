import base64
import io
import re
from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlwt
import calendar
from datetime import datetime, timedelta


class kpiPerformanceReportWizard(models.TransientModel):
    _name = "kpi.performance.report.wizard"
    _description = "Kpi Performance Report"

    start_date = fields.Date(
        string='Start Date:',
        required=True,
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
    )
    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
    )

    department_ids = fields.Many2many(
        "hr.department",
        string="Department",
    )
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employee",
    )

    job_position_ids = fields.Many2many(
        "hr.job",
        string="Job Positions",
    )

    def action_print_report(self):
        today_date = fields.Date.context_today(self)

        filename = 'Kpi_Performance_Report'
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
        label = 'KPI PERFORMANCE REPORT'

        row = 0
        sheet.write_merge(row, row + 1, 0, 7, label, header_style)
        sheet.row(row).height = 300
        domain = [
            ('employee_score_id.month', '>=', self.start_date),
            ('employee_score_id.month', '<=', self.end_date),
        ]
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))

        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))

        if self.job_position_ids:
            domain.append(('job_id', 'in', self.job_position_ids.ids))

        payroll_data = {}
        payroll_kpi = self.env['payroll.kpi'].sudo().search(domain)
        company_list = []
        department_list = []
        employee_list = []
        job_list = []
        for payroll in payroll_kpi:
            if payroll.employee_id not in payroll_data:
                payroll_data[payroll.employee_id] = {}
                payroll_data[payroll.employee_id]['company'] = payroll.company_id
                payroll_data[payroll.employee_id]['department'] = payroll.department_id
                payroll_data[payroll.employee_id]['job'] = payroll.job_id
                payroll_data[payroll.employee_id]['manager'] = payroll.employee_id.parent_id
                payroll_data[payroll.employee_id]['total_score_achievable'] = payroll.score
                payroll_data[payroll.employee_id]['total_score_achieved'] = payroll.kpi
            else:
                payroll_data[payroll.employee_id]['total_score_achievable'] += payroll.score
                payroll_data[payroll.employee_id]['total_score_achieved'] += payroll.kpi

        row += 3
        sheet.write(row, 1, "Start Date", title_style1_table_head_left)
        sheet.write(row, 2, self.start_date, title_style_right_date)
        sheet.write(row, 5, "End Date", title_style1_table_head_left)
        sheet.write(row, 6, self.end_date, title_style_right_date)
        head_col = 0
        row += 2

        if self.company_ids:
            sheet.write(row, 0, "Companies", title_style1_table_head_left)
            for rec in self.company_ids:
                if rec.name not in company_list:
                    company_list.append(rec.name)
            sheet.write(row, 1, ', '.join(company_list), title_style_left)
        if self.department_ids:
            sheet.write(row, 2, "Department ", title_style1_table_head_left)
            for rec in self.department_ids:
                if rec.name not in department_list:
                    department_list.append(rec.name)
            sheet.write(row, 3, ', '.join(department_list), title_style_left)
        if self.employee_ids:
            sheet.write(row, 4, "Employee ", title_style1_table_head_left)
            for rec in self.employee_ids:
                if rec.name not in employee_list:
                    employee_list.append(rec.name)
            sheet.write(row, 5, ', '.join(employee_list), title_style_left)
        if self.job_position_ids:
            sheet.write(row, 6, "Jobs ", title_style1_table_head_left)
            for rec in self.job_position_ids:
                if rec.name not in job_list:
                    job_list.append(rec.name)
            sheet.write(row, 7, ', '.join(job_list), title_style_left)
        row += 2
        sheet.write(row, head_col, "Company", title_style1_table_head_left)
        sheet.col(head_col).width = 7000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Department", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Employee", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Job Position", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Line Manager", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Total score Achievable ", title_style1_table_head_left)
        sheet.col(head_col).width = 4000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Total Score Achieved', title_style1_table_head_left)
        sheet.col(head_col).width = 4000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Percentage', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        row += 1

        for payroll_d in payroll_data:
            col = 0
            sheet.write(row, col, payroll_data[payroll_d]['company'].name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1
            sheet.write(row, col, payroll_data[payroll_d]['department'].name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, payroll_d.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, payroll_data[payroll_d]['job'].name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, payroll_data[payroll_d]['manager'].name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, payroll_data[payroll_d]['total_score_achievable'] or '', title_style_left)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, payroll_data[payroll_d]['total_score_achieved'] or '', title_style_left)
            sheet.col(col).width = 4000
            col += 1
            percentage = (payroll_data[payroll_d]['total_score_achieved'] * 100) / payroll_data[payroll_d][
                'total_score_achievable']
            sheet.write(row, col, percentage or '', title_style_left)
            sheet.col(col).width = 4000
            col += 1
            row += 1
        stream = io.BytesIO()

        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()

    @api.model
    def get_year_financial(self, start_date, end_date):
        date1 = start_date
        date2 = end_date
        date1 = date1.replace(day=1)
        date2 = date2.replace(day=1)
        months_str = calendar.month_name
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

    def action_print_monthly_report(self):
        today_date = fields.Date.context_today(self)

        filename = 'Kpi_monthly_Performance_Report'
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
        label = 'KPI Monthly PERFORMANCE REPORT'

        row = 0
        sheet.write_merge(row, row + 1, 0, 7, label, header_style)
        sheet.row(row).height = 300
        company_list = []
        department_list = []
        employee_list = []
        job_list = []
        mont_list = self.get_year_financial(self.start_date, self.end_date)

        domain = [
            ('month', '>=', self.start_date),
            ('month', '<=', self.end_date),
        ]
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))

        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))

        if self.job_position_ids:
            domain.append(('job_id', 'in', self.job_position_ids.ids))


        payroll_kpi = self.env['payroll.kpi'].sudo().search(domain)
        payroll_data = {}
        for payroll in payroll_kpi:
            if payroll.employee_id not in payroll_data:
                payroll_data[payroll.employee_id] = {}
                payroll_data[payroll.employee_id]['month'] = {}
                for months in mont_list:
                    if months not in payroll_data[payroll.employee_id]['month']:
                        payroll_data[payroll.employee_id]['month'][months] = {}
                        payroll_data[payroll.employee_id]['company'] = payroll.company_id
                        payroll_data[payroll.employee_id]['department'] = payroll.department_id
                        payroll_data[payroll.employee_id]['job'] = payroll.job_id
                        payroll_data[payroll.employee_id]['manager'] = payroll.employee_id.parent_id
                        payroll_data[payroll.employee_id]['month'][months]['total_score_achievable'] = 0
                        payroll_data[payroll.employee_id]['month'][months]['total_score_achieved'] = 0

        for payroll in payroll_kpi:
            payroll_data[payroll.employee_id]['month'][payroll.month.strftime("%B-%Y")][
                'total_score_achievable'] += payroll.score
            payroll_data[payroll.employee_id]['month'][payroll.month.strftime("%B-%Y")][
                'total_score_achieved'] += payroll.kpi

        row += 3
        sheet.write(row, 1, "Start Date", title_style1_table_head_left)
        sheet.write(row, 2, self.start_date, title_style_right_date)
        sheet.write(row, 5, "End Date", title_style1_table_head_left)
        sheet.write(row, 6, self.end_date, title_style_right_date)
        row += 2
        if self.company_ids:
            sheet.write(row, 0, "Companies", title_style1_table_head_left)
            for rec in self.company_ids:
                if rec.name not in company_list:
                    company_list.append(rec.name)
            sheet.write(row, 1, ', '.join(company_list), title_style_left)
        if self.department_ids:
            sheet.write(row, 2, "Department ", title_style1_table_head_left)
            for rec in self.department_ids:
                if rec.name not in department_list:
                    department_list.append(rec.name)
            sheet.write(row, 3, ', '.join(department_list), title_style_left)
        if self.employee_ids:
            sheet.write(row, 4, "Employee ", title_style1_table_head_left)
            for rec in self.employee_ids:
                if rec.name not in employee_list:
                    employee_list.append(rec.name)
            sheet.write(row, 5, ', '.join(employee_list), title_style_left)
        if self.job_position_ids:
            sheet.write(row, 6, "Jobs ", title_style1_table_head_left)
            for rec in self.job_position_ids:
                if rec.name not in job_list:
                    job_list.append(rec.name)
            sheet.write(row, 7, ', '.join(job_list), title_style_left)

        month_list = self.get_year_financial(self.start_date, self.end_date)
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
        sheet.write(row, head_col, "Employee", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Job Position", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Line Manager", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        for month_header in month_list:
            sheet.write(row, head_col, month_header, title_style1_table_head_left)
            sheet.col(head_col).width = 6000
            sheet.row(row).height = 300
            head_col += 1
        sheet.write(row, head_col, "Avg", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        row += 1

        for payroll in payroll_data:
            col = 0
            sheet.write(row, col, payroll_data[payroll]['company'].name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1

            sheet.write(row, col, payroll_data[payroll]['department'].name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1

            sheet.write(row, col, payroll.name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1

            sheet.write(row, col, payroll_data[payroll]['job'].name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1

            sheet.write(row, col, payroll_data[payroll]['manager'].name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1
            average_value = 0
            average_count = len(payroll_data[payroll]['month'])
            for month_data in payroll_data[payroll]['month']:
                percentage = 0
                if payroll_data[payroll]['month'][month_data]['total_score_achieved']:
                    percentage = (payroll_data[payroll]['month'][month_data]['total_score_achieved'] * 100) / \
                                 payroll_data[payroll]['month'][month_data]['total_score_achievable']
                average_value += percentage
                sheet.write(row, col, percentage, title_style_left)
                sheet.col(col).width = 7000
                col += 1
            avg = average_value / average_count
            sheet.write(row, col, avg or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1
            row += 1
        stream = io.BytesIO()

        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()
