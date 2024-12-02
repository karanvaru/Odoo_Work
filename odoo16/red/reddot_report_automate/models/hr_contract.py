from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import base64
import xlwt
from io import BytesIO


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    def contract_generate_excel_report(self, period_days_count, report_conf):
        today = fields.Date.context_today(self)
        conf_contract = self.search([('date_end', '>=', today), ('date_end', '<=', period_days_count)])

        filename = 'Contract_Expiry_Staus_'
        filename = filename + today.strftime("%d/%m/%Y")

        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet("exel", cell_overwrite_ok=True)


        header_style = xlwt.easyxf("""
               font: name Times New Roman, height 300;
               align: horiz center; font: color black; font:bold True;
           """)

        title_style1_table_head_left = xlwt.easyxf("""
                   align: horiz left ;
                   font: name Times New Roman,bold on, italic off, height 200;
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

        title_style_right = xlwt.easyxf("""
                   font: name Times New Roman, height 200;align: horiz right;
                   borders:
                       top_color black, bottom_color black, right_color black, left_color black,
                       left thin, right thin, top thin, bottom thin;
               """)

        title_style_left = xlwt.easyxf("""
                  font: name Times New Roman, height 200;align: horiz left;
                  borders:
                      top_color black, bottom_color black, right_color black, left_color black,
                      left thin, right thin, top thin, bottom thin;
              """)
        for i in range(8):
            worksheet.col(i).width = 5000
        label = 'Contract Expiry In %s Days' % (period_days_count)
        row = 0
        worksheet.write_merge(row, row + 1, 0, 6, label, header_style)

        row += 2

        worksheet.write(row, 0, 'Report Date:')
        worksheet.write(row, 1, today, title_style_right_date)

        row += 2
        head_col = 0

        worksheet.write(row, head_col, "#", title_style1_table_head_left)
        head_col += 1
        worksheet.write(row, head_col, "Employee", title_style1_table_head_left)
        head_col += 1
        worksheet.write(row, head_col, "Department", title_style1_table_head_left)
        head_col += 1
        worksheet.write(row, head_col, "Job Position", title_style1_table_head_left)
        head_col += 1
        worksheet.write(row, head_col, "Company", title_style1_table_head_left)
        head_col += 1
        worksheet.write(row, head_col, "Start Date", title_style1_table_head_left)
        head_col += 1
        worksheet.write(row, head_col, "End Date", title_style1_table_head_left)
        head_col += 1
        worksheet.write(row, head_col, "Expiry In (Days)", title_style1_table_head_left)

        row += 1
        contract_count = 1
        for contract in conf_contract:
            col = 0
            worksheet.write(row, col, contract_count, title_style_right)
            col += 1
            worksheet.write(row, col, contract.employee_id.name, title_style_left)
            worksheet.col(col).width = 6000
            col += 1
            worksheet.write(row, col, contract.department_id.name, title_style_left)
            worksheet.col(col).width = 6000
            col += 1

            worksheet.write(row, col, contract.job_id.name, title_style_left)
            worksheet.col(col).width = 6000
            col += 1

            worksheet.write(row, col, contract.company_id.name, title_style_left)
            worksheet.col(col).width = 6000
            col += 1

            worksheet.write(row, col, contract.date_start, title_style_right_date)
            worksheet.col(col).width = 4000
            col += 1
            worksheet.write(row, col, contract.date_end, title_style_right_date)
            worksheet.col(col).width = 4000
            col += 1

            expiry_days = (contract.date_end - today).days
            worksheet.write(row, col, expiry_days, title_style_right)

            row += 1
            contract_count += 1

        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        contract_sheet = stream.read()

        if conf_contract:
            for rec in conf_contract:
                attachment_data = {
                    'name': filename,
                    'datas': base64.b64encode(contract_sheet),
                    'res_model': 'hr.contract',
                    'type': 'binary',
                    'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
                attachment = self.env['ir.attachment'].create(attachment_data)
                template_id = self.env.ref(
                    'reddot_report_automate.contract_reminder_email_template')
                template_id.attachment_ids = attachment
                if rec.hr_responsible_id:
                    email_to = ','.join([rec.hr_responsible_id.email, rec.employee_id.parent_id.work_email or ''])
                template_id.email_to = email_to
                if template_id:
                    template_id.with_context(
                        attachment_ids=[attachment.id],
                        days=report_conf.period_days
                    ).send_mail(rec.id, force_send=True)

        return

    def action_send_contract_terminate_1_month_mail(self):
        cron_id = self.env.context.get('cron_id')
        report_conf = self.env['report.automation.config'].search([('action_id', '=', cron_id.id)])
        today = date.today()
        if report_conf:
            period_days_count = today + relativedelta(days=report_conf.period_days)
        else:
            period_days_count = today + relativedelta(months=1)

        self.contract_generate_excel_report(period_days_count, report_conf)

    def action_send_contract_terminate_15_days_mail(self):
        cron_id = self.env.context.get('cron_id')
        report_conf = self.env['report.automation.config'].search([('action_id', '=', cron_id.id)])
        today = date.today()
        if report_conf:
            period_days_count = today + relativedelta(days=report_conf.period_days)
        else:
            period_days_count = today + relativedelta(days=15)
        self.contract_generate_excel_report(period_days_count, report_conf)

    def action_send_contract_terminate_7_days_mail(self):
        cron_id = self.env.context.get('cron_id')
        report_conf = self.env['report.automation.config'].search([('action_id', '=', cron_id.id)])
        today = date.today()
        if report_conf:
            period_days_count = today + relativedelta(days=report_conf.period_days)
        else:
            period_days_count = today + relativedelta(days=7)
        self.contract_generate_excel_report(period_days_count, report_conf)



