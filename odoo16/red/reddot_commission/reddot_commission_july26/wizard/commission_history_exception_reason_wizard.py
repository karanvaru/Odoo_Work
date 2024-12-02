from odoo import models, fields, api


class CommissionHistoryExceptionReasonWizard(models.TransientModel):
    _name = 'commission.history.exception.reason.wizard'
    _description = "Exception Reason Wizard"

    reason = fields.Text(
        string='Reason',
        required=True
    )

    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        commission_history = self.env[active_model].browse(active_id)
        commission_history.update({
            'exception_reason': self.reason,
            'state': 'exception',
        })
