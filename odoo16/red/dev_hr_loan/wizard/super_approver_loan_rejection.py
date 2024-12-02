from odoo import models, fields, api


class CfoRejectionWizard(models.TransientModel):
    _name = 'super.approver.reject.wizard'
    _description = 'Model for Super Approver Reject Wizard'


    reason = fields.Text(string="Reason")

    def reject_request(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({'super_approver_reject_reason': self.reason})
        active_record.super_approver_reject_loan()


    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
