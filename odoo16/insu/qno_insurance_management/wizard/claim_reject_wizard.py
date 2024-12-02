from odoo import models, fields, api


class ClaimRejectWizard(models.TransientModel):
    _name = "claim.reject.wizard"

    reason = fields.Text(
        string="Reason"
    )

    def action_reject_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        reject = self.env[active_model].browse(active_id)
        reject.message_post(body=self.reason)
        reject.update({
            'state': 'rejected',
        })
