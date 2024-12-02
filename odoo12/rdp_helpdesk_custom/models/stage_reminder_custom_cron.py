from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicketCustom(models.Model):
    _inherit = "helpdesk.ticket"

    # def action_psr_stage_reminders(self):
    #     stage_name = self.env['helpdesk.stage'].sudo().search([('name', '=', 'PSR opened stage')])
    #     psr_tickets = self.env['helpdesk.ticket'].search([('stage_id', '=', stage_name.id)])
    #     psr_template = self.env.ref('rdp_helpdesk_custom.psr_stage_reminder_custom_template')
    #     for rec in psr_tickets:
    #         psr_template.send_mail(rec.id)

    def action_back_order_stage_reminders(self):
        stage_name = self.env['helpdesk.stage'].sudo().search([('rdp_mail_notify_type', '=', 'back_order_stage')])
        for rec in stage_name:
            back_order_tickets = self.env['helpdesk.ticket'].search([('stage_id', '=', rec.id)])
            back_order_template = self.env.ref('rdp_helpdesk_custom.back_order_stage_mail_template')

            for ticket in back_order_tickets:
                if ticket.partner_email:
                    try:
                        back_order_template.send_mail(ticket.id, force_send=True,
                                                      email_values={'partner_ids': [(4, ticket.partner_id.id)]})
                        ticket.message_post(
                            subtype_id=self.env.ref('mail.mt_note').id,
                        )
                    except Exception as e:
                        _logger.error(f"Error sending Back Order email for ticket ID {ticket.id}: {e}")

    def action_customer_side_pending_stage_reminders(self):
        stage_name = self.env['helpdesk.stage'].sudo().search([('rdp_mail_notify_type', '=', 'customer_side_pending_stage')])
        for rec in stage_name:
            customer_side_pending = self.env['helpdesk.ticket'].search([('stage_id', '=', rec.id)])
            customer_side_pending_template = self.env.ref('rdp_helpdesk_custom.customer_side_pending_stage')

            for ticket in customer_side_pending:
                if ticket.partner_email:
                    try:
                        customer_side_pending_template.send_mail(ticket.id, force_send=True,
                                                                 email_values={'partner_ids': [(4, ticket.partner_id.id)]})
                        ticket.message_post(
                            subtype_id=self.env.ref('mail.mt_note').id, )
                    except Exception as e:
                        _logger.error(f"Error sending Back Order email for ticket ID {ticket.id}: {e}")
