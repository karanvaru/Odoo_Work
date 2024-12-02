# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_no = fields.Char(string='Employee No.')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HrEmployee, self).create(vals_list)
        for data in res:

            if(
                self.env['ir.config_parameter'].sudo().get_param(
                    'sh_auto_create') and not data.emp_no
            ):
                seq = self.env['ir.sequence'].next_by_code('hr.employee')
                data.emp_no = seq
        return res

    def action_create_sequence(self):
        if not self.emp_no:
            seq = self.env['ir.sequence'].next_by_code('hr.employee')
            self.emp_no = seq

    def action_generate(self):
        for rec in self:
            if not rec.emp_no:
                seq = self.env['ir.sequence'].next_by_code('hr.employee')
                rec.emp_no = seq
