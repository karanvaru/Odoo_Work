from odoo import models, fields
from datetime import date, datetime, timedelta
import time

class HpiFutureWizard(models.TransientModel):
    _name = 'wizard.future.hpi'
    _description = 'Create Application Wizard'



    status = fields.Selection([
        ('new', 'NEW'),
        ('wip', 'WIP'),
        ('improved', 'IMPROVED'),
        ('cancel', 'CANCELLED'),
        ('future', 'FUTURE'),
    ], string='Status')
    future_description = fields.Text(string='Description', required=True)
    hdpi_future_category_id = fields.Many2one('hdpi.category', string="Category")

    def button_future(self):

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        self.status = 'future'
        active_record.update({

            'state': self.status,
            'hpi_future_ids': [
                (0, 0, {'future_description': self.future_description, 'hdpi_future_category_id': self.hdpi_future_category_id})]
        })

