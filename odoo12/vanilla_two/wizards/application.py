from odoo import models, fields


class VanillaTwoApplication(models.TransientModel):
    _name = 'vanilla.two.application'
    _description = 'Create Vanilla Application'


    status = fields.Selection([
        ('draft', 'DRAFT'),
        ('work_in_progress', 'WIP'),
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

