from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssignUser(models.TransientModel):
    _name = 'helpdesk.ticket.assign.user.wizard'
    _description = 'Assign Engineer'

    @api.model
    def _get_service_engineer_domain(self):
        res = self.env['res.users'].search([])
        lis = []
        for re in res:
            if re.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                lis.append(re.id)
        return [('id', 'in', lis)]

    wizard_user_id = fields.Many2one(
        'res.users',
        string='Assign User',
        required=True,
        store=True,
        domain=_get_service_engineer_domain
    )

    def action_assign(self):
        ticket_active_id = self._context.get('active_id')
        id_brows = self.env['helpdesk.ticket'].browse(ticket_active_id)
        id_brows.user_id = self.wizard_user_id.id
        stage = self.env['helpdesk.ticket.stage'].sudo().search([('name', '=', 'Assign')])
        id_brows.update({
            'stage_id': stage
        })

        try:
            device_ids = self.wizard_user_id.mobi_device_ids.mapped('device_id')

            #device_id = "e5_MekscSlmz4LGkjVCW_Q:APA91bGJAEUR4BxiOQFzoQSws89O5ap9trcKQ8u91i8uDru01iC8BeDg2S-K89ffCEU9yYCMJwrZVn1a8pQ7pwTxWcwdLtgGk0izIOHmK-fvrwT7EeoWCnXWgsD54Tj2HnnSwLnhcx46"
            if device_ids:
                active_fb = self.env['ki.firebase.notification'].search([('state', '=', 'active')], limit=1)
                for device_id in device_ids:
                    notif_status = active_fb.send_push_notification(
                        mobile_device_id=str(device_id),
                        body='Assigned New Ticket: %s' % (id_brows.name),
                        title='Hey! You have new Assignment',
                        order_id = str(id_brows.id)
                    )
            else:
                notif_status = "No Device Id Found"
        except:
            pass