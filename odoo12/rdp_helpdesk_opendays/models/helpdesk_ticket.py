# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
import datetime
from datetime import date, datetime
import time

_logger = logging.getLogger(__name__)

class HelpdeskOpenDays(models.Model):

    _inherit = 'helpdesk.ticket'


    
    team_opendays = fields.Char('Team Opendays',compute="compute_team_opendays")
    team_date = fields.Datetime('Team Date',default=datetime.today())
    asp_opendays = fields.Char('ASP Opendays',compute="compute_asp_opendays")
    asp_date = fields.Datetime('ASP Date',default=datetime.today())
    stage_date = fields.Datetime('Stage Date',default=datetime.today())
    stage_days = fields.Char('Stage Opendays',compute="compute_stage_days")
    assign_date = fields.Datetime('Assign Date',default=datetime.today())
    assign_days = fields.Char('Agent Opendays',compute = "compute_assign_days")
    ticket_opendays = fields.Char('Ticket Opendays',compute = "compute_ticket_open_days")
    # asp_opendays_count = fields.Integer('ASP Opendays Count',compute="compute_asp_opendays_count")
    portal_ticket_opendays = fields.Char('Ticket Opendays',compute="compute_ticket_opendays")
    portal_agent_opendays = fields.Char('Agent Opendays',compute="compute_agent_opendays")


    @api.onchange('team_id','team_date')
    def onchange_team_id(self):
        self.team_date = datetime.today()



    @api.onchange('stage_id','stage_date')
    def onchange_stage_id(self):
        self.stage_date = datetime.today()
   

    @api.onchange('asp_engineer_id','asp_date')
    def onchange_asp_engineer_id(self):
        self.asp_date = datetime.today()

      

    @api.onchange('user_id','assign_date')
    def onchange_user_id(self):
        self.assign_date = datetime.today()    
    



   
    def compute_team_opendays(self):
       for record in self:
        tm = record.team_date
        if record['close_date']:
            if tm:
                record['team_opendays'] = str((record['close_date'] - tm)) 
                record['team_opendays'] = record['team_opendays'][:-10]
        else:
            if tm:
                record['team_opendays'] = str((datetime.today() - tm)) 
                record['team_opendays'] = record['team_opendays'][:-10]
        if not record.team_id:
             record['team_opendays'] = 0


    def compute_asp_opendays(self):
       for record in self:
        asp = record.asp_date
        if record['close_date']:
            if asp:
                record['asp_opendays'] = str((record['close_date'] - asp)) 
                record['asp_opendays'] = record['asp_opendays'][:-10]
        else:
            if asp:
                record['asp_opendays'] = str((datetime.today() - asp)) 
                record['asp_opendays'] = record['asp_opendays'][:-10]
        if not record.asp_engineer_id:
             record['asp_opendays'] = 0

    def compute_assign_days(self):
        for record in self:
            asn = record.assign_date
            if record['close_date']:
                if asn:
                    record['assign_days'] = str((record['close_date'] - asn))
                    record['assign_days'] = record['assign_days'][:-10]
            else:
                if asn:
                    record['assign_days'] = str((datetime.today() - asn)) 
                    record['assign_days'] = record['assign_days'][:-10]
            if not record.user_id:
                record['assign_days'] = 0

    def compute_stage_days(self):
        for record in self:
            stg = record.stage_date
            if record['close_date']:
                if stg:
                    record['stage_days'] = str((record['close_date'] - stg))
                    record['stage_days'] = record['stage_days'][:-10]
            else:
                if stg:
                    record['stage_days'] = str((datetime.today() - stg)) 
                    record['stage_days'] = record['stage_days'][:-10]
            if not record.stage_id:
                record['stage_days'] = 0 

    def compute_ticket_open_days(self):
        for record in self:
            if record['close_date']:
                record['ticket_opendays'] = str((record['close_date'] - record['create_date'])) 
                record['ticket_opendays'] = record['ticket_opendays'][:-10]
            else:
                    record['ticket_opendays'] = str((datetime.today() - record['create_date'])) 
                    record['ticket_opendays'] = record['ticket_opendays'][:-10]

    @api.multi
    def compute_ticket_opendays(self):
        for rec in self:
            portal_tod  = rec.ticket_opendays 
            rec.portal_ticket_opendays = portal_tod[:-6]                   
           

    @api.multi
    def compute_agent_opendays(self):
        for rec in self:
            portal_aod  = rec.assign_days 
            rec.portal_agent_opendays = portal_aod[:-6]          

        
                        












