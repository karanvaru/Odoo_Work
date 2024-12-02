from odoo import models, fields
from datetime import date, datetime, timedelta
import time

class DxWizard(models.TransientModel):
    _name = 'wizard.dx'
    _description = 'Create Application Wizard'


    status = fields.Selection([
        ('draft', 'DRAFT'),
        ('front_desk', 'FRONT DESK'),
        ('assigned', 'ASSIGNED'),
        ('wip', 'WIP'),
        ('testing', 'TESTING'),
        ('submit_to_admin', 'Submit To Admin'),
        ('live', 'LIVE'),
        ('documentation', 'Documentation'),
        ('hold', 'Hold'),
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED')
    ], string='Status')
    reason = fields.Text(string='Reason', required=True)
    created_by = fields.Char('Created By', default=lambda self: self.env.user.name, readonly="1")
    created_date = fields.Datetime(string='Created Date', default=datetime.today())

    def button_cancel(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        self.status = 'cancel'
        active_record.update({

            'state': self.status,
            'dx_cancel_ids': [
                (0, 0, {'created_by': self.created_by, 'created_date': self.created_date, 'reason': self.reason})]
        })

