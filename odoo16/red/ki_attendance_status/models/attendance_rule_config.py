from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time,timedelta, date
from dateutil.relativedelta import relativedelta

import pytz




class AttendanceRuleConfig(models.Model):
    _name = "attendance.rule.config"

    name = fields.Char(string="Name", required=True)
    start_time = fields.Float(string="Start Time", required=True)
    end_time = fields.Float(string="End Time", required=True)
    status_color = fields.Integer(string="Color")
    description = fields.Text(string="Description")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)

    @api.constrains('end_time')
    def end_time_constrains(self):
        if self.start_time > self.end_time:
            raise UserError(_("End time must be greater then Start time."))


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    status_id = fields.Many2one(
        'attendance.rule.config',
        string="Status",

    )

    def convert_time_to_utc(self, dt, tz_name=None):
        tz_name = tz_name or self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise ValidationError(
                _("Local time zone is not defined. You may need to set a time zone in your user's Preferences.")
            )
        local = pytz.timezone(tz_name)
        local_dt = local.localize(dt, is_dst=None)
        uts_cnt =  local_dt.astimezone(pytz.utc)
#         uts_cnt = uts_cnt.strftime("%Y-%m-%d %H:%M:%S")
        return uts_cnt


    def _cron_auto_generate_leave_from_attendance(self):
        today = fields.Date.today()

        #         today = datetime.strptime("2022-06-01", "%Y-%m-%d").date()#fields.Date.today()
        first_day = today.replace(day=1)
        end_date = date(
            first_day.year,
            first_day.month,
            1
        ) + relativedelta(months=1, days=-1)
        date1 = first_day
        date2 = end_date
        months = [date1 + timedelta(days=x) for x in range((date2 - date1).days + 1)]
        company_ids = self.env['res.company'].sudo().search([])
        for company in company_ids:
            leave_type = self.env['hr.leave.type'].sudo().search(
                [('company_id', '=', company.id),
                 ('name', '=', 'Unpaid')
                 ])
            if not leave_type:
                leave_type = self.env['hr.leave.type'].sudo().search(
                    [('company_id', '=', False),
                     ('name', '=', 'Unpaid')
                     ])

            employees = self.env['hr.employee'].sudo().search([('company_id', '=', company.id)])
            if not leave_type:
                continue
            for employee in employees:
                self._cr.execute("""
                             SELECT
                                 check_in::date
                             FROM
                                 hr_attendance
                             WHERE
                                 employee_id=%s
                             ORDER BY
                                 check_in
                         """ % employee.id)
                date_list_res = self._cr.dictfetchall()
                date_list = [x['check_in'] for x in date_list_res]
                missing_dates = [x for x in months if x not in date_list]
                leave_date_list = []
                for missiong_date in missing_dates:
                    start_dt = missiong_date + relativedelta(hours=00, minutes=00, seconds=10)
                    end_dt = missiong_date + relativedelta(hours=23, minutes=59, seconds=59)
                    start_dt = self.convert_time_to_utc(start_dt)
                    end_dt = self.convert_time_to_utc(end_dt)

                    leave_status = employee.resource_calendar_id._work_intervals_batch(start_dt=start_dt, end_dt=end_dt,
                                                                                 resources=employee.resource_id
                                                                                       )
                    if leave_status:
                        today_start = fields.Datetime.to_string(start_dt)
                        today_end = fields.Datetime.to_string(start_dt + relativedelta(hours=23, minutes=59, seconds=59))
                        #                         today_end = fields.Datetime.to_string(today_date + relativedelta(hours=23, minutes=59, seconds=59))
                        holidays = self.env['hr.leave'].sudo().search([
                            ('employee_id', '=', employee.id),
                            ('state', 'not in', ['cancel', 'refuse']),
                            ('date_from', '<=', today_end),
                            ('date_to', '>=', today_start),
                        ])
                        if not holidays:
                            leave_date_list.append(missiong_date)
                for leave_date in leave_date_list:
                    leave = self.env['hr.leave'].create({
                        'name': 'Attendance missing - ' + str(leave_date),
                        'employee_id': employee.id,
                        'holiday_status_id': leave_type.id,
                        'request_date_from': leave_date,
                        'date_from': leave_date,
                        'request_date_to': leave_date,
                        'date_to': leave_date,
                        'number_of_days': 1,
                    })


