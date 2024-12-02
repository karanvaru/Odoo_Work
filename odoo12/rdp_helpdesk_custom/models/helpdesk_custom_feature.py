# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class HelpdeskCustom(models.Model):
    _inherit = "helpdesk.ticket"

    product_serial_no = fields.Many2one('stock.production.lot', string='Product Serail No')
    serial_product = fields.Many2one('product.product', string='Product', related='product_serial_no.product_id',
                                     store="True")
    pspr_count = fields.Integer('PSPR Count', compute="compute_pspr_count")
    otd_ots_priority = fields.Selection([
        ('vip_platinum', 'VIP Platinum'),
        ('gold', 'Gold'),
        ('general', 'General'),
    ], string="OTD & OTS Priority", track_visibility='onchange', compute="compute_otd_ots_priority")



    ####################cron_job######################
    # @api.model
    # def action_send_reminders(self):
    #     # psr_tickets = self.search([('stage_id.id', 'in', [161, 108])])
    #     psr_tickets = self.search([('stage_id.id', 'in', [172, 194])])
    #     # back_order_tickets = self.search([('stage_id.id', 'in', [132, 158])])
    #     back_order_tickets = self.search([('stage_id.id', 'in', [233, 234])])
    #     psr_template = self.env.ref('rdp_helpdesk_custom.psr_stage_reminder_template')
    #     back_order_template = self.env.ref('rdp_helpdesk_custom.back_order_stage_mail_template')
    #     for ticket in psr_tickets:
    #         if ticket.partner_email:
    #             try:
    #                 psr_template.send_mail(ticket.id, force_send=True)
    #                 ticket.message_post(
    #                     subtype_id=self.env.ref('mail.mt_note').id,
    #                 )
    #             except Exception as e:
    #                 _logger.error(f"Error sending email for ticket ID {ticket.id}: {e}")
    #     for ticket in back_order_tickets:
    #         if ticket.partner_email:
    #             try:
    #                 back_order_template.send_mail(ticket.id, force_send=True)
    #                 ticket.message_post(
    #                     subtype_id=self.env.ref('mail.mt_note').id,
    #                 )
    #             except Exception as e:
    #                 _logger.error(f"Error sending email for ticket ID {ticket.id}: {e}")
    @api.model
    def action_send_reminders(self):
        stage_name = self.env['helpdesk.stage'].sudo().search([('rdp_mail_notify_type', '=', 'PSR_opened_stage')])
        for rec in stage_name:
            psr_tickets = self.env['helpdesk.ticket'].search([('stage_id', '=', rec.id)])
            psr_template = self.env.ref('rdp_helpdesk_custom.psr_stage_reminder_template')

            # back_order_tickets = self.env['helpdesk.ticket'].search([('stage_id', 'in', [233, 234])])
            # customer_side_pending = self.env['helpdesk.ticket'].search([('stage_id', 'in',[239] )])
            #

            # back_order_template = self.env.ref('rdp_helpdesk_custom.back_order_stage_mail_template')
            # customer_side_pending_template = self.env.ref('rdp_helpdesk_custom.customer_side_pending_stage')

            for ticket in psr_tickets:
                if ticket.partner_email:
                    try:
                        psr_template.send_mail(ticket.id, force_send=True,
                                               email_values={'partner_ids': [(4, ticket.partner_id.id)]})
                        ticket.message_post(
                            subtype_id=self.env.ref('mail.mt_note').id,
                        )
                    except Exception as e:
                        _logger.error(f"Error sending PSR email for ticket ID {ticket.id}: {e}")
        #
        # for ticket in back_order_tickets:
        #     if ticket.partner_email:
        #         try:
        #             back_order_template.send_mail(ticket.id, force_send=True,
        #                                           email_values={'partner_ids': [(4, ticket.partner_id.id)]})
        #             ticket.message_post(
        #                 subtype_id=self.env.ref('mail.mt_note').id,
        #             )
        #         except Exception as e:
        #             _logger.error(f"Error sending Back Order email for ticket ID {ticket.id}: {e}")
        #
        # for ticket in customer_side_pending:
        #     if ticket.partner_email:
        #         try:
        #             customer_side_pending_template.send_mail(ticket.id, force_send=True,
        #                                                     email_values = {'partner_ids':[(4, ticket.partner_id.id)]} )
        #             ticket.message_post(
        #                 subtype_id=self.env.ref('mail.mt_note').id,)
        #         except Exception as e:
        #             _logger.error(f"Error sending Back Order email for ticket ID {ticket.id}: {e}")

    # for onchange
    # @api.multi
    # def write(self, vals):
    #     # psr_stage_ids = [161, 108]
    #     psr_stage_ids = [172, 194]
    #     # back_order_stage_ids = [132, 158]
    #     back_order_stage_ids = [233, 234]
    #     psr_template = self.env.ref('rdp_helpdesk_custom.psr_stage_reminder_template')
    #     back_order_template = self.env.ref('rdp_helpdesk_custom.back_order_stage_mail_template')
    #     for ticket in self:
    #         if 'stage_id' in vals and vals['stage_id'] in psr_stage_ids and ticket.partner_email:
    #             _logger.info(f"Sending PSR email for ticket {ticket.id}")
    #             psr_template.send_mail(ticket.id, force_send=True)
    #         elif 'stage_id' in vals and vals['stage_id'] in back_order_stage_ids and ticket.partner_email:
    #             _logger.info(f"Sending Back Order email for ticket {ticket.id}")
    #             back_order_template.send_mail(ticket.id, force_send=True)
    #     return super(HelpdeskCustom, self).write(vals)
    @api.multi
    def write(self, vals):
        # Retrieve email templates
        print("11111111111111111111111111  selffffff ",self.message_follower_ids)
        pspr_values = self.env['product.details'].search([('helpdesk_ticket_id', '=', self.id)])
        print("111111111111111pspr_valuespspr_values", pspr_values)
        psr_template = self.env.ref('rdp_helpdesk_custom.psr_stage_reminder_template')
        back_order_template = self.env.ref('rdp_helpdesk_custom.back_order_stage_mail_template')
        customer_side_pending_template = self.env.ref('rdp_helpdesk_custom.customer_side_pending_stage')

        for ticket in self:
            if 'stage_id' in vals and vals['stage_id'] in [172, 194] and ticket.partner_email:
                _logger.info(f"Sending PSR email for ticket {ticket.id}")
                psr_template.send_mail(ticket.id, force_send=True,
                                       email_values={'partner_ids': [(4, ticket.partner_id.id)]})
            elif 'stage_id' in vals and vals['stage_id'] in [233, 234] and ticket.partner_email:
                _logger.info(f"Sending Back Order email for ticket {ticket.id}")
                back_order_template.send_mail(ticket.id, force_send=True,
                                              email_values={'partner_ids': [(4, ticket.partner_id.id)]})

            elif 'stage_id' in vals and vals['stage_id'] == 239 and ticket.partner_email:
                _logger.info(f"Sending Customer Side Pending email for ticket {ticket.id}")
                customer_side_pending_template.send_mail(ticket.id, force_send=True,
                                                         email_values={'partner_ids': [(4, ticket.partner_id.id)]})

        # Call the original write method to update the record
        return super(HelpdeskCustom, self).write(vals)

    #####################studio_to_code#################
    brand_id = fields.Many2one('product.brand.amz.ept', string="Brand")
    problem_type = fields.Selection([
        ('DOA', 'DOA'),
        ('In-Warranty', 'In-Warranty'),
        ('Out-Of-Warranty', 'Out-Of-Warranty'),
        ('Other', 'Other'),
    ], string="Problem Type", track_visibility='onchange')
    problem_category = fields.Selection([
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Other', 'Other'),
    ], string="Problem Category", track_visibility='onchange')
    temp_asp_id = fields.Many2one('res.partner', string="Temp ASP")
    kam_id = fields.Many2one('hr.employee', string="KAM")
    sla_achieved = fields.Boolean(string="RDP SLA Achieved")
    asp_sla_achieved = fields.Boolean(string="ASP SLA Achieved")
    asp_ticket_no = fields.Char(string="ASP Ticket NO")
    onsite_assign_date = fields.Date(string="Onsite Assign Date")
    field_engineer_name = fields.Char(string="Field Engineer Name")
    field_engineer_mobile = fields.Char(string="Field Engineer Mobile")
    ######################23rd_sep##############
    is_different_location = fields.Boolean(string="Is Different Location")
    mobile_one = fields.Char(string="Mobile",
                             # compute="compute_end_customer_company"
                             )
    email_one = fields.Char(string="Email",
                            # compute="compute_end_customer_company"
                            )

    def compute_pspr_count(self):
        pspr_count_values = self.env['product.details'].search_count([('helpdesk_ticket_id', '=', self.id)])
        # pspr_values = self.env['product.details'].search([('helpdesk_ticket_id', '=', self.id)])
        # print("111111111111111pspr_valuespspr_values",pspr_values)
        # for rec in pspr_values:
        #     rec.write(
        #         {'message_follower_ids': [(6, 0, self.message_follower_ids.ids)]})
        #     # rec.update({
        #     #     'message_follower_ids' : self.message_follower_ids.ids
        #     # })
        # print("111111111111111pspr_valuespspr_value11111s",self.message_follower_ids)

        self.pspr_count = pspr_count_values

    def open_pspr_tickets(self):
        self.ensure_one()
        return {
            'name': 'PSPR Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'product.details',
            'domain': [('helpdesk_ticket_id', '=', self.id)],
            # 'context': {'default_message_follower_ids': self.message_follower_ids.ids},
        }

    def action_to_pspr_ticket(self, vals):
        pspr_helpdesk_id = self.env['product.details']
        vals = {
            'helpdesk_ticket_id': self.id,
        }
        new_val = pspr_helpdesk_id.create(vals)
        return new_val

    @api.depends('partner_id')
    def compute_otd_ots_priority(self):
        for rec in self:
            rec.otd_ots_priority = rec.partner_id.otd_ots_priority

    # @api.depends('x_studio_contact_person')
    # def compute_end_customer_company(self):
    #     for record in self:
    #         record.email_one = record.x_studio_contact_person.email
    #         record.mobile_one = record.x_studio_contact_person.mobile
