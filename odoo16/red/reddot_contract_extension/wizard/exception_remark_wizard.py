from odoo import models, fields, api


class ExceptionRemarkWizard(models.TransientModel):
    _name = 'exception.remark.wizard'
    _description = "Exception Remark Wizard"

    exception_remark = fields.Text(
        'Exception Remarks',
        required=True
    )

    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        current_contact = self.env[active_model].browse(active_id)
        if current_contact:
            current_contact.update({
                'exception_remark': self.exception_remark,
                'state': 'exception'
            })
