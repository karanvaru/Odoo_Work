# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import *


class helpdesk_ticket_age(models.Model):
    _inherit = 'helpdesk.ticket'

    age_audit_ids = fields.One2many('stages.history', 'ticket_id', index=True, store=True)
    current_stage_id =fields.Many2one('helpdesk.stage','Stage',compute="compute_current_stage")
    current_team_id = fields.Many2one('helpdesk.team','Team',compute="compute_current_team")

    

    @api.model
    def set_create_date_for_old_ticket(self):
        self._cr.execute("""INSERT INTO stages_history (ticket_id, date_in, stage_id)
                    SELECT p.id, p.create_date,r.id FROM helpdesk_ticket p
                    left join helpdesk_stage r on (r.id=p.stage_id)
                    WHERE r.is_close != True""")

    @api.model
    def create(self, values):
        line = super(helpdesk_ticket_age, self).create(values)
        line.age_audit_ids.create({'ticket_id': line.id,
                            #    'stage_id': line.stage_id.id,
                               'from_stage_id':line.stage_id.id,
                               'to_stage_id':line.stage_id.id,
                            #    'team_id':line.team_id.id,
                               'from_team_id': line.team_id.id,
                                'to_team_id': line.team_id.id,
                               'date_in': fields.datetime.today()})
        return line
    @api.multi
    def compute_current_stage(self):
        for rec in self:
            c_stage = self.env['stages.history'].search([('ticket_id','=',rec.id)],order="id desc",limit=1)
            for record in c_stage:
                if not rec.current_stage_id.id:
                    rec.current_stage_id = rec.stage_id
                rec.current_stage_id = record.to_stage_id
    @api.multi
    def compute_current_team(self):
        for rec in self:
            c_team = self.env['stages.history'].search([('ticket_id','=',rec.id)],order="id desc",limit=1)
            for record in c_team:
                if not rec.current_team_id.id:
                    rec.current_team_id = rec.team_id
                rec.current_team_id = record.to_team_id   

    @api.multi
    def write(self, vals):
        
        res = super(helpdesk_ticket_age, self).write(vals)
       
        for rec_age in self:
            if 'stage_id' in vals and vals['stage_id']:
                closing_value = self.env['helpdesk.stage'].sudo().browse(vals['stage_id'])
                for rec in rec_age.age_audit_ids:
                    if not rec.date_out:
                        rec.date_out = fields.datetime.today()
                
                if closing_value.is_close != True :                    

                        rec_age.age_audit_ids.create({'ticket_id': rec_age.id,
                                            #    'stage_id': rec_age.stage_id.id,
                                                'from_stage_id':rec_age.current_stage_id.id,
                                               'to_stage_id':rec_age.stage_id.id,
                                               'from_team_id': rec_age.current_team_id.id,
                                               'to_team_id': rec_age.team_id.id,
                                               'date_in': fields.datetime.today(),})
        
        return res
  




class HElpdeskSla(models.Model):
    _name = 'stages.history'
    _discription = "Stages History"

    name = fields.Char('Name')
    ticket_id = fields.Many2one('helpdesk.ticket')
    stage_id = fields.Many2one('helpdesk.stage')

    from_stage_id = fields.Many2one('helpdesk.stage')
    to_stage_id = fields.Many2one('helpdesk.stage')
    current_stage_id =fields.Many2one('helpdesk.stage')

    date_in = fields.Datetime()
    date_out = fields.Datetime()
    days = fields.Char('Open Days',compute="_compute_days",store=True)
    from_team_id = fields.Many2one('helpdesk.team','From Team')
    to_team_id = fields.Many2one('helpdesk.team','To Team')
    sla_days = fields.Char('SLA Days',compute="_compute_sla_days")
    tat_status = fields.Char('TAT Status')
    tat_time = fields.Datetime('TAT Time')
    current_user = fields.Char('User',default=lambda self: self.env.user.name,readonly="1")


    @api.depends('date_in', 'date_out')
    def _compute_days(self):
        for res in self:
            if res.date_in and res.date_out:
                if res.date_out:
                    # date_start = datetime.strftime(res.date_in,'%Y-%m-%d %H:%M:%S')
                    # date_end =datetime.strftime(res.date_out,'%Y-%m-%d %H:%M:%S')
                    # start = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
                    # end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
                    # self.days = (end - start).total_seconds()

                    self.days = str(((res.date_out - res.date_in))).split('.')[0]
                    # start = datetime.strftime(self.part_request_in, '%Y-%m-%d %H:%M:%S')
                    # end = datetime.strftime(self.part_request_out, '%Y-%m-%d %H:%M:%S')
                    # start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                    # end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

    @api.depends('date_in', 'date_out')
    def _compute_sla_days(self):
        for res in self:
            if res.date_in and res.date_out:
                res.sla_days = str(((res.date_out - res.date_in).total_seconds())/60).split('.')[0]
            else:
                res.sla_days = str(((datetime.today() - res.date_in).total_seconds())/60).split('.')[0]

    

    @api.multi
    def _compute_tat_status(self):
        
            for rec in self:
                if rec.to_stage_id:
                    tatlines = rec.env['helpdesk.stage'].search([('id','=',rec.to_stage_id.id)])
                    for t in tatlines:
                        t_status = t.tat_id.tat_value
                        if int(t_status) > int(rec.sla_days):
                            rec.tat_status = "Pass"
                        else:
                            rec.tat_status="Fail"


            


class helpdesk_ticket_tat(models.Model):
    _name = 'helpdesk.ticket.tat'
    _discription = "Helpdesk Ticket TAT"

    name = fields.Char('TAT Name')

    tat_value = fields.Float('TAT Value')

class helpdesk_stage_inherit(models.Model):
    _inherit = 'helpdesk.stage'

    tat_id = fields.Many2one('helpdesk.ticket.tat','TAT')