# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class TimerTrackingslaReason(models.TransientModel):
    _name = 'time.tracking.sla.wizard'
    _description = 'Time Tracking sla Wizard'

    reason = fields.Text(
        string='Reason',
        required=True,
    )

    def action_submit(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.write({
            'description': self.reason,
            'date_out': fields.Datetime.now(),
            'timer_status': 'off'
        })


