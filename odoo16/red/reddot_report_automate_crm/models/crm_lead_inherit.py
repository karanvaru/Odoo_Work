from odoo import api, fields, models, _
from datetime import date, datetime


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    def action_send_lead_mail(self, id):
        mail_template = id.env.ref('reddot_report_automate_crm.lead_email_template')
        email_to = ','.join([id.user_id.email, id.user_id.employee_id.parent_id.work_email or ''])
        mail_template.email_to = email_to
        mail_template.send_mail(id.id)

    @api.model
    def create(self, vals):
        id = super(CrmLeadInherit, self).create(vals)
        self.action_send_lead_mail(id)
        return id

    def write(self, vals):
        res = super(CrmLeadInherit, self).write(vals)

        if vals.get('user_id'):
            self.action_send_lead_mail(self)
        return res

    def action_send_lead_not_complete_mail(self):
        today = date.today()
        lead = self.sudo().search([('date_deadline', '<=', today), ('won_status', '=', 'pending')])
        for rec in lead:
            mail_template = rec.env.ref('reddot_report_automate_crm.lead_close_date_email_template')
            mail_template.send_mail(rec.id)

    def action_send_lead_status_mail(self):
        # print("___________________________")
        lead_status_dct = {}
        lead = self.sudo().search([])
        mail_template = self.env.ref('reddot_report_automate_crm.lead_status_email_template')

        for rec in lead:
            # print("_____________________recccc",rec)
            if rec.team_id not in lead_status_dct:
                lead_status_dct[rec.team_id] = {}
            if rec.stage_id not in lead_status_dct[rec.team_id]:
                lead_status_dct[rec.team_id][rec.stage_id] = 0
            lead_status_dct[rec.team_id][rec.stage_id] += 1

        for data in lead_status_dct:
            print("__________________ ")
            context = {
                'lead_status_dct': lead_status_dct[data],
                'lead_data': data.user_id.name or ''
            }
            print("____________________  dataa", data)
            print("____________________  1111", lead_status_dct[data])
            email_to = data.user_id.email
            mail_template.email_to = email_to

            mail_template.with_context(context).send_mail(data.id,force_send=True)

        # print("________________  lead",lead_status_dct)
