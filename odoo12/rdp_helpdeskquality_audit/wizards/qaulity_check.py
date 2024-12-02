from email.policy import default
from odoo import models, fields
from datetime import datetime


class QualityCheck(models.TransientModel):
    _name = 'quality.check'
    _description = 'Quality Check'

    
    emp_name = fields.Char('Employee Name',default=lambda self: self.env.user.name,readonly="1")
    quality_check_desc= fields.Text('Disciption')
   
    def action_to_wizard(self):

        quality_id = self.env['quality.audit']
      
        # active_id = self._context.get('active_id')
        # active_model = self._context.get('active_model')
        # active_record = self.env[active_model].browse(active_id)
        print("*********sabitha**********")
        active_id = self._context.get('active_id')
        h_id = self.env['helpdesk.ticket'].browse(active_id)
        vals = {
            'employee_name':self.emp_name,
            'description': self.quality_check_desc,
          
            'helpdesk_ticket_id' :h_id.id,
           
        }
        new_val = quality_id.create(vals)

        return new_val
        # return "sabitha"
       
    