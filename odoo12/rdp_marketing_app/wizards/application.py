from odoo import models, fields


class WizardApplication(models.TransientModel):
    _name = 'wizard.application'
    _description = 'Create Application Wizard'


    status = fields.Selection([
        ('draft', 'DRAFT'),
        ('work_in_progress', 'WIP'),
        ('live', 'LIVE'),
        ('hold', 'HOLD'),
        ('closed', 'Closed'),
        ('cancel', 'CANCELLED'),
    ], string='Status')
    reason = fields.Text(string='Congratulations')


    def button_confirmed(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        self.status = 'closed'
        active_record.update({

            'state': self.status
        })

