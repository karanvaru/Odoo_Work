# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields,_
from odoo.tools.misc import clean_context

class ActivityFeedback(models.TransientModel):
    _name = 'activity.feedback'
    _description = 'Activity Feedback'

    feedback = fields.Text("Feedback",required=True)
    done_button_pressed = fields.Boolean()
    
    def action_done(self):
        message = self.env['mail.message']
        active_id = self.env.context.get('active_id')
        activity_id = self.env['mail.activity'].sudo().browse(active_id)
        activity_id.state='done'
        activity_id.active=False
        activity_id.activity_done = True
        activity_id.date_done = fields.Date.today()
        activity_id.feedback = self.feedback
        if self.feedback:
            activity_id.sudo().write(dict(feedback=self.feedback))
        for activity in activity_id:
            record = self.env[activity.res_model].sudo().browse(activity.res_id)
            record.sudo().message_post_with_view(
                'mail.message_activity_done',
                values={'activity': activity},
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.sudo().message_ids[0]
    
    def action_schedule_done(self):
        active_id = self.env.context.get('active_id')
        activity_id = self.env['mail.activity'].sudo().browse(active_id)
        activity_id.state='done'
        activity_id.active=False
        activity_id.date_done = fields.Date.today()
        activity_id.activity_done = True
        activity_id.feedback = self.feedback
        message = self.env['mail.message']
        for activity in activity_id:
            record = self.env[activity.res_model].sudo().browse(activity.res_id)
            record.sudo().message_post_with_view(
                'mail.message_activity_done',
                values={'activity': activity},
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.sudo().message_ids[0]
        ctx = dict(
            clean_context(self.env.context),
            default_previous_activity_type_id=activity_id.activity_type_id.id,
            activity_previous_deadline=activity_id.date_deadline,
            default_res_id=activity_id.res_id,
            default_res_model=activity_id.res_model,
        )
        view_id = self.env.ref('sh_activities_management.sh_mail_activity_type_view_form_inherit').id
        return {
            'name': _('Schedule an Activity'),
            'context': ctx,
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }