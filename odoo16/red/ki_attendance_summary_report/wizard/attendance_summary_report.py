# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import base64
import io
import pytz
from datetime import date, timedelta
from xlwt import easyxf


class AttendanceSummaryWizard(models.TransientModel):
    _name = "attendance.summary.wizard"

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
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=False,
        string="Company",
        readonly=True
    )
    type = fields.Selection(
        [('summary', 'Summary'), ('summary_hours', 'Summary With Hours')],
        string='Status', default='summary'
    )

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
        filename = filename + '.xls'

        workbook = xlwt.Workbook(encoding="UTF-8")
        formate_3 = xlwt.easyxf('font:height 200; align: horiz center; font: color black; font:bold True;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;', num_format_str='DD/MM/YYYY')
        style4_title_value = xlwt.easyxf('font:height 200; align: horiz center; font: color black; font:bold True;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;')

        date_format = xlwt.easyxf('align: horiz right;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;')
        date_format.num_format_str = 'HH:MM'
        sheet1 = workbook.add_sheet('Attendance Report')

        present_title_value = xlwt.easyxf('pattern: pattern solid, fore_color green;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;')
        absent_title_value = xlwt.easyxf('pattern: pattern solid, fore_color red;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;')
        half_day_title_value = xlwt.easyxf('pattern: pattern solid, fore_color blue;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;')
        work_off_title_value = xlwt.easyxf('pattern: pattern solid, fore_color gray25;borders: top_color black, bottom_color black, right_color black, left_color black,\
                       left thin, right thin, top thin, bottom thin;')

        sheet1.write_merge(0, 1, 0, 10, 'Employee Attendance Summary Report ', easyxf(
            'font:height 300; align: horiz center; font: color black; font:bold True;'))
        sheet1.write(3, 0, 'From:')
        sheet1.write(3, 1, self.Start_date, formate_3)
        sheet1.write(3, 2, 'To:')
        sheet1.write(3, 3, self.end_date, formate_3)
        sheet1.write(3, 6, 'Company Name:')
        sheet1.write(3, 7, self.company_id.name, style4_title_value)

        sheet1.col(0).width = 4000
        row_index = 5
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
            date_wise_dict[each_date.strftime("%Y-%m-%d")] = employee_ids.ids
            date_wise_day_dict[each_date.strftime("%Y-%m-%d")] = each_date.strftime("%A")

        domain = [
            ('check_in', '>=', self.Start_date),
            ('check_in', '<=', self.end_date),
            ('employee_id', 'in', employee_ids.ids)
        ]
        record_ids = self.env['hr.attendance'].sudo().search(domain, order='employee_id, check_in desc')
        current_user = ''
        for records in record_ids:
            tz = records.employee_id.tz
            if records.employee_id.id != current_user:
                current_user = records.employee_id.id
                date_dict[current_user] = {
                    'name': records.employee_id.name,
                    'attendance': {}
                }
                for i in range(delta.days + 1):
                    is_present = 'A'

                    day = self.Start_date + timedelta(days=i)

                    if date_wise_day_dict.get(str(day), '') in ['Saturday', 'Sunday']:
                        is_present = date_wise_day_dict[str(day)]
                    elif self.env['hr.leave'].sudo().search(
                            [('request_unit_half', '=', True), ('employee_id', '=', records.employee_id.id),
                             ('request_date_from', '=', day)]):
                        is_present = 'Half Day'
                    else:
                        global_leave = records.employee_id.resource_calendar_id.global_leave_ids
                        if global_leave:
                            if global_leave.date_from.date() <= day and global_leave.date_to.date() >= day:
                                is_present = global_leave[0].name

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

        if self.type == 'summary':
            column_index = 0
            row_index += 1
            sheet1.write_merge(row_index, row_index + 1, column_index, column_index, 'Employee', style4_title_value)
            row_index_new = row_index
            column_index_new = column_index
            for i in range(delta.days + 1):
                day = self.Start_date + timedelta(days=i)
                column_index += 1
                sheet1.write(row_index, column_index, day.strftime("%d"), formate_3)
                sheet1.write(row_index + 1, column_index, day.strftime("%a"), formate_3)
            sheet1.write_merge(row_index, row_index + 1, column_index + 1, column_index + 1, 'Total Present',
                               style4_title_value)

            for i in date_dict:
                row_index_new += 1
                column_index_new += 1
                count = 0
                for j in date_dict[i]:
                    column_index_new = 0
                    if j == 'name':
                        sheet1.write(row_index_new + 1, column_index_new, date_dict[i][j])
                    if j == 'attendance':
                        for k in date_dict[i][j]:
                            column_index_new += 1
                            for l in date_dict[i][j][k]:
                                if l == 'is_present':
                                    if date_dict[i][j][k][l] == 'P':
                                        sheet1.write(row_index_new + 1, column_index_new, date_dict[i][j][k][l],
                                                     present_title_value)
                                        count += 1
                                    elif date_dict[i][j][k][l] == 'A':
                                        sheet1.write(row_index_new + 1, column_index_new, date_dict[i][j][k][l],
                                                     absent_title_value)
                                    elif date_dict[i][j][k][l] == 'Half Day':
                                        sheet1.write(row_index_new + 1, column_index_new, date_dict[i][j][k][l],
                                                     half_day_title_value)
                                        count += 0.5
                                    else:
                                        sheet1.write(row_index_new + 1, column_index_new, date_dict[i][j][k][l],
                                                     work_off_title_value)
                        sheet1.write(row_index_new + 1, column_index_new + 1, count, style4_title_value)

        else:
            column_index = 0
            row_index += 1
            sheet1.write_merge(row_index, row_index + 1, column_index, column_index, 'Employee', style4_title_value)
            row_index_new = row_index
            column_index_new = column_index
            for i in range(delta.days + 1):
                day = self.Start_date + timedelta(days=i)
                column_index += 1
                sheet1.write(row_index, column_index, day.strftime("%d"), formate_3)
                sheet1.write(row_index + 1, column_index, day.strftime("%a"), formate_3)
            sheet1.write_merge(row_index, row_index + 1, column_index + 1, column_index + 1, 'Total Hour',
                               style4_title_value)
            for i in date_dict:
                row_index_new += 1
                row = row_index_new
                total_work = 0.0
                column_index_new += 1
                for j in date_dict[i]:
                    column_index_new = 0
                    if j == 'name':
                        sheet1.write_merge(row_index_new + 1, row_index_new + 2, column_index_new, column_index_new,
                                           date_dict[i][j])
                        row_index_new += 1
                    if j == 'attendance':
                        for k in date_dict[i][j]:
                            column_index_new += 1
                            for l in date_dict[i][j][k]:
                                if l == 'is_present':
                                    if date_dict[i][j][k][l] == 'P':
                                        sheet1.write(row + 1, column_index_new, date_dict[i][j][k][l],
                                                     present_title_value)
                                    elif date_dict[i][j][k][l] == 'A':
                                        sheet1.write(row + 1, column_index_new, date_dict[i][j][k][l],
                                                     absent_title_value)
                                    elif date_dict[i][j][k][l] == 'Half Day':
                                        sheet1.write(row + 1, column_index_new, date_dict[i][j][k][l],
                                                     half_day_title_value)
                                    else:
                                        sheet1.write(row + 1, column_index_new, date_dict[i][j][k][l],
                                                     work_off_title_value)
                                if l == 'worked_hours':
                                    r = round(float(date_dict[i][j][k][l]))
                                    sheet1.write(row + 2, column_index_new,
                                                 '{0:02.0f}:{1:02.0f}'.format(*divmod(r * 60, 60), 2))
                                    total_work = total_work + (float(date_dict[i][j][k][l]))
                        sheet1.write_merge(row + 1, row + 2, column_index_new + 1, column_index_new + 1,
                                           round(total_work, 2), style4_title_value)
        fp = io.BytesIO()
        workbook.save(fp)

        report_id = self.env['excel.report'].create(
            {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': filename})
        fp.close()
        return {'view_mode': 'form',
                'res_id': report_id.id,
                'res_model': 'excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
                }


class ExcelReport(models.TransientModel):
    _name = 'excel.report'

    file_name = fields.Char(
        'Excel File',
        size=64,
        readonly=True,
    )

    excel_file = fields.Binary(
        'Download Report',
        readonly=True,
    )
