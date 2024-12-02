from odoo import models, fields, api


class AcceptContractWizard(models.TransientModel):
    _name = 'accept.contract.wizard'
    _description = "Accept Contract Wizard"

    employee_signature = fields.Char(
        'Employee Signature',
        required=True
    )

    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        current_contact = self.env[active_model].browse(active_id)
        if current_contact:
            current_contact.update({
                'employee_signature': self.employee_signature,
                'state': 'accepted'
            })
