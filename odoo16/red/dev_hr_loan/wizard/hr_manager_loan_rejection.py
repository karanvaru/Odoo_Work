from odoo import models, fields, api


class HrManagerRejectionWizard(models.TransientModel):
    _name = 'hr.manager.reject.wizard'
    _description = 'Model for Hr Manager Reject Wizard'


    reason = fields.Text(string="Reason")

    def reject_request(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({'hr_reject_reason': self.reason})
        active_record.hr_manager_reject_loan()


    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
