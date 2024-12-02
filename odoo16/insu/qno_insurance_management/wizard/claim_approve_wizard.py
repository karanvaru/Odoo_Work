from odoo import models, fields, api


class ClaimApproveWizard(models.TransientModel):
    _name = "claim.approve.wizard"

    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True
    )

    approve_amount = fields.Float(
        string='Approve Amount',
    )

    def action_approve(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        approve = self.env[active_model].browse(active_id)
        approve.update({
            'claimed_passed_date': self.date,
            'passed_amount': self.approve_amount,
            'state': 'approved'
        })
