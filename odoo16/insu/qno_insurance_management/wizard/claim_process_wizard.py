from odoo import models, fields, api


class ClaimProcessWizard(models.TransientModel):
    _name = "claim.process.wizard"

    process_date = fields.Date(
        string='Process Date',
        default=fields.Date.context_today,
        required=True
    )

    claim_amount = fields.Float(
        string='Claim Amount',
    )

    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        claim = self.env[active_model].browse(active_id)
        claim.update({
            'date_claimed': self.process_date,
            'claimed_amount': self.claim_amount,
            'state': 'in_process'
        })
