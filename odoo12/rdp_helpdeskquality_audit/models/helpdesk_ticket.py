
import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time



class KAMEsclationInherit(models.Model):
    _inherit ="helpdesk.ticket"

    qa_ticket_count = fields.Integer(string="QA Count",compute="compute_qa_count")
    qa_associate_emp = fields.Many2one('res.users','Associate Employee')
   
   
   
 
        
    @api.multi
    def compute_qa_count(self):
        for rec in self:
            count_values = self.env['quality.audit'].search_count([('helpdesk_ticket_id','=',rec.id)])
            rec.qa_ticket_count = count_values


    def action_to_qa_ticket(self, vals):

        qa_helpdesk_id = self.env['quality.audit']
        print("*********sabitha**********")

        vals = {
            'helpdesk_ticket_id': self.id,
        }
        
        new_val = qa_helpdesk_id.create(vals)
    


        return new_val


    def open_qa_tickets(self):

            self.ensure_one()
            return {
                'name': 'Quality Audit',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'quality.audit',
                'domain': [('helpdesk_ticket_id','=',self.id)],
            }   
   
              

