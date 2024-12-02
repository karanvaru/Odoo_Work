# -*- coding: utf-8 -*-
import datetime
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.addons.helpdesk.models.helpdesk_ticket import TICKET_PRIORITY
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError

class HelpdeskSlaCustom(models.Model):
    _inherit = 'helpdesk.sla'

    time_minutes = fields.Integer('Minutes', default=0, required=True, help="Minutes to reach given stage based on ticket creation date")

    time_hours = fields.Integer('Hours', default=0, required=True,
                                help="Hours to reach given stage based on ticket creation date")

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


