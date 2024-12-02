# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time



class KedEscalation(models.Model):

    _name = "ked.escalation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "KED Escalation"
   


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    helpdesk_ticket_fed_id = fields.Many2one('helpdesk.ticket', string="Helpdesk Ticket", track_visibility='onchange',store="True")
    helpdesk_team_id = fields.Many2one('helpdesk.team',string="Helpdesk Team",related='helpdesk_ticket_fed_id.team_id',track_visibility='onchange',store="True",readonly=True)
    assigned_to = fields.Many2one('res.users',string="Assigned To",related='helpdesk_ticket_fed_id.user_id',track_visibility='onchange',store="True",readonly=True)
    priority = fields.Selection([
        ('[0]','All'),
        ('[1]','Low priority'),
        ('[2]','High priority'),
        ('[3]','Urgent'),
        ],string='Priority',related='helpdesk_ticket_fed_id.priority',track_visibility='always', store="True")
    state = fields.Selection([
        ('open', 'Open'), 
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED'),

    ], string='Status', readonly=True, default='open',track_visibility='always')
    helpdesk_opendays = fields.Char('Ticket Opendays',track_visibility='always',compute="assign_helpdesk_opendays")
    open_days = fields.Char(string="KED Opendays",compute="compute_open_days")
    closed_date = fields.Datetime('Closed Date')
    cancelled_date = fields.Datetime('Cancelled Date')
    effort = fields.Float('Effort',compute="comput_total_effort")
    activities = fields.Integer('Activities',compute="comput_total_activities")
    # kam_created_by = fields.Char()
    ked_sla_date = fields.Datetime('KED SLA',track_visibility='always')
    ked_sla_days = fields.Char('KED SLA Days',compute="compute_ked_sla_days")
    designation =  fields.Char('Designation',compute ='compute_designation')
    emp_mobile =  fields.Char('Mobile',compute ='compute_designation')
    delay_days = fields.Char('Days Delay',compute="compute_delay_days")
    ked_sla_days_num = fields.Integer('Ked SLA Days Number',compute="compute_ked_sla_days_number")
    base_url = fields.Char('Base Url')
    # print("*************ked sla number days ************",ked_sla_days_number)
    escalation_id =fields.Many2one('res.users', string="Escalated By")
    global_feedback_id =fields.Many2one('global.feedback', string="Global Feedback")

    @api.multi
    def compute_designation(self):
        for rec in self:
            emp_rec = rec.env['hr.employee'].search([('user_id', '=', rec.create_uid.id)])
            for emp in emp_rec:
                rec.designation = emp.job_id.name
                rec.emp_mobile = emp.mobile_phone
            
   
            

    @api.multi    
    def get_helpdesk_id_in_ked_chatter(self):
        for rec in self:
    # Helpdesk ID in Chatter.
            helpdesk_id =  self.env['helpdesk.ticket'].search([('id','=',rec.id)])
            if helpdesk_id:
                hid_message = _('This Is the Helpdesk Ticket : <a href="#" data-oe-id="%s" data-oe-model="ked.escalation">%s</a>') % (rec.id)
                helpdesk_id.message_post(body = hid_message)    

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('ked.escalation.sequence'),
            'base_url' : self.env['ir.config_parameter'].get_param('web.base.url')
        })
        res = super(KedEscalation, self).create(vals)
        print("*********************res***********",res)
        print('============url=======',self.base_url)
        
        template_id = self.env['ir.model.data'].get_object_reference('rdp_ked_escalation','kam_escalation_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)
        return res
          
       



    @api.multi
    def action_to_closed(self):
        self.closed_date = datetime.today()
        self.state = 'closed'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        template_id = self.env['ir.model.data'].get_object_reference('rdp_ked_escalation','kam_escalation_close_email_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, base_url) 

    @api.multi
    def action_to_send_warning(self):
        # self.closed_date = datetime.today()
        # self.state = 'closed'
        # base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        template_id = self.env['ir.model.data'].get_object_reference('rdp_ked_escalation','kam_escalation_warning_template')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)      

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
            record.open_days = 0
            if record.closed_date:
                close_date_str = datetime.strftime(record.closed_date, '%Y-%m-%d %H:%M')
                open_date_str = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M')
                close_date = datetime.strptime(close_date_str, '%Y-%m-%d %H:%M')
                open_date = datetime.strptime(open_date_str, '%Y-%m-%d %H:%M')
                
                record.open_days =  close_date - open_date
            else:
                current_date_str = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M')
                current_date= datetime.strptime(current_date_str, '%Y-%m-%d %H:%M')
                open_date_str = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M')
                open_date = datetime.strptime(open_date_str, '%Y-%m-%d %H:%M')

                record.open_days =  current_date - open_date

          
    @api.multi
    def compute_delay_days(self):
        for rec in self:
            if rec.closed_date and rec.ked_sla_date:
                
                closed_str = datetime.strftime(rec.closed_date, '%Y-%m-%d %H:%M')
                closed_dt = datetime.strptime(closed_str, '%Y-%m-%d %H:%M')
                ked_dt_str = datetime.strftime(rec.ked_sla_date, '%Y-%m-%d %H:%M')
                ked_dt = datetime.strptime(ked_dt_str,'%Y-%m-%d %H:%M')

                rec.delay_days = closed_dt - ked_dt
            else:
               
                rec.delay_days = '00:00:00'
            if rec.ked_sla_date and not rec.closed_date:
                current_date_str = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M')
                current_date= datetime.strptime(current_date_str, '%Y-%m-%d %H:%M')
                ked_dt_str = datetime.strftime(rec.ked_sla_date, '%Y-%m-%d %H:%M')
                ked_dt = datetime.strptime(ked_dt_str,'%Y-%m-%d %H:%M')
                
                rec.delay_days = current_date - ked_dt
            else:
                rec.delay_days = '00:00:00'


    @api.multi
    def comput_total_effort(self):
        
        for record in self:
            for reco in record:
                h_id = reco.id
                if h_id:
                    total_effort_lines = reco.env['time.tracking.users'].search([('ked_id.id','=',h_id)])
                    total_effort_count = reco.env['time.tracking.users'].search_count([('ked_id.id','=',h_id)])
                if total_effort_count:
                    for rec in total_effort_lines:
                        reco['effort'] = reco['effort'] + rec['duration']
    @api.multi
    def comput_total_activities(self):
        
        for record in self:
            for reco in record:
                h_id = reco.id
                if h_id:
                    total_effort_count = reco.env['time.tracking.users'].search_count([('ked_id.id','=',h_id)])
                    reco['activities'] = total_effort_count
    @api.multi
    def compute_ked_sla_days(self):
        for record in self:
            # if record['ked_sla_date']:
            if record.ked_sla_date:
                ked_sla_str = datetime.strftime(record.ked_sla_date, "%Y-%m-%d %H:%M:%S")
                ked_sla = datetime.strptime(ked_sla_str, "%Y-%m-%d %H:%M:%S") 
                create_date_str = datetime.strftime(record.create_date, "%Y-%m-%d %H:%M:%S")
                create_dt = datetime.strptime(create_date_str, "%Y-%m-%d %H:%M:%S")
                record.ked_sla_days = ked_sla - create_dt
            else:
                record.ked_sla_days = '00:00:00'
    @api.multi
    def compute_ked_sla_days_number(self):
        for record in self:
            if record['ked_sla_date']:
                record['ked_sla_days_num'] = (record['ked_sla_date'] - record['create_date']).days 
            else:
                record['ked_sla_days_num'] = 0

    @api.onchange('helpdesk_ticket_fed_id')
    def assign_helpdesk_opendays(self):
        for rec in self:
            rec.helpdesk_opendays = rec.helpdesk_ticket_fed_id.ticket_opendays
