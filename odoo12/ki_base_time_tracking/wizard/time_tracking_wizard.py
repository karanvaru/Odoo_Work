# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class TimerTrackingReason(models.TransientModel):
    _name = 'time.tracking.reason.wizard'
    _description = 'Time Tracking Wizard'

    reason = fields.Text(
        string='Reason',
        required=True,
    )

    def action_submit(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({
            'description': self.reason,
            'stop_datetime': fields.Datetime.now(),
            'state': 'stop'
        })
