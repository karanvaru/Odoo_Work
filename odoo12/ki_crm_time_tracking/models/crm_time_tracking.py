# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    user_time_tracking_ids = fields.One2many(
        'time.tracking.users',
        'crm_id',
        string='User Time Tracking'
    )
    active_user_count = fields.Integer(
        compute="_compute_active_user_count",
        string="Active Users",
        store=True
    )

    @api.depends(
        'user_time_tracking_ids',
        'user_time_tracking_ids.start_datetime',
        'user_time_tracking_ids.stop_datetime'
    )
    def _compute_active_user_count(self):
        for record in self:
            record.active_user_count = len(
                record.user_time_tracking_ids.filtered(
                    lambda i: i.start_datetime and not i.stop_datetime
                )
            )

    def action_start(self):
        user = self.env.user
        for rec in self:
            name = rec.display_name

            if 'x_studio_lead_number' in self._fields:
                if rec.x_studio_lead_number:
                    name = rec.x_studio_lead_number + ' : ' + rec.display_name

            self.env['time.tracking.users']._action_start(
                active_id=rec.id,
                foreign_key='crm_id',
                name=name
            )

class TimerTrackingUser(models.Model):
    _inherit = 'time.tracking.users'

    crm_id = fields.Many2one(
        'crm.lead',
        string='CRM',
    )
