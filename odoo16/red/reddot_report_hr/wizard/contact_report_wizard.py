import base64
import io
import re
from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlwt


class ContactReportWizard(models.TransientModel):
    _name = "contact.report.wizard"
    _description="Running Contract Report"

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

    def strip_html_tags(self, text):
        if text:
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)

    def generate_contract_report(self, start_date, end_date):
        today_date = fields.Date.context_today(self)

        filename = 'Running_Contract_Report'
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
        title_style_right = xlwt.easyxf("""
            font: name Times New Roman, height 200;align: horiz right;
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

        sheet = workbook.add_sheet('sheet1')
        label = 'Contract Report'

        row = 0
        sheet.write_merge(row, row + 1, 0, 7, label, header_style)
        sheet.row(row).height = 300

        domain = [
            ('date_start', '>=', start_date),
            ('date_start', '<=', end_date),
        ]
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))

        contract_results = self.env['hr.contract'].sudo().search(domain)
        row += 3

        sheet.write(row, 1, "Start Date", title_style1_table_head_left)
        sheet.write(row, 2, start_date, title_style_right_date)
        sheet.write(row, 5, "End Date", title_style1_table_head_left)
        sheet.write(row, 6, end_date, title_style_right_date)
        head_col = 0
        row += 2
        sheet.write(row, head_col, "Contract Name", title_style1_table_head_left)
        sheet.col(head_col).width = 7000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Employee", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Company", title_style1_table_head_left)
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
        sheet.write(row, head_col, "Department", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Start Date", title_style1_table_head_left)
        sheet.col(head_col).width = 4000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'End Date', title_style1_table_head_left)
        sheet.col(head_col).width = 4000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Expiry In (Days)', title_style1_table_head_left)
        sheet.col(head_col).width = 4000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Notes', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        row += 1

        for contract in contract_results:
            col = 0
            sheet.write(row, col, contract.name or '', title_style_left)
            sheet.col(col).width = 7000
            col += 1
            sheet.write(row, col, contract.employee_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, contract.company_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, contract.job_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, contract.employee_id.parent_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, contract.department_id.name or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, contract.date_start or '', title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row, col, contract.date_end or '', title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            expiry_days = ''
            if contract.date_end:
                expiry_days = (contract.date_end - today_date).days
            sheet.write(row, col, expiry_days or '', title_style_right)
            sheet.col(col).width = 4000
            col += 1
            
            note_data = contract.notes
            sheet.write(row, col, self.strip_html_tags(note_data) or '', title_style_left)
            sheet.col(col).width = 10000
            col += 1
            row += 1

        stream = io.BytesIO()
        workbook.save(stream)
        return stream, filename

    def action_print_contract_report(self):
        report, filename = self.generate_contract_report(self.start_date, self.end_date)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(report.getvalue())
        })
        return attach_id.download()

    def send_employee_contract_report_mail(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)
        report, filename = self.generate_contract_report(start_date, end_date)
        report.seek(0)
        attach_data_report = report.read()
        attachment_data = {
            'name': filename,
            'datas': base64.b64encode(attach_data_report),
            'res_model': 'contact.report.wizard',
            'type': 'binary',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)
        template_id = self.env.ref(
            'reddot_report_hr.mail_template_contract_report')
        template_id.attachment_ids = attachment
        template_id.email_from = self.env.company.email
        if template_id:
            template_id.with_context(
                attachment_ids=[attachment.id]
            ).send_mail(self.id, force_send=True)
