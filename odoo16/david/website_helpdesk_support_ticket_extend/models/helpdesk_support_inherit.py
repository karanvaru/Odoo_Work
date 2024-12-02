from odoo import models, fields, api


class HelpdeskSupportInherit(models.Model):
    _inherit = "helpdesk.support"

    priority = fields.Selection(
        [('0', 'Low'),
         ('1', 'Medium'),
         ('2', 'High'),
         ('3', 'Critical')

         ],
        default='1',
        string='Priority',
    )

    category = fields.Selection(
        selection='_get_new_category',
        string='Category',
    )
    custom_signature_helpdesk_support = fields.Image(
        string="Signature",
        copy=False
    )
    custom_helpdesk_sign_by = fields.Many2one(
        'res.users',
        string="Signed by",
        copy=False
    )
    custom_helpdesk_sign_date = fields.Datetime(
        string='Signed Date',
        copy=False
    )

    @api.onchange('user_id')
    def onchange_user_id(self):
        for rec in self:
            if rec.user_id:
                if rec.user_id.department_id:
                    rec.department_id = rec.user_id.department_id



    @api.model
    def _get_new_category(self):
        selection = [
            ('technical', 'Technical Support (Hardware And/or Software)'),
            ('functional', 'Inquiries'),
        ]
        return selection

    def set_to_close(self):
        url = self.get_base_url() + "/email-verification/%s" % (self.id)
        ctx = {
            'url': url
        }
        for rec in self:
            template_id = self.env.ref(
                'website_helpdesk_support_ticket_extend.customer_send_mail_verification_template')
            template_id.with_context(ctx).send_mail(rec.id, force_send=True)

    @api.model
    def create(self, vals):
        result = super(HelpdeskSupportInherit, self).create(vals)
        if 'team_id' in vals:
            ctx = {
                'name': result.name,
                'id': result.id
            }
            result.send_mail_helpdesk(ctx)
        if 'user_id' in vals:
            if vals['user_id'] != False:
                if vals['user_id'] != 1:
                    mail = result
                    result.send_mail_helpdesk_write(mail)
        return result

    def write(self, vals):
        res = super(HelpdeskSupportInherit, self).write(vals)
        if 'team_id' in vals:
            ctx = {
                'name': self.name,
                'id': self.id
            }
            self.send_mail_helpdesk(ctx)
        if 'user_id' in vals:
            mail = self
            self.send_mail_helpdesk_write(mail)
        if 'stage_id' in vals:
            stage = self.env['helpdesk.stage.config'].search([('stage_type', '=', 'pending_review')])
            if vals['stage_id'] == stage.id:
                self.send_pending_review_stage_mail()
        return res

    def send_pending_review_stage_mail(self):
        ticket_mail_template = self.env.ref(
            'website_helpdesk_support_ticket_extend.helpdesk_pending_review_stage_mail_template')
        if ticket_mail_template:
            ticket_mail_template.sudo().send_mail(self.id)

    def send_mail_helpdesk(self, ctx):
        ticket_mail_template = self.env.ref('website_helpdesk_support_ticket_extend.helpdesk_ticket_assign_for_team')
        if ticket_mail_template:
            ticket_mail_template.sudo().with_context(ctx).send_mail(self.id)

    def send_mail_helpdesk_write(self, mail):
        # message = "I am {} and I am assigned to your case. We will do our best to resolve your Ticket ASAP.".format(
        #     mail.user_id.name)
        # mail.message_post(body=message)
        ticket_mail_template = mail.env.ref(
            'website_helpdesk_support_ticket_extend.helpdesk_ticket_assign_for_user')
        if ticket_mail_template:
            ticket_mail_template.send_mail(mail.id)

    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            order.access_url = f'/my/ticket/{order.id}'

