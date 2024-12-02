from odoo import models, fields
from datetime import date, datetime, timedelta
import time

class HpiCancelWizard(models.TransientModel):
    _name = 'wizard.cancel.hpi'
    _description = 'Create Application Wizard'



    status = fields.Selection([
        ('new', 'NEW'),
        ('wip', 'WIP'),
        ('improved', 'IMPROVED'),
        ('cancel', 'CANCELLED'),
        ('future', 'FUTURE'),
    ], string='Status')
    cancel_description = fields.Text(string='Description', required=True)
    hdpi_cancel_category_id = fields.Many2one('hdpi.category', string="Category")

    def button_cancel(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        self.status = 'cancel'
        active_record.update({

            'state': self.status,
            'hpi_cancel_ids': [
                (0, 0, {'cancel_description': self.cancel_description, 'hdpi_cancel_category_id': self.hdpi_cancel_category_id})]
        })

