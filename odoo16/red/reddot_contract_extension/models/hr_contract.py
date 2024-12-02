from odoo import api, fields, models, _
import re
import base64
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    new_contract_id = fields.Many2one(
        'hr.contract',
        string="New Contract",
    )

    state = fields.Selection(
        selection_add=[("sent", "Sent"), ("accepted", "Accepted"), ("exception", "Exception")],
        ondelete={'sent': 'cascade', 'accepted': 'cascade', 'exception': 'cascade'}
    )
    is_renew_button_invisible = fields.Boolean(
        compute="_compute_is_renew_button_invisible",
    )
    report_template_id = fields.Many2one(
        'contract.report.template',
        string="Report Template",
        domain="[('company_id', '=', company_id)]"
    )
    exception_remark = fields.Text(
        'Exception Remarks'
    )
    sequence = fields.Char(
        'sequence',
        default='New',
        copy=False,
        readonly=True
    )
    employee_signature = fields.Char(
        'Employee Signature',
    )
    close_contract_comment = fields.Text(
        'Close Contract Comment',
    )

    report_description = fields.Html(
        string="Description",
    )
    is_renealble = fields.Boolean(
        string="Is Renealble?"
    )
    renewal_status = fields.Selection([
        ('to_renew', 'To Renew'),
        ('to_approve', 'To Approve'),
        ('do_not_renew', 'Do Not Renew'),
        ('approved', 'Approved'),

    ], string='Renewal Status'
    )
    basic_salary_amount = fields.Monetary(
        string='Basic Salary',
        tracking=True,
    )
    transportation_alw_amount = fields.Monetary(
        string='Transport Allowance',
        tracking=True,
    )
    housing_alw_amount = fields.Monetary(
        string='Housing Allowance',
        tracking=True,
    )
    other_alw_amount = fields.Monetary(
        string='Other Allowance',
        tracking=True,
    )
    meal_alw_amount = fields.Monetary(
        string='Meal Allowance',
        tracking=True,
    )
    is_probation = fields.Boolean(
        string="Is Probation?",
    )

    @api.depends('date_end')
    def _compute_is_renew_button_invisible(self):
        for record in self:
            if record.date_end:
                month_date = record.date_end + relativedelta(months=1)
                if date.today() > month_date:
                    record.is_renew_button_invisible = True
                else:
                    record.is_renew_button_invisible = False
            else:
                record.is_renew_button_invisible = False

    @api.onchange('report_template_id')
    def onchange_report_template_id(self):
        for rec in self:
            if rec.report_template_id:
                rec.compute_description()

    def process_tag(self, message, condition, tag):
        if condition:
            return message.replace(f"&lt;{tag}&gt;", "").replace(f"&lt;/{tag}&gt;", "")
        else:
            pattern = re.compile(rf"&lt;{tag}&gt;.*?&lt;/{tag}&gt;", re.DOTALL)
            return re.sub(pattern, '', message)

    def compute_description(self):
        if self.report_template_id:
            message = re.sub(
                r'\{(\w+(\.\w+)*)\}',
                lambda match: self._get_dynamic_value(match.group(1)),
                self.report_template_id.description
            )

            message = self.process_tag(message, self.is_probation, "probation")
            message = self.process_tag(message, self.employee_id.gender == "male", "male")
            message = self.process_tag(message, self.employee_id.gender == "female", "female")

            self.report_description = message

    def _get_dynamic_value(self, placeholder):
        try:
            parts = placeholder.split('.')
            value = self
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    return f"[Missing: {placeholder}]"
                if type(value).__name__ == 'datetime':
                    value = value.strftime("%d %B %Y")
                elif type(value).__name__ == 'date':
                    value = value.strftime("%d %B %Y")
                elif type(value).__name__ == 'float':
                    value = '{:,.2f}'.format(value)
            return str('' if value == False else value)
        except Exception as e:
            return f"[Invalid: {placeholder}]"

    # @api.model
    # def create(self, vals):
    #     vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.contact.custom')
    #     return super(ContractInherit, self).create(vals)

    @api.model
    def create(self, vals):
        res = super(ContractInherit, self).create(vals)
        if res.date_end:
            current_year = res.date_end.year
            company = res.employee_id.address_id
            country_code = company.country_id.code
            if country_code:
                sequence = self.env['ir.sequence'].next_by_code('contract.dynamic.sequence')
                res.update({
                    'sequence': f"RDD/{country_code}/CONTRACT/{current_year}/{sequence}"
                })
        #         else:
        #             raise ValidationError(_('Please enter valid date!'))
        return res

    def send_email(self):
        email_template = self.env.ref('reddot_contract_extension.mail_template_contract_send')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        pdf_content = self.env['ir.actions.report']._render_qweb_pdf(
            'reddot_contract_extension.action_print_contract_report', self.id)
        pdf_attachment = base64.b64encode(pdf_content[0])

        attachment = self.env['ir.attachment'].create({
            'name': f'Contract For {self.employee_id.name}.pdf',
            'type': 'binary',
            'datas': pdf_attachment,
            'res_model': 'hr.contract',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        ctx = {
            'default_model': 'hr.contract',
            'default_res_id': self.ids[0],
            'default_use_template': bool(email_template),
            'default_template_id': email_template.id if email_template else None,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'force_email': True,
            'default_attachment_ids': [attachment.id]
        }
        self.update({
            'state': 'sent'
        })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def reset_to_draft(self):
        self.update({
            'state': 'draft'
        })

    def action_approve(self):
        template_id = self.env.ref(
            'reddot_contract_extension.contract_reminder_for_renew_to_approve')
        #         if template_id:
        #             template_id.send_mail(self.id, force_send=True)
        self.update({
            'renewal_status': 'to_approve'
        })

    def contract_expire_in_60_days(self):
        return True
        today = date.today()
        before_60_days = today + relativedelta(months=2)
        conf_contract = self.search(
            [('date_end', '>=', today), ('date_end', '<=', before_60_days), ('state', '=', 'open')])
        if conf_contract:
            for rec in conf_contract:
                if rec.employee_id.parent_id:
                    rec.is_renealble = True
                    rec.renewal_status = 'to_renew'
                    template_id = self.env.ref(
                        'reddot_contract_extension.contract_reminder_before_60_daya_email_template')
                    if template_id:
                        template_id.send_mail(rec.id, force_send=True)

    def contract_state_running(self):
        today = date.today()
        draft_contract = self.search([('date_start', '<=', today), ('state', '=', 'draft')])
        for rec in draft_contract:
            rec.update({
                'state': 'open'
            })
