from odoo import models, fields, api


class CountryAccountantApprovalWizard(models.TransientModel):
    _name = 'country.accountant.approval.wizard'
    _description = 'Country Accountant Approval Wizard'


    reason = fields.Text(string="Reason")

    def approve_request(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({'ca_approval_reason': self.reason})
        active_record.country_accountant_approval_loan()


    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
