
from odoo import models, api, fields
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_employee_birthday_info(self):
        reminder_before_day = self.env['ir.config_parameter'].sudo().get_param("employee.reminder_before_day")
        next_date = datetime.today() + timedelta(days=int(reminder_before_day or 1))
        employee_ids = self.env['hr.employee'].search([('anniversary_date', '=', next_date.day),
                                                       ('anniversary_month', '=', next_date.month)])
        return {'employees': employee_ids, 'date': next_date.strftime(DEFAULT_SERVER_DATE_FORMAT)}


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    anniversary_date = fields.Integer(compute="_get_anniversary_identifier", store=1)
    anniversary_month = fields.Integer(compute="_get_anniversary_identifier", store=1)

    @api.multi
    @api.depends('x_studio_joining_date')
    def _get_anniversary_identifier(self):
        for employee in self.filtered(lambda e: e.x_studio_joining_date):
            employee.anniversary_date = employee.x_studio_joining_date.day
            employee.anniversary_month = employee.x_studio_joining_date.month

    @api.model
    def send_anniversary_reminder_employee(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        template_env = self.env['mail.template']
        send_employee = bool(IrConfigParameter.get_param("employee.send_wish_employee"))

        # Send birthday wish to employee
        if send_employee:
            domain = [('anniversary_date', '=', datetime.today().day),
                      ('anniversary_month', '=', datetime.today().month)]
            emp_template_id = IrConfigParameter.get_param("employee.emp_wish_template_id")
            if emp_template_id:
                template_id = template_env.sudo().browse(int(emp_template_id))
                for employee in self.env['hr.employee'].search(domain):
                    template_id.send_mail(employee.id, force_send=True)
