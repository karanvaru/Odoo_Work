from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DescriptionCallCloseWizard(models.TransientModel):
    _name = 'helpdesk.ticket.close.description.wizard'
    _description = 'Call Close Comment'

    comment = fields.Text(
        string='Comment',
        required=True,
    )

    def action_comment(self):
        ticket_active_id = self._context.get('active_id')
        id_brows = self.env['helpdesk.ticket'].browse(ticket_active_id)
        id_brows.message_post(body=self.comment)
        stage = self.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'Call Close')])
        id_brows.update({
            'stage_id': stage
        })
