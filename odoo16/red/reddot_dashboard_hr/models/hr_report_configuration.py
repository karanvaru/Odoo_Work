from odoo import models, api, fields, _
from datetime import timedelta, datetime, time, date
from .report_configuration_recurrence import DAYS, WEEKS
from odoo.tools.misc import get_lang
from odoo.osv import expression
from io import BytesIO
from odoo.tools import ustr
import base64
from odoo.exceptions import UserError, ValidationError
import xlwt
from dateutil.relativedelta import relativedelta


class HrReportConfiguration(models.Model):
    _name = "hr.report.configuration"

    reporting_to_ids = fields.Many2many(
        'res.partner',
        string='Reporting To',
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Send To',
    )

    server_action_id = fields.Many2one(
        "ir.actions.server",
        string="Server Action",
    )

    report_type = fields.Selection([
        ('hr', 'Hr'),
        ('payroll', 'Payroll'),

    ], string='Report Type', )

    report_code = fields.Char(
        string='Report Code',
    )

    recurring_task = fields.Boolean(
        string="Recurring Task",
        default=True
    )
    recurring_count = fields.Integer(string="Tasks in Recurrence", compute='_compute_recurring_count')

    repeat_interval = fields.Integer(string='Repeat Every', default=1, compute='_compute_repeat', readonly=False,
                                     groups="project.group_project_user")

    repeat_unit = fields.Selection([
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], default='week', compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_type = fields.Selection([
        ('forever', 'Forever'),
        ('until', 'End Date'),
        ('after', 'Number of Repetitions'),
    ], default="forever", string="Until", compute='_compute_repeat', readonly=False,
        groups="project.group_project_user")

    repeat_on_month = fields.Selection([
        ('date', 'Date of the Month'),
        ('day', 'Day of the Month'),
    ], default='date', compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_on_year = fields.Selection([
        ('date', 'Date of the Year'),
        ('day', 'Day of the Year'),
    ], default='date', compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    mon = fields.Boolean(string="Mon", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    tue = fields.Boolean(string="Tue", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    wed = fields.Boolean(string="Wed", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    thu = fields.Boolean(string="Thu", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    fri = fields.Boolean(string="Fri", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    sat = fields.Boolean(string="Sat", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    sun = fields.Boolean(string="Sun", compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_day = fields.Selection([
        (str(i), str(i)) for i in range(1, 32)
    ], compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_week = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
        ('last', 'Last'),
    ], default='first', compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_weekday = fields.Selection([
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ], string='Day Of The Week', compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    repeat_month = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December'),
    ], compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    recurrence_id_default = fields.Many2one('project.task.recurrence', copy=False)
    recurrence_id = fields.Many2one('report.configuration.recurrence', copy=False)
    repeat_until = fields.Date(string="End Date", compute='_compute_repeat', readonly=False,
                               groups="project.group_project_user")
    repeat_number = fields.Integer(string="Repetitions", default=1, compute='_compute_repeat', readonly=False,
                                   groups="project.group_project_user")

    repeat_show_dow = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")
    repeat_show_day = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")
    repeat_show_week = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")
    repeat_show_month = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")
    recurrence_message = fields.Char(string='Next Recurrencies', compute='_compute_recurrence_message',
                                     groups="project.group_project_user")

    @api.model
    def default_get(self, default_fields):
        vals = super(HrReportConfiguration, self).default_get(default_fields)
        current_model_name = self._name
        server_action = self.env['ir.actions.server'].search([('model_id.model', '=', current_model_name)], limit=1)
        if server_action:
            vals['server_action_id'] = server_action.id
        days = list(DAYS.keys())
        week_start = fields.Datetime.today().weekday()
        value = self._fields.get('repeat_weekday').selection[week_start][0]
        if all(d in default_fields for d in days):
            vals[days[week_start]] = True
        if 'repeat_day' in default_fields:
            vals['repeat_day'] = str(fields.Datetime.today().day)
        if 'repeat_month' in default_fields:
            vals['repeat_month'] = self._fields.get('repeat_month').selection[fields.Datetime.today().month - 1][0]
        if 'repeat_until' in default_fields:
            vals['repeat_until'] = fields.Date.today() + timedelta(days=7)
        if 'repeat_weekday' in default_fields:
            vals['repeat_weekday'] = self._fields.get('repeat_weekday').selection[week_start][0]

        return vals

    def write(self, vals):
        if 'allow_recurring_tasks' in vals and not vals.get('allow_recurring_tasks'):
            self.env['project.task'].search([('project_id', 'in', self.ids), ('recurring_task', '=', True)]).write(
                {'recurring_task': False})
        if 'active' in vals and not vals.get('active') and any(self.mapped('recurrence_id')):
            vals['recurring_task'] = False
        if 'recurrence_id' in vals and vals.get('recurrence_id') and any(not task.active for task in self):
            raise UserError(_('Archived tasks cannot be recurring. Please unarchive the task first.'))
        rec_fields = vals.keys() & self._get_recurrence_fields()
        if rec_fields:
            rec_values = {rec_field: vals[rec_field] for rec_field in rec_fields}
            for task in self:
                if task.recurrence_id:
                    task.recurrence_id.write(rec_values)
                elif vals.get('recurring_task'):
                    rec_values['next_recurrence_date'] = fields.Datetime.today()
                    recurrence = self.env['report.configuration.recurrence'].create(rec_values)
                    task.recurrence_id = recurrence.id

        if not vals.get('recurring_task', True) and self.recurrence_id:
            tasks_in_recurrence = self.recurrence_id.report_configuration_ids
            self.recurrence_id.unlink()
            tasks_in_recurrence.write({'recurring_task': False})

        tasks = self
        recurrence_update = vals.pop('recurrence_update', 'this')
        if recurrence_update != 'this':
            recurrence_domain = []
            if recurrence_update == 'subsequent':
                for task in self:
                    recurrence_domain = expression.OR([recurrence_domain,
                                                       ['&', ('recurrence_id', '=', task.recurrence_id.id),
                                                        ('create_date', '>=', task.create_date)]])
            else:
                recurrence_domain = [('recurrence_id', 'in', self.recurrence_id.ids)]
            tasks |= self.env['hr.report.configuration'].search(recurrence_domain)

        result = super(HrReportConfiguration, tasks).write(vals)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            rec_fields = vals.keys() & self._get_recurrence_fields()
            if rec_fields and vals.get('recurring_task') is True:
                rec_values = {rec_field: vals[rec_field] for rec_field in rec_fields}
                rec_values['next_recurrence_date'] = fields.Datetime.today()
                recurrence = self.env['report.configuration.recurrence'].create(rec_values)
                vals['recurrence_id'] = recurrence.id
        config = super(HrReportConfiguration, self).create(vals_list)
        return config

    @api.depends('recurring_task', 'repeat_unit', 'repeat_on_month', 'repeat_on_year')
    def _compute_repeat_visibility(self):
        for task in self:
            task.repeat_show_day = task.recurring_task and (
                    task.repeat_unit == 'month' and task.repeat_on_month == 'date') or (
                                           task.repeat_unit == 'year' and task.repeat_on_year == 'date')
            task.repeat_show_week = task.recurring_task and (
                    task.repeat_unit == 'month' and task.repeat_on_month == 'day') or (
                                            task.repeat_unit == 'year' and task.repeat_on_year == 'day')
            task.repeat_show_dow = task.recurring_task and task.repeat_unit == 'week'
            task.repeat_show_month = task.recurring_task and task.repeat_unit == 'year'

    @api.model
    def _get_recurrence_fields(self):
        return ['repeat_interval', 'repeat_unit', 'repeat_type', 'repeat_until', 'repeat_number',
                'repeat_on_month', 'repeat_on_year', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat',
                'sun', 'repeat_day', 'repeat_week', 'repeat_month', 'repeat_weekday']

    @api.depends('recurring_task')
    def _compute_repeat(self):
        rec_fields = self._get_recurrence_fields()
        defaults = self.default_get(rec_fields)
        for task in self:
            for f in rec_fields:
                if task.recurrence_id:
                    task[f] = task.recurrence_id[f]
                else:
                    if task.recurring_task:
                        task[f] = defaults.get(f)
                    else:
                        task[f] = False

    def _get_weekdays(self, n=1):
        self.ensure_one()
        if self.repeat_unit == 'week':
            return [fn(n) for day, fn in DAYS.items() if self[day]]
        return [DAYS.get(self.repeat_weekday)(n)]

    def _get_recurrence_start_date(self):
        return fields.Date.today()

    @api.depends(
        'recurring_task', 'repeat_interval', 'repeat_unit', 'repeat_type', 'repeat_until',
        'repeat_number', 'repeat_on_month', 'repeat_on_year', 'mon', 'tue', 'wed', 'thu', 'fri',
        'sat', 'sun', 'repeat_day', 'repeat_week', 'repeat_month', 'repeat_weekday')
    def _compute_recurrence_message(self):
        self.recurrence_message = False
        for task in self.filtered(lambda t: t.recurring_task and t._is_recurrence_valid()):
            date = task._get_recurrence_start_date()
            recurrence_left = task.recurrence_id.recurrence_left if task.recurrence_id else task.repeat_number
            number_occurrences = min(5, recurrence_left if task.repeat_type == 'after' else 5)
            delta = task.repeat_interval if task.repeat_unit == 'day' else 1
            recurring_dates = self.env['report.configuration.recurrence']._get_next_recurring_dates(
                date + timedelta(days=delta),
                task.repeat_interval,
                task.repeat_unit,
                task.repeat_type,
                task.repeat_until,
                task.repeat_on_month,
                task.repeat_on_year,
                task._get_weekdays(WEEKS.get(task.repeat_week)),
                task.repeat_day,
                task.repeat_week,
                task.repeat_month,
                count=number_occurrences)
            date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format or get_lang(
                self.env).date_format
            if recurrence_left == 0:
                recurrence_title = _('There are no more occurrences.')
            else:
                recurrence_title = _('A new task will be created on the following dates:')
            task.recurrence_message = '<p><span class="fa fa-check-circle"></span> %s</p><ul>' % recurrence_title
            task.recurrence_message += ''.join(
                ['<li>%s</li>' % date.strftime(date_format) for date in recurring_dates[:5]])
            if task.repeat_type == 'after' and recurrence_left > 5 or task.repeat_type == 'forever' or len(
                    recurring_dates) > 5:
                task.recurrence_message += '<li>...</li>'
            task.recurrence_message += '</ul>'
            if task.repeat_type == 'until':
                task.recurrence_message += _('<p><em>Number of tasks: %(tasks_count)s</em></p>') % {
                    'tasks_count': len(recurring_dates)}

    def _is_recurrence_valid(self):
        self.ensure_one()
        return self.repeat_interval > 0 and \
            (not self.repeat_show_dow or self._get_weekdays()) and \
            (self.repeat_type != 'after' or self.repeat_number) and \
            (self.repeat_type != 'until' or self.repeat_until and self.repeat_until > fields.Date.today())

    def generate_excel_report(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)

        date_format = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                                     left thin, right thin, top thin, bottom thin;", num_format_str='DD/MM/YYYY', )
        header_style = xlwt.easyxf("align:horiz center;align:vertical center;font:color black,bold True;")

        title_style = xlwt.easyxf(
            'align: horiz center;font: bold 1, color black;pattern: pattern solid, fore_color gray25;'"borders: left thin, right thin, top thin, bottom thin;")

        detail_style = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                                     left thin, right thin, top thin, bottom thin;", )

        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet("exel", cell_overwrite_ok=True)

        for i in range(7):
            worksheet.col(i).width = 5000
        row_index = 6
        index = 1
        worksheet.write(1, 1, 'Start Date', detail_style)
        worksheet.write(1, 2, start_date, date_format)
        worksheet.write(1, 4, 'End Date', detail_style)
        worksheet.write(1, 5, end_date, date_format)
        worksheet.write_merge(3, 3, 0, 6, "Active Contract ", header_style)
        worksheet.write(5, 0, '#', title_style)
        worksheet.write(5, 1, 'Contract', title_style)
        worksheet.write(5, 2, 'Employee', title_style)
        worksheet.write(5, 3, 'Start Date', title_style)
        worksheet.write(5, 4, 'End Date', title_style)
        worksheet.write(5, 5, 'Status', title_style)
        worksheet.write(5, 6, 'Responsible', title_style)
        active_contract = self.env['hr.contract'].search(
            [('state', '=', 'open')])
        for contract in active_contract:
            worksheet.write(row_index, 0, index, detail_style)
            worksheet.write(row_index, 1, contract.name, detail_style)
            worksheet.write(row_index, 2, contract.employee_id.name, detail_style)
            worksheet.write(row_index, 3, contract.date_start if contract.date_start else '', date_format)
            worksheet.write(row_index, 4, contract.date_end if contract.date_end else '', date_format)
            worksheet.write(row_index, 5, contract.state, detail_style)
            worksheet.write(row_index, 6, contract.hr_responsible_id.name, detail_style)
            row_index += 1
            index += 1

        contract_data = self.env['hr.contract'].search(
            [('state', '=', 'open'), ('date_end', '>=', start_date), ('date_end', '<=', end_date)])
        next_tabel_index = row_index + 2
        worksheet.write_merge(next_tabel_index, next_tabel_index, 0, 6, "Contract To Expire ", header_style)
        header_index = next_tabel_index + 2
        worksheet.write(header_index, 0, '#', title_style)
        worksheet.write(header_index, 1, 'Contract', title_style)
        worksheet.write(header_index, 2, 'Employee', title_style)
        worksheet.write(header_index, 3, 'Start Date', title_style)
        worksheet.write(header_index, 4, 'End Date', title_style)
        worksheet.write(header_index, 5, 'Status', title_style)
        worksheet.write(header_index, 6, 'Responsible', title_style)
        to_row_index = header_index + 1
        to_index = 1

        for contract_d in contract_data:
            worksheet.write(to_row_index, 0, to_index, detail_style)
            worksheet.write(to_row_index, 1, contract_d.name, detail_style)
            worksheet.write(to_row_index, 2, contract_d.employee_id.name, detail_style)
            worksheet.write(to_row_index, 3, contract_d.date_start if contract_d.date_start else '', date_format)
            worksheet.write(to_row_index, 4, contract_d.date_end if contract_d.date_end else '', date_format)
            worksheet.write(to_row_index, 5, contract_d.state, detail_style)
            worksheet.write(to_row_index, 6, contract_d.hr_responsible_id.name, detail_style)
            to_row_index += 1
            to_index += 1

        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream.read()

    def action_send_report(self):
        # report_config = self.env['hr.report.configuration'].search([])
        # for report in report_config:
        excel_data = self.generate_excel_report()
        for emails in self.employee_ids:
            email_values = {
                'subject': 'Contract Expiration Report',
                'body_html': '<p>Hello,%s</p><p>Please find the attached report.</p>' % (emails.name),
                'email_to': emails.work_email,
                'attachment_ids': [(0, 0, {
                    'name': 'contract_summary.xlsx',
                    'datas': ustr(base64.b64encode(excel_data)),
                    'res_model': 'hr.report.configuration',
                    'type': 'binary',
                    'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                })],
            }
            mail_id = self.env['mail.mail'].create(email_values)
            mail_id.send()

    def action_server(self):
        report_config = self.search([])
        for report in report_config:
            if report.server_action_id:
                context = report.env.context.copy()
                context.update({
                    'active_model': report._name,
                    'active_ids': report.ids,
                    'active_id': report.id,
                })
                # self.env['ir.actions.server'].browse(report.server_action_id.id).with_context(context).run()
                report.server_action_id.with_context(context).sudo().run()
            else:
                raise UserError(_('Please select a server action.'))

    def action_recurring_tasks(self):
        return {
            'name': _('Report in Recurrence'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.report.configuration',
            'view_mode': 'tree,form,kanban',
            'context': {'create': False},
            'domain': [('recurrence_id', 'in', self.recurrence_id.ids)],
        }

    @api.depends('recurrence_id')
    def _compute_recurring_count(self):
        self.recurring_count = 0
        count = self.env['hr.report.configuration'].search_count([('recurrence_id', 'in', self.recurrence_id.ids)])
        self.recurring_count = count

    def generate_birthday_list_excel_report(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)

        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet("exel", cell_overwrite_ok=True)

        date_format = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                                     left thin, right thin, top thin, bottom thin;", num_format_str='DD/MM/YYYY', )
        header_style = xlwt.easyxf("align:horiz center;align:vertical center;font:color black,bold True;")

        title_style = xlwt.easyxf(
            'align: horiz center;font: bold 1, color black;pattern: pattern solid, fore_color gray25;'"borders: left thin, right thin, top thin, bottom thin;")

        detail_style = xlwt.easyxf("align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                                     left thin, right thin, top thin, bottom thin;", )

        for i in range(7):
            worksheet.col(i).width = 5000

        worksheet.write(1, 1, 'Start Date', detail_style)
        worksheet.write(1, 2, start_date, date_format)
        worksheet.write(1, 4, 'End Date', detail_style)
        worksheet.write(1, 5, end_date, date_format)
        worksheet.write_merge(3, 3, 0, 6, "Upcoming Birthdays ", header_style)

        worksheet.write(5, 1, '#', title_style)
        worksheet.write(5, 2, 'Employee', title_style)
        worksheet.write(5, 3, 'Birth Date', title_style)
        worksheet.write(5, 4, 'Department', title_style)
        worksheet.write(5, 5, 'Manager', title_style)

        today = fields.date.today()
        employee_data = self.env['hr.employee'].search([])
        list_5_year = []
        list_10_year = []
        list_15_year = []
        list_20_year = []
        list_25_year = []
        birthday_index = 1
        birthday_details_row = 6
        for employee in employee_data:
            if employee.first_contract_date:
                join_year = today.year - employee.first_contract_date.year
                if join_year == 5:
                    list_5_year.append(employee)
                if join_year == 10:
                    list_10_year.append(employee)
                if join_year == 15:
                    list_15_year.append(employee)
                if join_year == 20:
                    list_20_year.append(employee)
                if join_year == 25:
                    list_25_year.append(employee)

            if employee.birthday:
                if employee.birthday.month == today.month:
                    worksheet.write(birthday_details_row, 1, birthday_index, detail_style)
                    worksheet.write(birthday_details_row, 2, employee.name, detail_style)
                    worksheet.write(birthday_details_row, 3, employee.birthday, date_format)
                    worksheet.write(birthday_details_row, 4, employee.department_id.name, detail_style)
                    worksheet.write(birthday_details_row, 5, employee.parent_id.name, detail_style)
                    birthday_details_row += 1
                    birthday_index += 1
        index_5_year_row = birthday_details_row
        list_5_year_index = 1
        index_10_year_row = index_5_year_row
        if list_5_year:
            worksheet.write_merge(index_5_year_row + 1, index_5_year_row + 1, 0, 6, "5 Year Anniversary", header_style)

            worksheet.write(index_5_year_row + 3, 1, '#', title_style)
            worksheet.write(index_5_year_row + 3, 2, 'Employee', title_style)
            worksheet.write(index_5_year_row + 3, 3, 'Joining Date', title_style)
            worksheet.write(index_5_year_row + 3, 4, 'Department', title_style)
            worksheet.write(index_5_year_row + 3, 5, 'Manager', title_style)
            row_5 = index_5_year_row + 4

            for rec in list_5_year:
                worksheet.write(row_5, 1, list_5_year_index, detail_style)
                worksheet.write(row_5, 2, rec.name, detail_style)
                worksheet.write(row_5, 3, rec.first_contract_date, date_format)
                worksheet.write(row_5, 4, rec.department_id.name, detail_style)
                worksheet.write(row_5, 5, rec.parent_id.name, detail_style)
                row_5 += 1
                list_5_year_index += 1
            index_10_year_row = row_5

        index_15_year_row = index_10_year_row
        if list_10_year:
            worksheet.write_merge(index_10_year_row + 1, index_10_year_row + 1, 0, 6, "10 Year Anniversary", header_style)
            list_10_year_index = 1
            worksheet.write(index_10_year_row + 3, 1, '#', title_style)
            worksheet.write(index_10_year_row + 3, 2, 'Employee', title_style)
            worksheet.write(index_10_year_row + 3, 3, 'Joining Date', title_style)
            worksheet.write(index_10_year_row + 3, 4, 'Department', title_style)
            worksheet.write(index_10_year_row + 3, 5, 'Manager', title_style)
            row_10 = index_10_year_row + 4
            for rec in list_10_year:
                worksheet.write(row_10, 1, list_10_year_index, detail_style)
                worksheet.write(row_10, 2, rec.name, detail_style)
                worksheet.write(row_10, 3, rec.first_contract_date, date_format)
                worksheet.write(row_10, 4, rec.department_id.name, detail_style)
                worksheet.write(row_10, 5, rec.parent_id.name, detail_style)
                list_10_year_index += 1
                row_10 += 1
            index_15_year_row = row_10
        index_20_year_row = index_15_year_row
        if list_15_year:
            list_15_year_index = 1
            worksheet.write_merge(index_15_year_row + 1, index_15_year_row + 2, 0, 6, "15 Year Anniversary", header_style)
            worksheet.write(index_15_year_row + 3, 1, '#', title_style)
            worksheet.write(index_15_year_row + 3, 2, 'Employee', title_style)
            worksheet.write(index_15_year_row + 3, 3, 'Joining Date', title_style)
            worksheet.write(index_15_year_row + 3, 4, 'Department', title_style)
            worksheet.write(index_15_year_row + 3, 5, 'Manager', title_style)
            row_15 = index_15_year_row + 4
            for rec in list_15_year:
                worksheet.write(row_15, 1, list_15_year_index, detail_style)
                worksheet.write(row_15, 2, rec.name, detail_style)
                worksheet.write(row_15, 3, rec.first_contract_date, date_format)
                worksheet.write(row_15, 4, rec.department_id.name, detail_style)
                worksheet.write(row_15, 5, rec.parent_id.name, detail_style)

                row_15 += 1
            list_15_year_index += 1
            index_20_year_row = row_15
        index_25_year_row = index_20_year_row
        if list_20_year:
            list_20_year_index = 1
            worksheet.write_merge(index_20_year_row + 1, index_20_year_row + 2, 0, 6, "25 Year Anniversary", header_style)

            worksheet.write(index_20_year_row + 3, 1, '#', title_style)
            worksheet.write(index_20_year_row + 3, 2, 'Employee', title_style)
            worksheet.write(index_20_year_row + 3, 3, 'Joining Date', title_style)
            worksheet.write(index_20_year_row + 3, 4, 'Department', title_style)
            worksheet.write(index_20_year_row + 3, 5, 'Manager', title_style)
            row_20 = index_20_year_row + 4
            for rec in list_20_year:
                worksheet.write(row_20, 1, list_20_year_index, detail_style)
                worksheet.write(row_20, 2, rec.name, detail_style)
                worksheet.write(row_20, 3, rec.first_contract_date, date_format)
                worksheet.write(row_20, 4, rec.department_id.name, detail_style)
                worksheet.write(row_20, 5, rec.parent_id.name, detail_style)
                list_20_year_index += 1
                row_20 += 1
            index_25_year_row = row_20

        if list_25_year:

            list_25_year_index = 1
            worksheet.write_merge(index_25_year_row + 1, index_25_year_row + 2, 0, 6, "20 Year Anniversary", header_style)

            worksheet.write(index_25_year_row + 3, 1, '#', title_style)
            worksheet.write(index_25_year_row + 3, 2, 'Employee', title_style)
            worksheet.write(index_25_year_row + 3, 3, 'Joining Date', title_style)
            worksheet.write(index_25_year_row + 3, 4, 'Department', title_style)
            worksheet.write(index_25_year_row + 3, 5, 'Manager', title_style)
            row_25 = index_25_year_row + 4
            for rec in list_25_year:
                worksheet.write(row_25, 1, list_25_year_index, detail_style)
                worksheet.write(row_25, 2, rec.name, detail_style)
                worksheet.write(row_25, 3, rec.first_contract_date, date_format)
                worksheet.write(row_25, 4, rec.department_id.name, detail_style)
                worksheet.write(row_25, 5, rec.parent_id.name, detail_style)
                list_25_year_index += 1
                row_25 += 1


        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream.read()

    def action_send_birthday_reminder(self):
        birthday_list = self.generate_birthday_list_excel_report()
        employee = self.env['hr.employee'].sudo().search([])
        for emails in employee:
            email_values = {
                'subject': 'Reminder',
                'body_html': '<p>Hello,%s</p><p>Please find the attached report.</p>' % (emails.name),
                'email_to': emails.work_email,
                'attachment_ids': [(0, 0, {
                    'name': 'reminders.xlsx',
                    'datas': ustr(base64.b64encode(birthday_list)),
                    'res_model': 'hr.report.configuration',
                    'type': 'binary',
                    'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                })],
            }
            mail_id = self.env['mail.mail'].create(email_values)
            mail_id.send()
