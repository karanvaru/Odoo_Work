from odoo import models, fields, api,_
from datetime import datetime
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import *



class TATConfiguration(models.Model):
    _name = 'tat.config'
    _discription = "TAT Configuration"

    name = fields.Char('TAT Name')
    sequence_id = fields.Char('Reference',required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    model_id = fields.Many2one('ir.model','Model')
    model_name = fields.Char('Model Name')
    time_days = fields.Integer('Days', default=0, required=True, help="Days to reach given stage based on ticket creation date")
    time_minutes = fields.Integer('Minutes', default=0, required=True, help="Minutes to reach given stage based on ticket creation date")


    time_hours = fields.Integer('Hours', default=0, required=True,
                                help="Hours to reach given stage based on ticket creation date")
    # team_id = fields.Many2one('helpdesk.team',"Team")
    team_id = fields.Many2one('helpdesk.team','Team')
    stage_id = fields.Many2one('helpdesk.stage','Stage')
    resource_calendar_id = fields.Many2one('resource.calendar','Working Hours')
    # stage_ids = fields.Many2many('helpdesk.stage')

    @api.model
    def create(self, vals):
       
        vals.update({
            'sequence_id': self.env['ir.sequence'].next_by_code('tat.config.sequence'),
        })

        return super(TATConfiguration, self).create(vals)


    @api.onchange('time_hours','team_id')
    def _onchange_time_hours(self):
        if self.team_id:
            working_hours = self.team_id.resource_calendar_id.hours_per_day
            if self.time_hours >= working_hours:
                # working_hours = self.team_id.resource_calendar_id.hours_per_day
                self.time_days += self.time_hours / working_hours
                self.time_hours = self.time_hours % working_hours
        else:
            if self.time_hours >= 24:
                self.time_days += self.time_hours / 24
                self.time_hours = self.time_hours % 24

    @api.onchange('time_minutes')
    def _onchange_time_minutes(self):
        if self.time_minutes >= 60:
            self.time_hours += self.time_minutes / 60
            self.time_minutes = self.time_minutes % 60

class helpdesk_stage_inherit(models.Model):
    _inherit = 'helpdesk.stage'

    tat_id = fields.Many2one('helpdesk.ticket.tat','TAT')

class HelpdeskSlaCustomInherited(models.Model):
    _inherit = 'helpdesk.sla'

    tat_id = fields.Many2one('helpdesk.ticket.tat')