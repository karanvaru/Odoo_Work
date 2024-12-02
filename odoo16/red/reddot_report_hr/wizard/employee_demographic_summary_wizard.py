import base64
import io
from odoo.tools.misc import xlwt
from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta


class EmployeeDemographicSummaryWizard(models.TransientModel):
    _name = "employee.demographic.summary.wizard"

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

    def update_department_count_iterative(self, department, department_dct):
        if department['department_id'] != False:
            department_id = department['department_id'][0]
            count = department['department_id_count']
            department_browse = self.env['hr.department'].browse(department_id)

            if not department_browse.parent_id:
                if department_browse not in department_dct:
                    department_dct[department_browse] = 0
                department_dct[department_browse] += count

            # department_browse = self.env['hr.department'].browse(department_id)
            while department_browse.parent_id:
                parent_id = department_browse.parent_id
                if not parent_id.parent_id:
                    if parent_id not in department_dct:
                        department_dct[parent_id] = 0
                    department_dct[parent_id] += count
                department_browse = department_browse.parent_id

    def generate_employee_demographic_summary_report(self, start_date, end_date):
        today_date = fields.Date.context_today(self)

        filename = 'Employee_Demographic_Report'
        filename = filename + '_' + today_date.strftime("%d/%m/%Y")

        workbook = xlwt.Workbook()
        header_style = xlwt.easyxf(
            "font: height 00,name Arial; align: horiz center, vert center;font: color black; font:bold True; ")
        table_header = xlwt.easyxf("""
            align: horiz left ;font: color black; font:bold True;font: name Times New Roman,italic off, height 200;
            pattern: pattern solid, fore_color gray25;
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
            borders:
                top_color black, bottom_color black, right_color black, left_color black,
                left thin, right thin, top thin, bottom thin; 
        """)
        title_style1_table_head_right = xlwt.easyxf("""
            align: horiz right ;font: color black; font:bold True;font: name Times New Roman,italic off, height 200;
            borders:
                top_color black, bottom_color black, right_color black, left_color black,
                left thin, right thin, top thin, bottom thin; 
        """)

        sheet = workbook.add_sheet('sheet1')
        label = 'Employee Demographics Report'

        row = 0
        sheet.write_merge(row, row + 1, 0, 7, label, header_style)
        sheet.row(row).height = 300

        #         domain = [
        #             ('first_contract_date', '>=', start_date),
        #             ('first_contract_date', '<=', end_date),
        #         ]
        company_domain = []
        if self.company_ids:
            company_domain.append(('company_id', 'in', self.company_ids.ids))
        employee_ids = self.env['hr.employee'].with_context(active_test=False).sudo().search(company_domain)
        contract_results = self.env['hr.employee'].sudo().search(company_domain)

        turn_over_rate = {}
        total_emp = 0
        male_count = 0
        female_count = 0
        emp_dct = {'New': [], 'Resigned': []}
        for rec in employee_ids:
            if rec.company_id not in turn_over_rate:
                turn_over_rate[rec.company_id] = {'join': 0, 'resigned': 0}

            if rec.active:
                total_emp += 1
                if rec.gender == 'male':
                    male_count += 1
                if rec.gender == 'female':
                    female_count += 1
                if rec.first_contract_date:
                    if rec.first_contract_date >= start_date and rec.first_contract_date <= end_date:
                        turn_over_rate[rec.company_id]['join'] += 1
                        emp_dct['New'].append(rec)
            if rec.departure_date:
                if rec.departure_date >= start_date and rec.departure_date <= end_date:
                    turn_over_rate[rec.company_id]['resigned'] += 1
                    emp_dct['Resigned'].append(rec)

        row += 3
        sheet.write(row, 0, "Start Date", title_style1_table_head_left)
        sheet.write(row, 1, start_date, title_style_right_date)
        sheet.write(row, 2, "End Date", title_style1_table_head_left)
        sheet.write(row, 3, end_date, title_style_right_date)
        head_col = 0
        row += 2

        sheet.write(row, head_col, 'Total No of Employees', title_style1_table_head_left)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, total_emp, title_style1_table_head_right)
        row += 1
        sheet.write(row, head_col, 'Female Head Count', title_style1_table_head_left)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, female_count, title_style1_table_head_right)
        row += 1
        sheet.write(row, head_col, 'Male Head Count', title_style1_table_head_left)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, male_count, title_style1_table_head_right)
        row += 1
        sheet.write(row, head_col, 'New Employees Count', title_style1_table_head_left)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, len(emp_dct['New']), title_style1_table_head_right)
        row += 1
        sheet.write(row, head_col, 'Resigned Employees', title_style1_table_head_left)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, len(emp_dct['Resigned']), title_style1_table_head_right)
        row += 1

        department_count = self.env['hr.employee'].sudo().read_group(
            company_domain,
            fields=['department_id'], groupby=['department_id'])
        row += 2
        sheet.write_merge(row, row, 0, 2, 'Department Wise Distribution', header_style)
        row += 2
        sheet.write(row, head_col, 'Name of Department', table_header)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, 'Count', table_header)
        # sheet.write(row, head_col + 2, 'Company', table_header)
        sheet.col(head_col + 2).width = 10000
        department_dct = {}
        for department in department_count:  # Assuming 'departments' is your list of dictionaries
            self.update_department_count_iterative(department, department_dct)
        for department in department_dct:
            row += 1
            sheet.write(row, head_col, department.name, title_style1_table_head_left)
            sheet.write(row, head_col + 1, department_dct[department], title_style1_table_head_right)

        company_count = self.env['hr.employee'].sudo().read_group(
            company_domain,
            fields=['company_id'], groupby=['company_id'])
        row += 2
        sheet.write_merge(row, row, 0, 2, 'Company Wise Distribution', header_style)
        row += 2
        sheet.write(row, head_col, 'Name of Company', table_header)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, 'Count', table_header)
        for company in company_count:
            row += 1
            if company['company_id'] != False:
                sheet.write(row, head_col, str(company['company_id'][1]), title_style1_table_head_left)
                sheet.write(row, head_col + 1, company['company_id_count'], title_style1_table_head_right)

        row += 3
        sheet.write_merge(row, row, 0, 2, 'Turnover Rates', header_style)
        row += 2
        sheet.write(row, head_col, 'Company Name', table_header)
        sheet.col(head_col).width = 20000
        sheet.write(row, head_col + 1, 'Joined Count', table_header)
        sheet.write(row, head_col + 2, 'Resigned Count', table_header)
        for turn_over in turn_over_rate:
            row += 1
            sheet.write(row, head_col, turn_over.name, title_style1_table_head_left)
            sheet.write(row, head_col + 1, turn_over_rate[turn_over]['join'], title_style1_table_head_right)
            sheet.write(row, head_col + 2, turn_over_rate[turn_over]['resigned'], title_style1_table_head_right)

        for emp in emp_dct:
            row += 3
            label = emp + ' ' + 'Employees'
            sheet.write_merge(row, row, 0, 2, label, header_style)
            row += 2
            sheet.write(row, head_col, 'Employee Name', table_header)
            sheet.write(row, head_col + 1, 'Department ', table_header)
            sheet.write(row, head_col + 2, 'Email Address', table_header)
            sheet.write(row, head_col + 3, 'Company', table_header)
            sheet.write(row, head_col + 4, 'Gender', table_header)
            sheet.write(row, head_col + 5, 'Job Position', table_header)
            sheet.write(row, head_col + 6, 'Line Manager', table_header)
            if emp == 'New':
                sheet.write(row, head_col + 7, 'Joining Date', table_header)
                sheet.write(row, head_col + 8, 'Probation Renewal Date', table_header)
            if emp == 'Resigned':
                sheet.write(row, head_col + 7, 'Reason for Leaving', table_header)
                sheet.write(row, head_col + 8, 'Exit Date', table_header)

            for emp_detail in emp_dct[emp]:
                row += 1
                sheet.write(row, head_col, emp_detail.name, title_style1_table_head_left)
                sheet.write(row, head_col + 1, emp_detail.department_id.name or '', title_style1_table_head_left)
                sheet.write(row, head_col + 2, emp_detail.work_email or '', title_style1_table_head_left)
                sheet.write(row, head_col + 3, emp_detail.company_id.name or '', title_style1_table_head_left)
                sheet.write(row, head_col + 4, emp_detail.gender or '', title_style1_table_head_left)
                sheet.write(row, head_col + 5, emp_detail.job_id.name or '', title_style1_table_head_left)
                sheet.write(row, head_col + 6, emp_detail.parent_id.name or '', title_style1_table_head_left)

                if emp == 'New':
                    sheet.write(row, head_col + 7, emp_detail.first_contract_date or '', title_style_right_date)
                    sheet.write(row, head_col + 8, emp_detail.probation_renewal_date or '', title_style_right_date)
                if emp == 'Resigned':
                    sheet.write(row, head_col + 7, emp_detail.departure_reason_id.name or '',
                                title_style1_table_head_left)
                    sheet.write(row, head_col + 8, emp_detail.departure_date or '', title_style_right_date)

        stream = io.BytesIO()
        workbook.save(stream)
        return stream, filename

    def send_employee_mail(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)
        report, filename = self.generate_employee_demographic_summary_report(start_date, end_date)
        report.seek(0)
        attach_data_report = report.read()
        attachment_data = {
            'name': filename,
            'datas': base64.b64encode(attach_data_report),
            'res_model': 'employee.demographic.summary.wizard',
            'type': 'binary',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)
        template_id = self.env.ref(
            'reddot_report_hr.mail_template_demographics_summary')
        template_id.attachment_ids = attachment
        template_id.email_from = self.env.company.email
        if template_id:
            template_id.with_context(
                attachment_ids=[attachment.id]
            ).send_mail(self.id, force_send=True)

    def action_print_employee_demographic_summary_report(self):
        report, filename = self.generate_employee_demographic_summary_report(self.start_date, self.end_date)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(report.getvalue())
        })
        return attach_id.download()
