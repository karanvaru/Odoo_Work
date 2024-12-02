# -*- coding: utf-8 -*-
from odoo import models, api, fields
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

#
# class ResUsers(models.Model):
#     _inherit = "res.users"
#
#     @api.model
#     def get_employee_birthday_info(self):
#         reminder_before_1day = self.env['ir.config_parameter'].sudo().get_param("employee.reminder_before_1day")
#         next_date = datetime.today() + timedelta(days=int(reminder_before_1day or 1))
#         employee_ids = self.env['hr.employee'].search([('birthday_date', '=', next_date.day),
#                                                        ('birthday_month', '=', next_date.month)])
#         return {'employees': employee_ids, 'date': next_date.strftime(DEFAULT_SERVER_DATE_FORMAT)}


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    birthday_date = fields.Integer(compute="_get_birthday_identifier", store=1)
    birthday_month = fields.Integer(compute="_get_birthday_identifier", store=1)

    @api.multi
    @api.depends('birthday')
    def _get_birthday_identifier(self):
        for employee in self.filtered(lambda e: e.birthday):
            employee.birthday_date = employee.birthday.day
            employee.birthday_month = employee.birthday.month

    @api.model
    def send_birthday_reminder_employee(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        template_env = self.env['mail.template']
        send_employee = bool(IrConfigParameter.get_param("employee.send_wish_employee"))

        # Send birthday wish to employee
        if send_employee and self.active == False:
            domain = [('birthday_date', '=', datetime.today().day),
                      ('birthday_month', '=', datetime.today().month)]
            emp_template_id = IrConfigParameter.get_param("employee.emp_wish_template")
            if emp_template_id:
                template_id = template_env.sudo().browse(int(emp_template_id))
                for employee in self.env['hr.employee'].search(domain):
                    template_id.send_mail(employee.id,force_send=True)

