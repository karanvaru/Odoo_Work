# -*- coding: utf-8 -*-

from datetime import *
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class BaseTimeTracking(models.Model):
    _name = 'time.tracking.users'
    _description = "Time Tracking for Users"

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
    )
    start_datetime = fields.Datetime(
        string='Start Time',
        required=True,
    )
    pause_datetime = fields.Datetime(
        string='Pause Time',
    )
    resume_datetime = fields.Datetime(
        string='Resume Time',
    )
    stop_datetime = fields.Datetime(
        string='Stop Time',
    )
    description = fields.Text(
        string='Description',
    )
    duration = fields.Float(
        string='Duration',
        compute="_compute_duration",
        store=True
    )
    state = fields.Selection(
        [
            ('start', 'Start'),
            ('stop', 'Stop'),
            ('pause', 'Pause'),
            ('resume', 'Resume'),
        ],
        string="Status"
    )
    name = fields.Char(
        string="Name"
    )
    start_date = fields.Date(
        string="Start Date",
        compute="_compute_start_date",
        store=True
    )
    
    @api.depends('start_datetime')
    def _compute_start_date(self):
        for record in self:
            if record.start_datetime:
                record.start_date = record.start_datetime.date()

    @api.depends('start_datetime', 'stop_datetime')
    def _compute_duration(self):
        for record in self:
            if record.start_datetime and record.stop_datetime:
                elapsed_seconds = (
                    record.stop_datetime - record.start_datetime
                ).total_seconds()
                seconds_in_day =  60
                record.duration = elapsed_seconds / seconds_in_day

    @api.model
    def _action_start(self, active_id, foreign_key, name):
        user = self.env.user
        exist_lines = self.search([
#             (foreign_key , '=', active_id),
            ('start_datetime' , '!=', False),
            ('stop_datetime' , '=', False),
            ('user_id' , '=', user.id)
        ], limit=1)
        if exist_lines:
            raise ValidationError(
                _('Timer Already Started in: %s!' %(exist_lines.name))
            )
        vals = {
            'user_id': user.id,
            foreign_key: active_id,
            'start_datetime': fields.Datetime.now(),
            'state' : 'start',
            'name': name,
        }
        self.create(vals)

    def action_stop(self):
        user = self.env.user
        if (user != self.user_id) and not user._is_admin():
            raise ValidationError(
                _('You can not do other users operations!')
            )
        act = self.env.ref(
            'ki_base_time_tracking.action_time_tracking_reason'
        ).sudo().read([])[0]
        return act

    def action_pause(self):
        for record in self:
            record.update({
                'state': 'pause',
                'pause_datetime': fields.Datetime.now()
            })

    def action_resume(self):
        for record in self:
            record.update({
                'state': 'resume',
                'resume_datetime': fields.Datetime.now()
            })
