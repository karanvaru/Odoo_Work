# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    send_wish_employee = fields.Boolean(string='Send birthday with to employee?',
                                        config_parameter='employee.send_wish_employee')
    emp_wish_template_id = fields.Many2one('mail.template', string='Employee Email Template',
                                           domain=[('model', '=', 'hr.employee')])

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        emp_wish_template_id = IrConfigParameter.get_param("employee.emp_wish_template_id")
        res.update(
            emp_wish_template_id=int(emp_wish_template_id),
        )
        return res

    def set_values(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        super(ResConfigSettings, self).set_values()
        IrConfigParameter.set_param("employee.emp_wish_template_id", self.emp_wish_template_id.id or False)
