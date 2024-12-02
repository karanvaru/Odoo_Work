from odoo import models, fields, api


class CfoApprovalWizard(models.TransientModel):
    _name = 'cfo.approval.wizard'
    _description = 'Model for Cfo Approval Wizard'


    reason = fields.Text(string="Reason")

    def approve_request(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({'cfo_approval_reason': self.reason})
        active_record.cfo_approval_loan()


    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