class HrEmployeeEmail(models.Model):
    _inherit = "hr.employee"

    current_year = date.today().year
    current_month = date.today().strftime('%B')

    start_date = datetime.today() + relativedelta(day=1)
    End_date = datetime.today() + relativedelta(day=31)

    def convert_time_to_utc(self, dt, tz_name=None):
        tz_name = tz_name or self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise ValidationError(
                _("Local time zone is not defined. You may need to set a time zone in your user's Preferences.")
            )
        local = pytz.timezone(tz_name)
        local_dt = local.localize(dt, is_dst=None)
        uts_cnt =  local_dt.astimezone(pytz.utc)
#         uts_cnt = uts_cnt.strftime("%Y-%m-%d %H:%M:%S")
        return uts_cnt


    def _send_mail(self):
        employee_id = self.env['hr.employee'].search([])
        today = fields.Date.today()

        #         today = datetime.strptime("2022-06-01", "%Y-%m-%d").date()#fields.Date.today()
        first_day = today.replace(day=1)
        end_date = date(
            first_day.year,
            first_day.month,
            1
        ) + relativedelta(months=1, days=-1)
        date1 = first_day
        date2 = end_date
        months = [date1 + timedelta(days=x) for x in range((date2 - date1).days + 1)]

        for rec in employee_id:
            employee = rec
            self._cr.execute("""
                         SELECT
                             check_in::date
                         FROM
                             hr_attendance
                         WHERE
                             employee_id=%s
                         ORDER BY
                             check_in
                     """ % employee.id)
            date_list_res = self._cr.dictfetchall()
            date_list = [x['check_in'] for x in date_list_res]
            missing_dates = [x for x in months if x not in date_list]
            leave_date_list = []
            for missiong_date in missing_dates:
                start_dt = missiong_date + relativedelta(hours=00, minutes=00, seconds=10)
                end_dt = missiong_date + relativedelta(hours=23, minutes=59, seconds=59)
                start_dt = self.convert_time_to_utc(start_dt)
                end_dt = self.convert_time_to_utc(end_dt)

                leave_status = employee.resource_calendar_id._work_intervals_batch(start_dt=start_dt, end_dt=end_dt,
                                                                             resources=employee.resource_id
                                                                                   )
                if leave_status:
                    today_start = fields.Datetime.to_string(start_dt)
                    today_end = fields.Datetime.to_string(start_dt + relativedelta(hours=23, minutes=59, seconds=59))
                    #                         today_end = fields.Datetime.to_string(today_date + relativedelta(hours=23, minutes=59, seconds=59))
                    holidays = self.env['hr.leave'].sudo().search([
                        ('employee_id', '=', employee.id),
                        ('state', 'not in', ['cancel', 'refuse']),
                        ('date_from', '<=', today_end),
                        ('date_to', '>=', today_start),
                    ])
                    if holidays:
                        att_holidays = holidays.filtered(lambda i: 'missing' not in (i.name and i.name or ''))
                        if not att_holidays:
                            leave_date_list.append(missiong_date)
                    else:
                        leave_date_list.append(missiong_date)

            attendance_id = self.env['hr.attendance'].search(
                [('employee_id', '=', rec.id), ('check_in', ">=", self.start_date), ('check_in', "<=", self.End_date),
                 ('check_out', ">=", self.start_date), ('check_out', "<=", self.End_date)])
            dict = {}
            for recs in attendance_id:
                if recs.status_id.name not in dict:
                    dict[recs.status_id.name] = 0
                dict[recs.status_id.name] += 1
            dict.update({'Absent': len(leave_date_list)})
            vals = {
                'dict': dict
            }
            mail_template = self.env.ref('ki_attendance_status.employee_email_template')
            mail_template.with_context(vals).send_mail(rec.id)
