# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import *


class HelpdeskTATandSLA(models.Model):
    _inherit = 'helpdesk.ticket'

    tat_ids = fields.One2many('tat.sla', 'ticket_id', index=True, store=True)
    current_stage_id =fields.Many2one('helpdesk.stage','Stage',compute="compute_current_stage")
    current_team_id = fields.Many2one('helpdesk.team','Team',compute="compute_current_team")
    tat_status = fields.Selection(
        selection=[('new', 'New'), ('pass', 'Pass'), ('fail', 'Fail')],
        string='SLA Status:',
        compute="_compute_ticket_tat_status",
        default='new',
    )

    status = fields.Selection(
        selection=[('new', 'New'), ('pass', 'Pass'), ('fail', 'Fail')],
        string='S status:',
        compute="_compute_ticket_tat_status",
        store=True,
        default='new',
    )

    @api.model
    def set_create_date_for_old_ticket(self):
        self._cr.execute("""INSERT INTO tat_sla (ticket_id, date_in, stage_id)
                    SELECT p.id, p.create_date,r.id FROM helpdesk_ticket p
                    left join helpdesk_stage r on (r.id=p.stage_id)
                    WHERE r.is_close != True""")

    @api.model
    def create(self, values):
        line = super(HelpdeskTATandSLA, self).create(values)
        tat_val = self.env['tat.config'].search([('team_id', '=', line.team_id.id)], limit=1).id
        tat_vall = self.env['tat.config'].search([('team_id', '=', line.current_team_id.id)], limit=1).id
        tat_id = tat_val
        if not tat_id:
            tat_id = tat_vall

        line.tat_ids.create({'ticket_id': line.id,
                            #    'stage_id': line.stage_id.id,
                               'from_stage_id':line.stage_id.id,
                               'to_stage_id':line.stage_id.id,
                            #    'team_id':line.team_id.id,
                               'from_team_id': line.team_id.id,
                                'to_team_id': line.team_id.id,
                               'date_in': fields.datetime.today(),
                                   'tat_id': tat_id

                                   # 'date_out': fields.datetime.today().replace(day=23,hour=10,minute=59)

                                   })
        return line
    @api.multi
    def compute_current_stage(self):
        for rec in self:
            c_stage = self.env['tat.sla'].search([('ticket_id','=',rec.id)],order="id desc",limit=1)
            for record in c_stage:
                if not rec.current_stage_id.id:
                    rec.current_stage_id = rec.stage_id
                rec.current_stage_id = record.to_stage_id
    @api.multi
    def compute_current_team(self):
        for rec in self:
            c_team = self.env['tat.sla'].search([('ticket_id','=',rec.id)],order="id desc",limit=1)
            for record in c_team:
                if not rec.current_team_id.id:
                    rec.current_team_id = rec.team_id
                rec.current_team_id = record.to_team_id   

    @api.multi
    def write(self, vals):
        res = super(HelpdeskTATandSLA, self).write(vals)
        if 'active' in vals:
            stage_name = self.env['helpdesk.stage'].sudo().search([('name', '=', 'CANCELLED')], limit=1)
            for rec in self.tat_ids:
                if vals['active'] == False:
                    rec.is_active = False
                    self.write({'stage_id': stage_name.id})
        for rec_age in self:
            if 'stage_id' in vals and vals['stage_id']:
                closing_value = self.env['helpdesk.stage'].sudo().browse(vals['stage_id'])
                for rec in rec_age.tat_ids:
                    if not rec.date_out:
                        rec.date_out = fields.datetime.today()
                        rec.action_stop_time()
                if closing_value.is_close != True :
                    tat_val = self.env['tat.config'].search([('team_id', '=', rec_age.team_id.id)], limit=1).id
                    tat_vall = self.env['tat.config'].search([('team_id', '=', rec_age.current_team_id.id)], limit=1).id
                    tat_id = tat_val
                    if not tat_id:
                        tat_id = tat_vall
                    rec_age.tat_ids.create({'ticket_id': rec_age.id,
                                                'from_stage_id':rec_age.current_stage_id.id,
                                               'to_stage_id':rec_age.stage_id.id,
                                               'from_team_id': rec_age.current_team_id.id,
                                               'to_team_id': rec_age.team_id.id,
                                               'date_in': fields.datetime.today(),
                                                  'tat_id': tat_id
                                                         ,})
        return res


    @api.multi
    @api.depends('tat_ids.tat_status')
    def _compute_ticket_tat_status(self):
        for rec in self:
            if all(i.tat_status == 'pass' for i in rec.tat_ids):
                rec.tat_status = 'pass'
            else:
                rec.tat_status = 'fail'
            rec.status = rec.tat_status


    # @api.multi
    # @api.depends('tat_ids.tat_status')
    # def _compute_ticket_tat_status(self):
    #     for rec in self:
    #         status = 'new'
    #         if rec.tat_ids:
    #             isStatusCheck = True
    #             for i in rec.tat_ids:
    #                 if i.tat_status != 'pass':
    #                     isStatusCheck = False
    #             if isStatusCheck:
    #                 status = 'pass'
    #             else:
    #                 status = 'fail'
    #         else:
    #             status = 'new'
    #         rec.tat_status = status
    #
    #         rec.status = status
    #         print('rec.tata>', rec.tat_status)
    #         print('rec.ss>', rec.status)

    def change_ticket_status(self):
        for rec in self:
            rec.tat_ids._compute_tat_status()
            rec._compute_ticket_tat_status()



class TimerTrackingUser(models.Model):
    _inherit = 'time.tracking.users'

    helpdesk_timer_id = fields.Many2one(
        'helpdesk.ticket',
    )



class helpdesk_stage_inherit(models.Model):
    _inherit = 'helpdesk.stage'

    tat_id = fields.Many2one('tat.config','TAT')

class HelpdeskSlaCustomInherited(models.Model):
    _inherit = 'helpdesk.sla'

    tat_id = fields.Many2one('tat.config')


