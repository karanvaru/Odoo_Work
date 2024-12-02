from odoo import models, fields


class CreateApplication(models.TransientModel):
    _name = 'create.application'
    _description = 'Create Application Wizard'

    reason = fields.Text(string="Reason")
    status = fields.Selection([
        ('draft', 'DRAFT'),
        ('work_in_progress', 'WIP'),
        ('closed', 'Closed'),
        ('cancel', 'CANCELLED'),
    ], string='Status')

    def action_submit(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        self.status = 'cancel'
        active_record.update({
            'description': self.reason,
            'state':self.status
        })
        # self.env['template.three'].



