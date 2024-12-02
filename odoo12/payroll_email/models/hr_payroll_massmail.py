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

from odoo import api,fields, models

class PayslipMassMail(models.TransientModel):
    _name="payroll.mass.mail"
    
    payslip_ids = fields.Many2many('hr.payslip',string="Payslips",required=True)
   
# function to send mass Payslip
    @api.multi
    def send_mass_ps_mail(self):
        values = self.payslip_ids
        for plp in values:
            email_action = plp.action_my_payslip_sent()
            if email_action and email_action.get('context'):
                email_ctx = email_action['context']
                email_ctx.update(default_email_from=values.company_id.email)
                plp.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))  
        return True