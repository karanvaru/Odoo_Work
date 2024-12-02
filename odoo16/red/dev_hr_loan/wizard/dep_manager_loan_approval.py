from odoo import models, fields, api


class DepartmentManagerApprovalWizard(models.TransientModel):
    _name = 'department.manager.approval.wizard'
    _description = 'Department Manager Approval Wizard'


    reason = fields.Text(string="Reason")

    def approve_request(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({'dep_manager_approval_reason': self.reason})
        active_record.dep_manager_approval_loan()


    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}