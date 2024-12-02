# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    send_wish_employee = fields.Boolean(string='Send birthday with to employee?',
                                        config_parameter='employee.send_wish_employee')
    emp_wish_template = fields.Many2one('mail.template', string='Employee Email Template',
                                           domain=[('model', '=', 'hr.employee')])
    reminder_before_day = fields.Integer(string='Send reminder before days')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        emp_wish_template = IrConfigParameter.get_param("employee.emp_wish_template")
        # reminder_before_1day = IrConfigParameter.get_param("employee.reminder_before_1day")
        res.update(
            emp_wish_template=int(emp_wish_template),
            # reminder_before_1day=int(reminder_before_1day),
        )
        return res

    def set_values(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        super(ResConfigSettings, self).set_values()
        IrConfigParameter.set_param("employee.emp_wish_template", self.emp_wish_template.id or False)
        # IrConfigParameter.set_param("employee.reminder_before_1day", self.reminder_before_1day or 0)
