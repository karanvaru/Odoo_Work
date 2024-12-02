# -*- coding: utf-8 -*-
###################################################################################
#    Payroll Email Project 
#
#    E-Soft Solution
#    Copyright (C) 2018-TODAY  E-Soft Solution (<https://www.sagarnetwork.com>).
#    Author: Sagar Jayswal (<https://www.sagarnetwork.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; See the GNU Affero General Public 
#    License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from odoo import fields, models, tools, api


class PayrollInheritsMail(models.Model):
    _inherit = 'hr.payslip'
    
    user_id = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    # partner_id = fields.Many2one('res.partner', string='Related Partner')
    flag  = fields.Boolean('Flag',default=False)
    
    # @api.onchange('employee_id')
    # def change_partner_id(self):
    #     if self.employee_id:
    #         self.partner_id = self.employee_id.user_id.partner_id.id

    @api.multi     
    def view_mass_payroll_wizard(self):
        payslip_ids = []
        active_ids = self.env.context.get('active_ids',[])
        psp_id = self.env['hr.payslip'].search([('id','in',active_ids)])
        for rec in psp_id:
            if rec.flag == False:
                payslip_ids.append(rec.id)   
        vals = ({'default_payslip_ids':payslip_ids})
        return {
            'name':"Send Mass Payslips by Mail",
            'type': 'ir.actions.act_window', 
            'view_type': 'form', 
            'view_mode': 'form',
            'res_model': 'payroll.mass.mail', 
            'target': 'new', 
            'context': vals,
            }

    @api.multi
    def action_my_payslip_sent(self):
        """ Action to send Payroll through Email."""
        self.ensure_one()
        template = self.env.ref('payroll_email.email_template_for_my_payroll')
        if template:
            self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)
            self.flag = True