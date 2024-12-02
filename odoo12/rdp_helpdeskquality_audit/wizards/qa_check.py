# -*- coding: utf-8 -*-

from odoo import models, fields


class QualityCheckAudit(models.TransientModel):
    _name = 'qualityaudit.check'
    _description = 'Quality Audit Check'

    emp_name = fields.Char('Employee Name',default=lambda self: self.env.user.name,readonly="1")
    emp_email = fields.Char('Employee email',related='qa_associate_employee_id.login')
    emp_qa_name = fields.Char('Emp Name',related='qa_associate_employee_id.name')
    quality_check_desc= fields.Text('Disciption')
    qa_category_id = fields.Many2one('qualityaudit.category',"Category")
    qa_category_ids = fields.Many2many('qualityaudit.category', string="QA Category")
    wizard_internal_notes = fields.Html(string='Internal Notes')
    qa_associate_employee_id = fields.Many2one('res.users','Associate')
    base_url = fields.Char('Base Url', default=lambda self: self.env['ir.config_parameter'].get_param('web.base.url'))
   
    def action_to_wizard(self):

        quality_id = self.env['quality.audit']
      
        # active_id = self._context.get('active_id')
        # active_model = self._context.get('active_model')
        # active_record = self.env[active_model].browse(active_id)
        print("*********sabitha**********")
        active_id = self._context.get('active_id')
        h_id = self.env['helpdesk.ticket'].browse(active_id)

        # qlty_id = self.env['quality.audit'].search([('helpdesk_ticket_id','=',h_id.id)],limit = 1)
        # for qt in qlty_id:
        #     q_id = qt.id
        print("=======email========",self.emp_email)
        vals = {
            'employee_name':self.emp_name,
            'description': self.quality_check_desc,
            'category_id':self.qa_category_id.id,
            'qa_category_ids': [(6, 0, self.qa_category_ids.ids)],
            'internal_notes':self.wizard_internal_notes,
            # 'qa_associate_emp': self.qa_associate_employee,
            'email_to':self.emp_email,
            'associate_name': self.emp_qa_name,
            'qa_associate_employee_id': self.qa_associate_employee_id.id,
            'helpdesk_ticket_id' :h_id.id

            
           
        }
       
        new_val = quality_id.create(vals)
        # print('===========new valus====',new_val)
        # # var = self.env['journal.audit'].browse(self.env.context.get('active_id'))
        # # print('========================Dayan=======================',var)
        # # issue_content = "  Hello  <b>" +var.journal_entry_id.create_uid.name + ",</b><br>Referring to the recorded transaction, the auditor error is noted below. <br><b>" + str(var.journal_entry_id.name) + ",</b><br><br> Description: " + self.description
        # issue_content = 'Dear &nbsp;' + self.qa_associate_employee.name + ',</b><br></b><br> You have a quality audit performed on a ticket you worked on. Please acknowledge or revert for any clarifications. </b><br></b><br>Please click on the link to view.<a href ="' + self.base_url+'/web#id='+ str(new_val.id)+'&amp;action=733&amp;model=quality.audit&amp;view_type=form&amp;menu_id=93" >Click Here</a> </b><br></b><br> Thank you!!!'
        # # print("*************new value******",new_val.create_uid)
        # main_content = {
        #     'subject': 'Helpdesk Quality Audit Ticket Created  ' + new_val.name + '.',
        #     'author_id': new_val.create_uid.id,
        #     'body_html': issue_content,
        #     'email_to':  self.qa_associate_employee.email,
            
        
        # }
        # # # print('=========author id ==========',author_id)
        # self.env['mail.mail'].sudo().create(main_content).send()
    
        return new_val

  