
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class SalePolicyDetailWizard(models.TransientModel):
    _name = "sale.policy.detail.wizard"

    start_date = fields.Date(
        string='Date Started',
        default=fields.Date.context_today,
        required=True
    )
    end_date = fields.Date(
        string='Date Expire',
        readonly=False
    )
    policy_number = fields.Char(
        string="Policy Number",
        required=True,
       help="Policy number is a unique number that"
            "an insurance company uses to identify"
            "you as a policyholder"
    )
    policy_duration = fields.Integer(
        string='Duration in Days',
        required=True,
        default=365
    )

    attachment = fields.Binary(
        string="Attachment",
        required=True,
    )
    attachment_name = fields.Char(string="Name")

    @api.onchange('policy_duration', 'start_date')
    def onchange_policy_duration(self):
        self.end_date = self.start_date + relativedelta(days=self.policy_duration - 1)

    def action_confirm(self):
        if self.attachment_name:
            if str(self.attachment_name.split(".")[1]) != 'pdf':
                raise ValidationError("Cannot upload file different from .pdf file")

        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        if active_id and active_model:
            order = self.env[active_model].browse(active_id)
            vals = {
                'policy_number': self.policy_number,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'policy_duration': self.policy_duration,
                'policy_document': self.attachment,
            }
            attachment_id = self.env['ir.attachment'].sudo().create({
                'name': self.attachment_name,
                'datas': self.attachment,
                'res_model': 'insurance.policy',
                'res_name': 'Policy',
                'res_id': active_id
            })
            order.update(vals)

        return True