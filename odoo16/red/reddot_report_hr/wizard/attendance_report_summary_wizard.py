# -*- coding: utf-8 -*-
from decorator import append
from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import base64
import io
import pytz
from datetime import date, timedelta
from xlwt import easyxf


class AttendanceReportSummaryWizard(models.TransientModel):
    _name = "attendance.report.summary.wizard"

    Start_date = fields.Date(
        string='Start Date:',
        required=True,
        default=fields.Date.today()
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.today()
    )
    employee_ids = fields.Many2many(
        'hr.employee'
    )
    company_ids = fields.Many2many(
        'res.company',
        string="Company",
    )
    department_ids = fields.Many2many(
        "hr.department",
        string="Departments",
    )
    report_type = fields.Selection(
        [('summary', 'Summary'), ('detail', 'Detail')],
        string='Type', default='summary'
    )

    type_data = {
        'summary': 'Summary',
        'detail': 'Detail'
    }

    def convert_utc_time_to_tz(self, utc_dt, tz_name=None):
        """
        Method to convert UTC time to local time
        :param utc_dt: datetime in UTC
        :param tz_name: the name of the timezone to convert. In case of no tz_name passed, this method will try to find the timezone in context or the login user record

        :return: datetime object presents local time
        """
        tz_name = tz_name or self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise ValidationError(
                _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
        tz = pytz.timezone(tz_name)
        return pytz.utc.localize(utc_dt, is_dst=None).astimezone(tz)

    def print_report(self):
        filename = ''
        if self.Start_date != self.end_date:
            filename = filename + self.Start_date.strftime("%d/%m/%Y") + '-' + self.end_date.strftime("%d/%m/%Y")
        else:
            filename = filename + self.Start_date.strftime("%d/%m/%Y")

        if self.report_type == 'summary':
            filename = filename + '_Summary'
        else:
            filename = filename + '_Detail'
        filename = filename + '.xls'

        workbook = xlwt.Workbook(encoding="UTF-8")
        xlwt.add_palette_colour("green_dark", 0x22)
        workbook.set_colour_RGB(0x22, 171, 241, 199)

        xlwt.add_palette_colour("red_dark", 0x21)
        workbook.set_colour_RGB(0x21, 255, 127, 113)

        xlwt.add_palette_colour("light_blue", 0x23)
        workbook.set_colour_RGB(0x23, 195, 232, 251)

        formate_3 = xlwt.easyxf('font:height 200; align: horiz center; font: color black; font:bold True;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;', num_format_str='DD/MM/YYYY')
        style4_title_value = xlwt.easyxf('font:height 200; align: horiz center; font: color black;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;font:bold True; align: horiz center;')
        title_style1_table_head_left = xlwt.easyxf("""
                                        align: horiz center ;font: color black; font:bold True;font: name Times New Roman,italic off, height 200;
                                        pattern: pattern solid, fore_color gray25;
                                        borders:
                                            top_color black, bottom_color black, right_color black, left_color black,
                                            left thin, right thin, top thin, bottom thin; 
                                    """)
        total_value_count_style = xlwt.easyxf("""
                                             font:bold True;font:name Times New Roman, height 200;align: horiz center;
                                             borders:
                                                 top_color black, bottom_color black, right_color black, left_color black,
                                                 left thin, right thin, top thin, bottom thin; 
                                         """)
        date_format = xlwt.easyxf('align: horiz right;borders: top_color black, bottom_color black, right_color black, left_color black,\
                                            left thin, right thin, top thin, bottom thin;')
        date_format.num_format_str = 'HH:MM'
        sheet1 = workbook.add_sheet('Attendance Report')

        present_title_value = xlwt.easyxf('pattern: pattern solid, fore_color green_dark;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;font:bold True; align: horiz center;')
        absent_title_value = xlwt.easyxf('pattern: pattern solid, fore_color red_dark;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;font:bold True; align: horiz center;')
        half_day_title_value = xlwt.easyxf('pattern: pattern solid, fore_color light_blue;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;font:bold True; align: horiz center;')
        work_off_title_value = xlwt.easyxf('pattern: pattern solid, fore_color gray25;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;font:bold True; align: horiz center;')
        if self.report_type == 'summary':
            heading = 'Employee Attendance Summary Report'
        if self.report_type == 'detail':
            heading = 'Employee Attendance Detail Report'

        sheet1.write_merge(0, 1, 0, 10, heading, easyxf(
            'font:height 300; align: horiz center; font: color black; font:bold True;'))
        sheet1.write(3, 1, 'From:', title_style1_table_head_left)
        sheet1.write(3, 2, self.Start_date, formate_3)
        sheet1.write(3, 4, 'To:', title_style1_table_head_left)
        sheet1.write(3, 5, self.end_date, formate_3)

        filter_company = 'All'
        sheet1.write(3, 7, 'Company Name:', title_style1_table_head_left)

        if self.company_ids:
            filter_company = '\n'.join([i.name for i in self.company_ids])
        sheet1.write(3, 8, filter_company, style4_title_value)

        sheet1.write(5, 1, 'Type:', title_style1_table_head_left)
        sheet1.write(5, 2, self.type_data[self.report_type], style4_title_value)

        filter_department = 'All'
        sheet1.write(5, 4, 'Department:', title_style1_table_head_left)
        if self.department_ids:
            filter_department = '\n'.join([i.name for i in self.department_ids])
        sheet1.write(5, 5, filter_department, style4_title_value)

        filter_employee = 'All'
        sheet1.write(5, 7, 'Employee:', title_style1_table_head_left)
        if self.employee_ids:
            filter_employee = '\n'.join([i.name for i in self.employee_ids])
        sheet1.write(5, 8, filter_employee, style4_title_value)

        sheet1.col(0).width = 4000
        row_index = 7
        date_dict = {}
        delta = self.end_date - self.Start_date

        employee_ids = self.employee_ids
        if not self.employee_ids:
            employee_ids = self.env['hr.employee'].sudo().search([])

        date1 = self.Start_date
        date2 = self.end_date

        date_list = [date1 + timedelta(days=x) for x in range((date2 - date1).days + 1)]

        date_wise_dict = {}
        date_wise_day_dict = {}
        for each_date in date_list:
            date_wise_dict[each_date.strftime("%Y-%m-%d")] = employee_ids
            date_wise_day_dict[each_date.strftime("%Y-%m-%d")] = each_date.strftime("%A")
        domain = [
            ('check_in', '>=', self.Start_date),
            ('check_in', '<=', self.end_date),
        ]
        if self.company_ids:
            domain.append(('employee_id.company_id', 'in', self.company_ids.ids))

        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))

        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        record_ids = self.env['hr.attendance'].sudo().search(domain, order='employee_id, check_in desc')
        current_user = ''
        for records in record_ids:
            tz = records.employee_id.tz
            if records.employee_id.id != current_user:
                current_user = records.employee_id.id
                date_dict[current_user] = {
                    'name': records.employee_id.name,
                    'department': records.department_id.name,
                    'company': records.employee_id.company_id.name,
                    'attendance': {}
                }
                for i in range(delta.days + 1):
                    is_present = 'A'

                    day = self.Start_date + timedelta(days=i)

                    if date_wise_day_dict.get(str(day), '') in ['Sunday']:
                        is_present = date_wise_day_dict[str(day)]
                    elif self.env['hr.leave'].sudo().search(
                            [('request_unit_half', '=', True), ('employee_id', '=', records.employee_id.id),
                             ('request_date_from', '=', day)]):
                        is_present = 'Half Day'
                    else:
                        global_leave = records.employee_id.resource_calendar_id.global_leave_ids

                        if global_leave:
                            for gl in global_leave:
                                if gl.date_from.date() <= day and gl.date_to.date() >= day:
                                    is_present = 'Holiday'

                    date_dict[current_user]['attendance'][day] = {
                        "is_present": is_present,
                        "worked_hours": '00'
                    }
            if date_dict[current_user]['attendance'][records.check_in.date()]['is_present'] == 'Half Day':
                date_dict[current_user]['attendance'][records.check_in.date()]['worked_hours'] = records.worked_hours
            else:
                date_dict[current_user]['attendance'][records.check_in.date()] = {
                    "worked_hours": records.worked_hours,
                    "is_present": 'P'
                }

        if self.report_type == 'detail':
            column_index = 0
            row_index += 1

            sheet1.write_merge(row_index, row_index + 1, column_index, column_index, 'Company',
                               title_style1_table_head_left)
            sheet1.write_merge(row_index, row_index + 1, column_index + 1, column_index + 1, 'Department',
                               title_style1_table_head_left)
            sheet1.write_merge(row_index, row_index + 1, column_index + 2, column_index + 2, 'Employee',
                               title_style1_table_head_left)

            row_index_new = row_index
            column_index_new = column_index
            for i in range(delta.days + 1):
                day = self.Start_date + timedelta(days=i)
                column_index += 1
                sheet1.write(row_index, column_index + 2, day.strftime("%d"), title_style1_table_head_left)
                sheet1.write(row_index + 1, column_index + 2, day.strftime("%a"), title_style1_table_head_left)
            column_index += 2
            sheet1.write_merge(row_index, row_index + 1, column_index + 1, column_index + 1, 'Total Hour',
                               style4_title_value)
            for i in date_dict:
                row_index_new += 2
                row = row_index_new
                total_work = 0.0
                column_index_new += 1
                for j in date_dict[i]:
                    column_index_new = 0
                    if j == 'company':
                        sheet1.write_merge(row_index_new, row_index_new, column_index_new, column_index_new,
                                           date_dict[i][j], style4_title_value)
                    column_index_new += 1
                    if j == 'department':
                        sheet1.write_merge(row_index_new, row_index_new, column_index_new, column_index_new,
                                           date_dict[i][j], style4_title_value)
                    column_index_new += 1
                    if j == 'name':
                        sheet1.write_merge(row_index_new, row_index_new, column_index_new, column_index_new,
                                           date_dict[i][j], style4_title_value)
                    if j == 'attendance':
                        for k in date_dict[i][j]:
                            column_index_new += 1
                            for l in date_dict[i][j][k]:
                                if l == 'is_present':
                                    if date_dict[i][j][k][l] == 'P':
                                        sheet1.write(row_index_new, column_index_new, date_dict[i][j][k][l],
                                                     present_title_value)
                                    elif date_dict[i][j][k][l] == 'A':
                                        sheet1.write(row_index_new, column_index_new, date_dict[i][j][k][l],
                                                     absent_title_value)
                                    elif date_dict[i][j][k][l] == 'Half Day':
                                        sheet1.write(row_index_new, column_index_new, date_dict[i][j][k][l],
                                                     half_day_title_value)
                                    else:
                                        sheet1.write(row_index_new, column_index_new, date_dict[i][j][k][l],
                                                     work_off_title_value)
                                if l == 'worked_hours':
                                    r = round(float(date_dict[i][j][k][l]))
                                    sheet1.write(row + 1, column_index_new,
                                                 '{0:02.0f}:{1:02.0f}'.format(*divmod(r * 60, 60), 2),
                                                 total_value_count_style)
                                    total_work = total_work + (float(date_dict[i][j][k][l]))
                        sheet1.write_merge(row_index_new, row + 1, column_index_new + 1, column_index_new + 1,
                                           round(total_work, 2), total_value_count_style)

        if self.report_type == 'summary':
            col = 0
            row = row_index + 1

            sheet1.write_merge(row, row + 1, col, col, 'Employee', title_style1_table_head_left)

            sheet1.write(row + 1, col + 1, 'Total Days', title_style1_table_head_left)
            sheet1.write(row + 1, col + 2, 'Present Days', title_style1_table_head_left)
            sheet1.write(row + 1, col + 3, 'Public Holiday', title_style1_table_head_left)
            sheet1.write(row + 1, col + 4, 'Leave Taken', title_style1_table_head_left)
            sheet1.write(row + 1, col + 5, 'Absent', title_style1_table_head_left)

            date_dict_details = {}
            attendance_ids = self.env['hr.attendance'].sudo().search(domain, order='employee_id, check_in desc')
            current_user = ''
            for records in attendance_ids:
                current_user = records.employee_id.id
                date_dict_details[current_user] = {
                    'name': records.employee_id.name,
                    'total': delta.days + 1,
                    'attendance': {}
                }

                for i in range(delta.days + 1):
                    is_present = 'A'

                    day = self.Start_date + timedelta(days=i)

                    if date_wise_day_dict.get(str(day), '') in ['Sunday']:
                        is_present = date_wise_day_dict[str(day)]
                    elif self.env['hr.leave'].sudo().search(
                            [('request_unit_half', '=', True), ('employee_id', '=', records.employee_id.id),
                             ('request_date_from', '=', day)]):
                        is_present = 'Half Day'
                    else:
                        global_leave = records.employee_id.resource_calendar_id.global_leave_ids
                        if global_leave:
                            for gl in global_leave:
                                if gl.date_from.date() <= day and gl.date_to.date() >= day:
                                    is_present = gl[0].name

                    date_dict_details[current_user]['attendance'][day] = {
                        "is_present": is_present,
                        "worked_hours": '00'
                    }
                if date_dict_details[current_user]['attendance'][records.check_in.date()]['is_present'] == 'Half Day':
                    date_dict_details[current_user]['attendance'][records.check_in.date()][
                        'worked_hours'] = records.worked_hours
                else:
                    date_dict_details[current_user]['attendance'][records.check_in.date()] = {
                        "worked_hours": records.worked_hours,
                        "is_present": 'P'
                    }

            data_list = []
            for re in date_dict_details:
                final_dct = {}
                present_total = 0
                abset_total = 0
                leave_taken_total = 0
                public_holiday_total = 0
                final_dct['name'] = date_dict_details[re]['name']
                final_dct['total'] = date_dict_details[re]['total']
                for att in date_dict_details[re]['attendance']:
                    if date_dict_details[re]['attendance'][att]['is_present'] == "A":
                        abset_total += 1
                    elif date_dict_details[re]['attendance'][att]['is_present'] == "P":
                        present_total += 1

                    elif date_dict_details[re]['attendance'][att]['is_present'] == "Half Day":
                        leave_taken_total += 1
                    else:
                        public_holiday_total += 1
                    final_dct['absent'] = abset_total
                    final_dct['present'] = present_total
                    final_dct['leave'] = leave_taken_total
                    final_dct['holiday'] = public_holiday_total
                data_list.append(final_dct)
            for rec in data_list:
                row += 1
                sheet1.write(row + 1, col, rec['name'], total_value_count_style)
                sheet1.write(row + 1, col + 1, rec['total'], total_value_count_style)
                sheet1.write(row + 1, col + 2, rec['present'], total_value_count_style)
                sheet1.write(row + 1, col + 3, rec['holiday'], total_value_count_style)
                sheet1.write(row + 1, col + 4, rec['leave'], total_value_count_style)
                sheet1.write(row + 1, col + 5, rec['absent'], total_value_count_style)

        # fp = io.BytesIO()
        # workbook.save(fp)

        stream = io.BytesIO()
        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()
