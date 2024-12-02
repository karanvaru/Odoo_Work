from odoo import models, fields, api


class CfoApprovalWizard(models.TransientModel):
    _name = 'super.approver.approval.wizard'
    _description = 'Model for Super Approver Approval Wizard'


    reason = fields.Text(string="Reason")

    def approve_request(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({'super_approver_approval_reason': self.reason})
        active_record.super_approver_approval_loan()

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
