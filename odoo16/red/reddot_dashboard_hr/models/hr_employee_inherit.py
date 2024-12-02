from odoo import models, api, fields, _
from datetime import datetime, date, timedelta
# import datetime
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    color_list = [
        '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
        '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
        '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
        ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
        '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
        '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
        '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
        '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
        '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
        '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
    ]

    def get_last_three_financial_years(self, *post):
        today = datetime.today()
        year = today.year

        if today.month >= 4:
            fy_start = datetime(year, 4, 1)
        else:
            fy_start = datetime(year - 1, 4, 1)

        financial_years = []
        for _ in range(3):
            financial_years.append(fy_start.year)
            fy_start = fy_start - relativedelta(years=1)
        return financial_years

    def find_company_value(self, company):
        company = self.env['res.company'].sudo().search([('name', '=', company)])
        return company

    def find_department_value(self, department):
        department = self.env['hr.department'].sudo().search([('name', '=', department)])
        return department

    def find_job_position_value(self, position):
        job_position = self.env['hr.job'].sudo().search([('name', '=', position)])
        return job_position

    @api.model
    def get_company_data(self):
        data_dct = {}
        company = self.env['res.company'].sudo().search([])
        for rec in company:
            data_dct[rec.id] = rec.name
        return data_dct

    @api.model
    def get_department_data(self):
        department_dct = {}
        department = self.env['hr.department'].sudo().search([])
        for rec in department:
            department_dct[rec.id] = rec.name
        return department_dct

    @api.model
    def get_job_position_data(self):
        job_dct = {}
        department = self.env['hr.job'].sudo().search([])
        for rec in department:
            job_dct[rec.id] = rec.name
        return job_dct

    @api.model
    def get_employee_domain(self, type, **kwargs):
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        headcount_domain = []

        hired_domain = [('date_hired', '!=', False)]
        terminate_domain = [('departure_date', '!=', False)]

        base_domain = []
        if company_data != None:
            company = self.find_company_value(company_data)
            base_domain += [('company_id', '=', company.id)]

        if department != None:
            department = self.find_department_value(department)
            base_domain += [('department_id', '=', department.id)]

        if position != None:
            job_position = self.find_job_position_value(position)
            base_domain += [('job_id', '=', job_position.id)]

        if type == 'headCount' or type == '':
            if gender != None:
                headcount_domain += base_domain + [('gender', '=', gender)]
            if start_date and end_date != None:
                start_date = fields.Date.from_string(start_date)
                end_date = fields.Date.from_string(end_date)
                headcount_domain += base_domain + [('first_contract_date', '<=', end_date),
                                                   (
                                                       'first_contract_date', '>=', start_date)]
        if type == 'hires' or type == '':
            if gender != None:
                hired_domain += base_domain + [('employee_id.gender', '=', gender)]
            if start_date and end_date != None:
                start_date = fields.Date.from_string(start_date)
                end_date = fields.Date.from_string(end_date)
                hired_domain += base_domain + [('date_hired', '>=', start_date), ('date_hired', '<=', end_date)]
        if type == 'terminations' or type == '':
            if start_date and end_date != None:
                terminate_domain += base_domain + [('departure_date', '<=', end_date),
                                                   ('departure_date', '>=', start_date)]
            if gender != None:
                terminate_domain += base_domain + [('gender', '=', gender)]
        return headcount_domain, hired_domain, terminate_domain

    @api.model
    def click_headCount(self, **kwargs):
        headcount_domain, hired_domain, terminate_domain = self.get_employee_domain(**kwargs, type='headCount')

        all_employee = self.search(headcount_domain)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Employee"),
            'res_model': 'hr.employee',
            'view_mode': 'tree',
            'domain': [('id', 'in', all_employee.ids)],
            'views': [(self.env.ref('hr.hr_kanban_view_employees').id, 'tree'),
                      (False, 'form')],
        }

    @api.model
    def click_hires(self, **kwargs):
        headcount_domain, hired_domain, terminate_domain = self.get_employee_domain(**kwargs, type='hires')
        hired_employee = self.env['hr.contract.history'].sudo().search(hired_domain)
        hired_employee_ids = hired_employee.mapped('employee_id')

        return {
            'type': 'ir.actions.act_window',
            'name': _("Hired Employee"),
            'res_model': 'hr.employee',
            'view_mode': 'tree',
            'domain': [('id', 'in', hired_employee_ids.ids)],
            'views': [(self.env.ref('hr.hr_kanban_view_employees').id, 'tree'),
                      (False, 'form')],
        }

    @api.model
    def click_terminations(self, **kwargs):
        headcount_domain, hired_domain, terminate_domain = self.get_employee_domain(**kwargs, type='terminations')
        terminate_employee = self.search(terminate_domain)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Terminate Employee"),
            'res_model': 'hr.employee',
            'view_mode': 'tree',
            'domain': [('id', 'in', terminate_employee.ids)],
            'views': [(self.env.ref('hr.hr_kanban_view_employees').id, 'tree'),
                      (False, 'form')],
        }

    @api.model
    def get_employee_count(self, **kwargs):
        headcount_domain, hired_domain, terminate_domain = self.get_employee_domain(**kwargs, type='')
        hired_employee_list = []

        all_employee = self.search_count(headcount_domain)
        terminate_employee = self.search_count(terminate_domain)
        hired_employee = self.env['hr.contract.history'].sudo().search(hired_domain)
        for rec in hired_employee:
            if rec.employee_id not in hired_employee_list:
                hired_employee_list.append(rec.employee_id)
        return {
            'all_employee': all_employee,
            'terminate_employee': terminate_employee,
            'hired_employee': len(hired_employee_list),
        }

    @api.model
    def get_contract_domain(self, type, **kwargs):
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        today_month = date.today().replace(day=1)
        next_month = today_month + relativedelta(months=1, day=31)
        open_contract_domain = []
        close_contract_domain = []
        upcoming_contract_domain = []
        base_domain = []
        if start_date and end_date != None:
            date_domain = [
                ('date_start', '>=', start_date), ('date_start', '<=', end_date),
                ('date_end', '>=', start_date), ('date_end', '<=', end_date)
            ]
        else:
            date_domain = []
        if position:
            position = self.find_job_position_value(position)
            base_domain.append(('job_id', '=', position.id))
        if gender:
            base_domain.append(('employee_id.gender', '=', gender))

        if department:
            department = self.find_department_value(department)
            base_domain.append(('department_id', '=', department.id))

        if company_data:
            company = self.find_company_value(company_data)
            base_domain.append(('company_id', '=', company.id))

        if type == 'open' or type == '':
            open_contract_domain += base_domain + date_domain + [('state', '=', 'open')]
        if type == 'expired' or type == '':
            close_contract_domain += base_domain + date_domain + [('state', '=', 'close')]
        if type == 'upcoming' or type == '':
            upcoming_contract_domain += base_domain + [('date_end', '>=', today_month), ('date_end', '<=', next_month)]

        return open_contract_domain, close_contract_domain, upcoming_contract_domain

    @api.model
    def get_contract_count(self, **kwargs):
        open_contract_domain, close_contract_domain, upcoming_contract_domain = self.get_contract_domain(**kwargs,
                                                                                                         type='')
        open_contract = self.env['hr.contract.history'].sudo().search_count(open_contract_domain)
        close_contract = self.env['hr.contract.history'].sudo().search_count(close_contract_domain)
        upcoming_contract = self.env['hr.contract.history'].sudo().search_count(upcoming_contract_domain)
        return {
            'open_contract': open_contract,
            'close_contract': close_contract,
            'upcoming_contract': upcoming_contract
        }

    @api.model
    def click_open_contract(self, **kwargs):
        open_contract_domain, close_contract_domain, upcoming_contract_domain = self.get_contract_domain(**kwargs,
                                                                                                         type='open')
        open_contract = self.env['hr.contract.history'].sudo().search(open_contract_domain)

        return {
            'type': 'ir.actions.act_window',
            'name': _("Open Contract"),
            'res_model': 'hr.contract.history',
            'view_mode': 'tree',
            'domain': [('id', 'in', open_contract.ids)],
            'views': [(self.env.ref('hr_contract.hr_contract_history_view_list').id, 'tree'),
                      (False, 'form')],
        }

    @api.model
    def click_expired_contract(self, **kwargs):
        open_contract_domain, close_contract_domain, upcoming_contract_domain = self.get_contract_domain(**kwargs,
                                                                                                         type='expired')

        close_contract = self.env['hr.contract.history'].sudo().search(close_contract_domain)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Expire Contract"),
            'res_model': 'hr.contract.history',
            'view_mode': 'tree',
            'domain': [('id', 'in', close_contract.ids)],
            'views': [(self.env.ref('hr_contract.hr_contract_history_view_list').id, 'tree'),
                      (False, 'form')],
        }

    @api.model
    def click_upcoming_contract(self, **kwargs):
        open_contract_domain, close_contract_domain, upcoming_contract_domain = self.get_contract_domain(**kwargs,
                                                                                                         type='upcoming')

        upcoming_contract = self.env['hr.contract.history'].sudo().search(upcoming_contract_domain)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Upcoming Contract"),
            'res_model': 'hr.contract.history',
            'view_mode': 'tree',
            'domain': [('id', 'in', upcoming_contract.ids)],
            'views': [(self.env.ref('hr_contract.hr_contract_history_view_list').id, 'tree'),
                      (False, 'form')],
        }

    @api.model
    def get_gender_count(self, **kwargs):
        gender_dct = {}
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        domain = []

        if position != None:
            job_position = self.find_job_position_value(position)
            domain += [('job_id', '=', job_position.id)]

        if gender != None:
            domain += [('gender', '=', gender)]

        if department != None:
            department = self.find_department_value(department)
            domain += [('department_id', '=', department.id)]

        if company_data != None:
            company = self.find_company_value(company_data)
            domain += [('company_id', '=', company.id)]

        if start_date and end_date != None:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)
            domain += ('departure_date', '<=', end_date), ('departure_date', '>=', start_date)
        employee_gender_count = self.read_group(
            domain,
            ['gender'], ['gender'])
        gender_dct['male'] = 0
        gender_dct['female'] = 0
        for employee in employee_gender_count:
            if employee['gender'] != False:
                if employee['gender'] not in gender_dct:
                    gender_dct[employee['gender']] = 0
                gender_dct[employee['gender']] += employee['gender_count']
        return gender_dct

    @api.model
    def open_position_employee_type(self, **kwargs):
        employee_type_label = []
        employee_type_value = []
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        domain = []

        if position != None:
            job_position = self.find_job_position_value(position)
            domain += [('job_id', '=', job_position.id)]

        if gender != None:
            domain += [('gender', '=', gender)]

        if company_data != None:
            company = self.find_company_value(company_data)
            domain += [('company_id', '=', company.id)]

        if start_date and end_date != None:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)
            domain += [('first_contract_date', '<=', end_date), ('first_contract_date', '>=', start_date)]

        if department != None:
            department = self.find_department_value(department)
            domain += [('department_id', '=', department.id)]
        employee_type_chart = self.read_group(
            domain,
            ['employee_type'], ['employee_type'])
        for employee_count in employee_type_chart:
            if employee_count['employee_type'] not in employee_type_label:
                employee_type_label.append(employee_count['employee_type'])
                employee_type_value.append(employee_count['employee_type_count'])
        return {
            'employee_type_label': employee_type_label,
            'employee_type_value': employee_type_value,
            'backgroundColor': self.color_list,
        }

    @api.model
    def get_headcount_by_office_pie_chart(self, **kwargs):
        office_type_label = []
        office_type_value = []
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        domain = []

        if position != None:
            job_position = self.find_job_position_value(position)
            domain += [('job_id', '=', job_position.id)]

        if company_data != None:
            company = self.find_company_value(company_data)
            domain += [('company_id', '=', company.id)]

        if start_date and end_date != None:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)
            domain += [('first_contract_date', '<=', end_date), ('first_contract_date', '>=', start_date)]

        if department != None:
            department = self.find_department_value(department)
            domain += [('department_id', '=', department.id)]

        if gender != None:
            domain += [('gender', '=', gender)]
        employee_count_by_office = self.read_group(
            domain,
            ['company_id'], ['company_id'])

        for company in employee_count_by_office:
            company_name = str(company['company_id'][1])
            if company_name not in office_type_label:
                office_type_label.append(company_name)
                office_type_value.append(company['company_id_count'])

        return {
            'office_type_label': office_type_label,
            'office_type_value': office_type_value,
            'backgroundColor': self.color_list,
        }

    @api.model
    def get_headcount_by_department_pie_chart(self, **kwargs):
        department_type_label = []
        department_type_value = []
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        domain = []

        if position != None:
            job_position = self.find_job_position_value(position)
            domain += [('job_id', '=', job_position.id)]

        if company_data != None:
            company = self.find_company_value(company_data)
            domain += [('company_id', '=', company.id)]

        if start_date and end_date != None:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)
            domain += [('first_contract_date', '<=', end_date), ('first_contract_date', '>=', start_date)]

        if department != None:
            department = self.find_department_value(department)
            domain += [('department_id', '=', department.id)]

        if gender != None:
            domain += [('gender', '=', gender)]
        employee_count_by_department = self.read_group(
            domain,
            ['department_id'], ['department_id'])
        for department in employee_count_by_department:
            if department['department_id']:
                department_name = str(department['department_id'][1])
                if department_name not in department_type_label:
                    department_type_label.append(department_name)
                    department_type_value.append(department['department_id_count'])
        return {
            'department_type_label': department_type_label or ['Null'],
            'department_type_value': department_type_value or [0],
            'backgroundColor': self.color_list,
        }

    @api.model
    def get_data_headcount_by_contract_type(self, **kwargs):
        contract_type_label = []
        contract_type_value = []
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        domain = [('contract_type_id', '!=', False)]

        if position != None:
            job_position = self.find_job_position_value(position)
            domain += [('job_id', '=', job_position.id)]

        if gender != None:
            domain += [('employee_id.gender', '=', gender)]

        if company_data != None:
            company = self.find_company_value(company_data)
            domain += [('company_id', '=', company.id)]

        if start_date and end_date:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)
            domain += [('date_start', '>=', start_date),
                       ('date_start', '<=', end_date), ('date_end', '>=', start_date),
                       ('date_end', '<=', end_date)]

        if department != None:
            department = self.find_department_value(department)
            domain += [('department_id', '=', department.id)]
        contract_type = self.env['hr.contract.history'].sudo().search(domain)
        contact_dct = {}
        for contract in contract_type:
            if contract.contract_type_id not in contact_dct:
                contact_dct[contract.contract_type_id] = []
            contact_dct[contract.contract_type_id].append(contract.employee_id)
        for contact_data in contact_dct:
            if contact_data.name not in contract_type_label:
                contract_type_label.append(contact_data.name)
                contract_type_value.append(len(contact_dct[contact_data]))
        return {
            'contract_type_label': contract_type_label or ["Null"],
            'contract_type_value': contract_type_value or [0],
            'backgroundColor': self.color_list,
        }

    @api.model
    def get_headcount_by_job_position(self, **kwargs):
        job_type_label = []
        job_type_value = []
        domain = [('job_id', '!=', False), ]
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']

        if position != None:
            job_position = self.find_job_position_value(position)
            domain += [('job_id', '=', job_position.id)]

        if company_data != None:
            company = self.find_company_value(company_data)
            domain += [('company_id', '=', company.id)]

        if start_date and end_date != None:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)
            domain += [('first_contract_date', '>=', start_date),
                       ('first_contract_date', '<=', end_date)]

        if department != None:
            department = self.find_department_value(department)
            domain += [('department_id', '=', department.id)]

        if gender != None:
            domain += [('gender', '=', gender)]
        employee_count_by_job_position = self.read_group(
            domain,
            ['job_id'], ['job_id'])
        for job in employee_count_by_job_position:
            if job['job_id']:
                job_name = str(job['job_id'][1])
                if job_name not in job_type_label:
                    job_type_label.append(job_name)
                    job_type_value.append(job['job_id_count'])
        return {
            'job_type_label': job_type_label or ['Null'],
            'job_type_value': job_type_value or [0],
            'backgroundColor': self.color_list,
        }

    @api.model
    def get_headcount_by_age_range(self, **kwargs):
        emp_dct = {'21-25': 0, '26-30': 0, '31-35': 0, '36-40': 0, '41-45': 0, '46-50': 0, '50+': 0}
        today = date.today()
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        company_data = kwargs['company']
        department = kwargs['department']
        gender = kwargs['gender']
        position = kwargs['position']
        domain = []

        if position != None:
            job_position = self.find_job_position_value(position)
            domain += [('job_id', '=', job_position.id)]

        if gender != None:
            domain += [('gender', '=', gender)]

        if company_data != None:
            company = self.find_company_value(company_data)
            domain += [('company_id', '=', company.id)]

        if start_date and end_date != None:
            start_date = fields.Date.from_string(start_date)
            end_date = fields.Date.from_string(end_date)
            domain += [('first_contract_date', '<=', end_date), ('first_contract_date', '>=', start_date)]

        if department != None:
            department = self.find_department_value(department)
            domain += [('department_id', '=', department.id)]
        for emp in self.search(domain):
            if emp.birthday:
                b_date = today.year - emp.birthday.year
                if b_date >= 21 and b_date <= 25:
                    emp_dct['21-25'] += 1
                if b_date >= 26 and b_date <= 30:
                    emp_dct['26-30'] += 1
                if b_date >= 31 and b_date <= 35:
                    emp_dct['31-35'] += 1
                if b_date >= 36 and b_date <= 40:
                    emp_dct['36-40'] += 1
                if b_date >= 41 and b_date <= 45:
                    emp_dct['41-45'] += 1
                if b_date >= 46 and b_date <= 50:
                    emp_dct['46-50'] += 1
                if b_date >= 50:
                    emp_dct['50+'] += 1
        employee_age = list(emp_dct.keys())
        employee_count = list(emp_dct.values())
        return employee_age, employee_count, self.color_list
