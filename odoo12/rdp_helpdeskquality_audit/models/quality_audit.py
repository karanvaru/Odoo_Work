# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import string
from unicodedata import category, name
from odoo import api, fields, models, _
from datetime import date, datetime
import time
from odoo.http import request



class QualityAudit(models.Model):

    _name = "quality.audit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Quality Audit"


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket',"Helpdesk Ticket",track_visibility='onchange')
    state = fields.Selection([
        ('open', 'Open'), 
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED'),

    ], string='Status', readonly=True, default='open',track_visibility='always')
    open_days = fields.Char(string="Opendays",compute="compute_open_days")
    closed_date = fields.Datetime('Closed Date')
    cancelled_date = fields.Datetime('Cancelled Date')
    description = fields.Text('Description',track_visibility='always')
    employee_name = fields.Char('Assigned By',readonly="True",track_visibility='always')
    internal_notes = fields.Html(string='Internal Notes',track_visibility='always')
    category_id = fields.Many2one('qualityaudit.category',string="QA Category",track_visibility='onchange')
    # agent_name = fields.Char('Agent Name', store=True)
    agent_id = fields.Many2one('res.users','Agent Name', related= "helpdesk_ticket_id.user_id")
    base_url = fields.Char('Base Url')
    email_to = fields.Char('Associate Email')
    associate_name = fields.Char('Associate Name',track_visibility='always')
    # qa_associate_emp = fields.Many2one('res.users','Associate Employee')
    qa_category_ids = fields.Many2many('qualityaudit.category', string="QA Category", track_visibility='onchange')
    call_number = fields.Char(string="Call Number",track_visibility='always')
    call_date = fields.Date(string="Call Date",track_visibility='always')
    qa_associate_employee_id = fields.Many2one('res.users', string="Associate Name(New)", track_visibility='always')
    


    @api.model
    def create(self, vals):
            vals.update({
                'name' : self.env['ir.sequence'].next_by_code('quality.audit.sequence'),
                'base_url' : self.env['ir.config_parameter'].get_param('web.base.url')
            })
           
            res = super(QualityAudit, self).create(vals)
            # print("*********************res***********",res)
            # print('============url=======',self.base_url)
        
            # template_id = self.env['ir.model.data'].get_object_reference('rdp_helpdeskquality_audit','quality_audit_email_template')[1]
            # template = self.env['mail.template'].browse(template_id)
            # template.send_mail(res.id, force_send=True)
            return res
    
    
    @api.multi
    def action_to_send_mail(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        template_id = self.env['ir.model.data'].get_object_reference('rdp_helpdeskquality_audit','quality_audit_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url) 

    def action_to_closed(self):
        self.closed_date = datetime.today() 
        self.state = 'closed'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        template_id = self.env['ir.model.data'].get_object_reference('rdp_helpdeskquality_audit','quality_audit_email_ticket_close_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)

    @api.multi
    def action_ticket_closing_remainder(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        template_id = self.env['ir.model.data'].get_object_reference('rdp_helpdeskquality_audit', 'quality_audit_ticket_close_remainder_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url)


    def server_action_close_tickets(self):
        for rec in self:
            rec.action_to_closed()
              
    @api.multi
    def action_to_cancel(self):
        self.cancelled_date = datetime.today()
        self.state = 'cancel'

    @api.multi
    def action_set_open(self):
        self.write({'state': 'open'})
    

    @api.depends('cancelled_date')
    def compute_open_days(self):
        for record in self:
            if record['closed_date']:
                record['open_days'] = str((record['closed_date'] - record['create_date']).days) + " Days"
            else:
                record['open_days'] = str((datetime.today() - record['create_date']).days) + " Days"

            record['open_days'] = record['open_days'].split(',')[0]
            if record['open_days'] == '0:00:00':
                record['open_days'] = '0 Days'

    @api.depends('helpdesk_ticket_id')
    def compute_agent_name(self):
        print("The copute function is calling")
        for rec in self:
            emp_rec = rec.env['helpdesk.ticket'].search([('id', '=', rec.helpdesk_ticket_id)])
            print("The selected emp of helpdesk ticket is ====================", emp_rec)
            for emp in emp_rec:
                rec.agent_name = emp.user_id.name

    def create_emp_ed(self):
        self.ensure_one()
        return {
                'name': 'Employee Disciplinary',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'employee.disciplinary',
                'domain': [('qa_ed_id','=',self.id)],
            }              
                            


class QACategory(models.Model):

    _name = "qualityaudit.category"
    _description = "Quality Audit Category"   


    name = fields.Char('Name')  

class QualityAuditEmployeeDisciplinary(models.Model):

    _inherit = "employee.disciplinary"


    qa_ed_id = fields.Many2one('quality.audit','Quality Audit ED')               

   
                                   

   














