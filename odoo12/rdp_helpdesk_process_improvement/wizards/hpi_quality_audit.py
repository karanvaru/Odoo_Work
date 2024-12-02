from email.policy import default
from odoo import models, fields
from datetime import datetime


class CreateQualityResponse(models.TransientModel):
    _name = 'hpi.quality.response'
    _description = 'Quality Process Improvement'


    subject = fields.Char(string="Subject", track_visibility='always')
    description = fields.Text(string="Description")

    created_by = fields.Char('Created By', default=lambda self: self.env.user.name, readonly="1")
    created_date = fields.Datetime(string='Created Date', default=datetime.today())

    def action_quality_submit(self):

        hpi_id = self.env['helpdesk.process.improvement']
        active_id = self._context.get('active_id')
        qa_id = self.env['quality.audit'].browse(active_id)
        vals = {
                'created_by': self.created_by,
                'created_date': self.created_date,
                'subject': self.subject,
                'description': self.description,
                'quality_audit_ticket_id': qa_id.id,

            }
        new_quality_val = hpi_id.create(vals)

        # return new_quality_val
        text = 'Thank you for sharing the idea!! Your insights and suggestions are valuable to us and team.Your willingness to share your thoughts and ideas is greatly appreciated.'
        partial = self.env['message.wizard'].create({'text': text})
        return {'name': ("Message"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'message.wizard',
                'view_id': self.env.ref('rdp_helpdesk_process_improvement.message_wizard_pop_up_form').id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                }

