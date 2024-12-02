from odoo import models, fields, api, _

# from odoo.tools import ustr
# import base64
# from dateutil.relativedelta import relativedelta
# from datetime import date
# import xlwt
# from io import BytesIO
# from datetime import datetime


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    # def generate_anniversary_list_excel_report(self):
    #     start_date = date.today().replace(day=1)
    #     end_date = date.today() + relativedelta(day=31)
    #
    #     workbook = xlwt.Workbook(encoding='utf-8')
    #     worksheet = workbook.add_sheet("exel", cell_overwrite_ok=True)
    #
    #     date_format = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
    #                                  left thin, right thin, top thin, bottom thin;", num_format_str='DD/MM/YYYY', )
    #     header_style = xlwt.easyxf("align:horiz center;align:vertical center;font:color black,bold True;")
    #
    #     title_style = xlwt.easyxf(
    #         'align: horiz center;font: bold 1, color black;pattern: pattern solid, fore_color gray25;'"borders: left thin, right thin, top thin, bottom thin;")
    #
    #     detail_style = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
    #                                  left thin, right thin, top thin, bottom thin;", )
    #
    #     for i in range(7):
    #         worksheet.col(i).width = 5000
    #
    #     worksheet.write(1, 1, 'Start Date', detail_style)
    #     worksheet.write(1, 2, start_date, date_format)
    #     worksheet.write(1, 4, 'End Date', detail_style)
    #     worksheet.write(1, 5, end_date, date_format)
    #     # worksheet.write_merge(3, 3, 0, 6, "Upcoming Birthdays ", header_style)
    #
    #     # worksheet.write(5, 1, '#', title_style)
    #     # worksheet.write(5, 2, 'Employee', title_style)
    #     # worksheet.write(5, 3, 'Birth Date', title_style)
    #     # worksheet.write(5, 4, 'Department', title_style)
    #     # worksheet.write(5, 5, 'Manager', title_style)
    #
    #     today = fields.date.today()
    #     employee_data = self.search([])
    #     list_5_year = []
    #     list_10_year = []
    #     list_15_year = []
    #     list_20_year = []
    #     list_25_year = []
    #     birthday_index = 1
    #     birthday_details_row = 6
    #     for employee in employee_data:
    #         if employee.first_contract_date:
    #             join_year = today.year - employee.first_contract_date.year
    #             if join_year == 5:
    #                 list_5_year.append(employee)
    #             if join_year == 10:
    #                 list_10_year.append(employee)
    #             if join_year == 15:
    #                 list_15_year.append(employee)
    #             if join_year == 20:
    #                 list_20_year.append(employee)
    #             if join_year == 25:
    #                 list_25_year.append(employee)
    #
    #         # if employee.birthday:
    #         #     if employee.birthday.month == today.month:
    #         #         worksheet.write(birthday_details_row, 1, birthday_index, detail_style)
    #         #         worksheet.write(birthday_details_row, 2, employee.name, detail_style)
    #         #         worksheet.write(birthday_details_row, 3, employee.birthday, date_format)
    #         #         worksheet.write(birthday_details_row, 4, employee.department_id.name, detail_style)
    #         #         worksheet.write(birthday_details_row, 5, employee.parent_id.name, detail_style)
    #         #         birthday_details_row += 1
    #         #         birthday_index += 1
    #     index_5_year_row = 6
    #     list_5_year_index = 1
    #     index_10_year_row = index_5_year_row
    #     if list_5_year:
    #         worksheet.write_merge(index_5_year_row + 1, index_5_year_row + 1, 0, 6, "5 Year Anniversary", header_style)
    #
    #         worksheet.write(index_5_year_row + 3, 1, '#', title_style)
    #         worksheet.write(index_5_year_row + 3, 2, 'Employee', title_style)
    #         worksheet.write(index_5_year_row + 3, 3, 'Joining Date', title_style)
    #         worksheet.write(index_5_year_row + 3, 4, 'Department', title_style)
    #         worksheet.write(index_5_year_row + 3, 5, 'Manager', title_style)
    #         row_5 = index_5_year_row + 4
    #
    #         for rec in list_5_year:
    #             worksheet.write(row_5, 1, list_5_year_index, detail_style)
    #             worksheet.write(row_5, 2, rec.name, detail_style)
    #             worksheet.write(row_5, 3, rec.first_contract_date, date_format)
    #             worksheet.write(row_5, 4, rec.department_id.name, detail_style)
    #             worksheet.write(row_5, 5, rec.parent_id.name, detail_style)
    #             row_5 += 1
    #             list_5_year_index += 1
    #         index_10_year_row = row_5
    #
    #     index_15_year_row = index_10_year_row
    #     if list_10_year:
    #         worksheet.write_merge(index_10_year_row + 1, index_10_year_row + 1, 0, 6, "10 Year Anniversary",
    #                               header_style)
    #         list_10_year_index = 1
    #         worksheet.write(index_10_year_row + 3, 1, '#', title_style)
    #         worksheet.write(index_10_year_row + 3, 2, 'Employee', title_style)
    #         worksheet.write(index_10_year_row + 3, 3, 'Joining Date', title_style)
    #         worksheet.write(index_10_year_row + 3, 4, 'Department', title_style)
    #         worksheet.write(index_10_year_row + 3, 5, 'Manager', title_style)
    #         row_10 = index_10_year_row + 4
    #         for rec in list_10_year:
    #             worksheet.write(row_10, 1, list_10_year_index, detail_style)
    #             worksheet.write(row_10, 2, rec.name, detail_style)
    #             worksheet.write(row_10, 3, rec.first_contract_date, date_format)
    #             worksheet.write(row_10, 4, rec.department_id.name, detail_style)
    #             worksheet.write(row_10, 5, rec.parent_id.name, detail_style)
    #             list_10_year_index += 1
    #             row_10 += 1
    #         index_15_year_row = row_10
    #     index_20_year_row = index_15_year_row
    #     if list_15_year:
    #         list_15_year_index = 1
    #         worksheet.write_merge(index_15_year_row + 1, index_15_year_row + 2, 0, 6, "15 Year Anniversary",
    #                               header_style)
    #         worksheet.write(index_15_year_row + 3, 1, '#', title_style)
    #         worksheet.write(index_15_year_row + 3, 2, 'Employee', title_style)
    #         worksheet.write(index_15_year_row + 3, 3, 'Joining Date', title_style)
    #         worksheet.write(index_15_year_row + 3, 4, 'Department', title_style)
    #         worksheet.write(index_15_year_row + 3, 5, 'Manager', title_style)
    #         row_15 = index_15_year_row + 4
    #         for rec in list_15_year:
    #             worksheet.write(row_15, 1, list_15_year_index, detail_style)
    #             worksheet.write(row_15, 2, rec.name, detail_style)
    #             worksheet.write(row_15, 3, rec.first_contract_date, date_format)
    #             worksheet.write(row_15, 4, rec.department_id.name, detail_style)
    #             worksheet.write(row_15, 5, rec.parent_id.name, detail_style)
    #
    #             row_15 += 1
    #         list_15_year_index += 1
    #         index_20_year_row = row_15
    #     index_25_year_row = index_20_year_row
    #     if list_20_year:
    #         list_20_year_index = 1
    #         worksheet.write_merge(index_20_year_row + 1, index_20_year_row + 2, 0, 6, "25 Year Anniversary",
    #                               header_style)
    #
    #         worksheet.write(index_20_year_row + 3, 1, '#', title_style)
    #         worksheet.write(index_20_year_row + 3, 2, 'Employee', title_style)
    #         worksheet.write(index_20_year_row + 3, 3, 'Joining Date', title_style)
    #         worksheet.write(index_20_year_row + 3, 4, 'Department', title_style)
    #         worksheet.write(index_20_year_row + 3, 5, 'Manager', title_style)
    #         row_20 = index_20_year_row + 4
    #         for rec in list_20_year:
    #             worksheet.write(row_20, 1, list_20_year_index, detail_style)
    #             worksheet.write(row_20, 2, rec.name, detail_style)
    #             worksheet.write(row_20, 3, rec.first_contract_date, date_format)
    #             worksheet.write(row_20, 4, rec.department_id.name, detail_style)
    #             worksheet.write(row_20, 5, rec.parent_id.name, detail_style)
    #             list_20_year_index += 1
    #             row_20 += 1
    #         index_25_year_row = row_20
    #
    #     if list_25_year:
    #
    #         list_25_year_index = 1
    #         worksheet.write_merge(index_25_year_row + 1, index_25_year_row + 2, 0, 6, "20 Year Anniversary",
    #                               header_style)
    #
    #         worksheet.write(index_25_year_row + 3, 1, '#', title_style)
    #         worksheet.write(index_25_year_row + 3, 2, 'Employee', title_style)
    #         worksheet.write(index_25_year_row + 3, 3, 'Joining Date', title_style)
    #         worksheet.write(index_25_year_row + 3, 4, 'Department', title_style)
    #         worksheet.write(index_25_year_row + 3, 5, 'Manager', title_style)
    #         row_25 = index_25_year_row + 4
    #         for rec in list_25_year:
    #             worksheet.write(row_25, 1, list_25_year_index, detail_style)
    #             worksheet.write(row_25, 2, rec.name, detail_style)
    #             worksheet.write(row_25, 3, rec.first_contract_date, date_format)
    #             worksheet.write(row_25, 4, rec.department_id.name, detail_style)
    #             worksheet.write(row_25, 5, rec.parent_id.name, detail_style)
    #             list_25_year_index += 1
    #             row_25 += 1
    #
    #     stream = BytesIO()
    #     workbook.save(stream)
    #     stream.seek(0)
    #     return stream.read()

    # def action_send_anniversary_reminder(self):
    #     anniversary_list = self.generate_anniversary_list_excel_report()
    #     employee_records = self.search([])
    #
    #     for employee in employee_records:
    #         # Prepare the attachment
    #         attachment_data = {
    #             'name': 'Anniversary Reminders.xlsx',
    #             'datas': base64.b64encode(anniversary_list),
    #             'res_model': 'hr.employee',
    #             'type': 'binary',
    #             'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #         }
    #         attachment = self.env['ir.attachment'].create(attachment_data)
    #
    #         template_id = self.env.ref(
    #             'reddot_report_automate.mail_template_anniversary_reminders')
    #         template_id.attachment_ids = attachment
    #         if template_id:
    #             template_id.with_context(
    #                 email_to=employee.work_email,
    #                 attachment_ids=[attachment.id]
    #             ).send_mail(employee.id, force_send=True)

    # def generate_birthday_list_excel_report(self):
    #     start_date = date.today().replace(day=1)
    #     end_date = date.today() + relativedelta(day=31)
    #
    #     workbook = xlwt.Workbook(encoding='utf-8')
    #     worksheet = workbook.add_sheet("exel", cell_overwrite_ok=True)
    #
    #     date_format = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
    #                                     left thin, right thin, top thin, bottom thin;", num_format_str='DD/MM/YYYY', )
    #     header_style = xlwt.easyxf("align:horiz center;align:vertical center;font:color black,bold True;")
    #
    #     title_style = xlwt.easyxf(
    #         'align: horiz center;font: bold 1, color black;pattern: pattern solid, fore_color gray25;'"borders: left thin, right thin, top thin, bottom thin;")
    #
    #     detail_style = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
    #                                     left thin, right thin, top thin, bottom thin;", )
    #
    #     for i in range(7):
    #         worksheet.col(i).width = 5000
    #
    #     worksheet.write(1, 1, 'Start Date', detail_style)
    #     worksheet.write(1, 2, start_date, date_format)
    #     worksheet.write(1, 4, 'End Date', detail_style)
    #     worksheet.write(1, 5, end_date, date_format)
    #     worksheet.write_merge(3, 3, 0, 6, "Upcoming Birthdays ", header_style)
    #
    #     worksheet.write(5, 1, '#', title_style)
    #     worksheet.write(5, 2, 'Employee', title_style)
    #     worksheet.write(5, 3, 'Birth Date', title_style)
    #     worksheet.write(5, 4, 'Department', title_style)
    #     worksheet.write(5, 5, 'Manager', title_style)
    #     today = fields.date.today()
    #     employee_data = self.search([])
    #     birthday_index = 1
    #     birthday_details_row = 6
    #     for employee in employee_data:
    #         if employee.birthday:
    #             if employee.birthday.month == today.month:
    #                 worksheet.write(birthday_details_row, 1, birthday_index, detail_style)
    #                 worksheet.write(birthday_details_row, 2, employee.name, detail_style)
    #                 worksheet.write(birthday_details_row, 3, employee.birthday, date_format)
    #                 worksheet.write(birthday_details_row, 4, employee.department_id.name, detail_style)
    #                 worksheet.write(birthday_details_row, 5, employee.parent_id.name, detail_style)
    #                 birthday_details_row += 1
    #                 birthday_index += 1
    #
    #     stream = BytesIO()
    #     workbook.save(stream)
    #     stream.seek(0)
    #     return stream.read()

    # def action_send_birthday_reminder(self):
    #     birthday_list = self.generate_birthday_list_excel_report()
    #     employee_records = self.search([], limit=1)
    #
    #     for employee in employee_records:
    #         attachment_data = {
    #             'name': 'Birthday Reminders.xlsx',
    #             'datas': base64.b64encode(birthday_list),
    #             'res_model': 'hr.employee',
    #             'type': 'binary',
    #             'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #         }
    #         attachment = self.env['ir.attachment'].create(attachment_data)
    #
            # template_id = self.env.ref(
            #     'reddot_report_automate.mail_template_birthday_reminders')
            # template_id.attachment_ids = attachment
            # if template_id:
            #     template_id.with_context(
            #         email_to=employee.work_email,
            #         attachment_ids=[attachment.id]
            #     ).send_mail(employee.id, force_send=True)

    def action_send_birthday_reminder(self):
        employee_records = self.search([])
        today = fields.date.today()
        email_to_list = []
        email_cc = []
        for employee in employee_records:
            if employee.birthday:
                birth_date = employee.birthday.day
                birth_month = employee.birthday.month
                if today.day == birth_date and today.month == birth_month:
                    email_to_list.append(employee)
                else:
                    if employee.work_email:
                        email_cc.append(employee.work_email)
        for rec in email_to_list:
            template_id = self.env.ref(
                'reddot_report_automate.mail_template_birthday_reminders')
            email_bcc_string = ','.join(email_cc)
            template_id.email_cc = email_bcc_string
            if template_id:
                template_id.with_context(
                    email_to=rec.work_email,
                ).send_mail(rec.id, force_send=True)

    def action_send_anniversary_reminder(self):
        employee_records = self.search([])
        today = fields.date.today()
        email_to_list = []
        email_cc = []
        for employee in employee_records:
            if employee.first_contract_date:
                anniversary_date = employee.first_contract_date.day
                anniversary_month = employee.first_contract_date.month
                if today.day == anniversary_date and today.month == anniversary_month:
                    email_to_list.append(employee)
                else:
                    if employee.work_email:
                        email_cc.append(employee.work_email)
        for rec in email_to_list:
            template_id = self.env.ref(
                'reddot_report_automate.mail_template_anniversary_reminders')
            email_bcc_string = ','.join(email_cc)
            template_id.email_cc = email_bcc_string
            if template_id:
                template_id.with_context(
                    email_to=rec.work_email,
                ).send_mail(rec.id, force_send=True)
