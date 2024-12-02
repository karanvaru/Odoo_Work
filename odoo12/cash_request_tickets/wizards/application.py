from odoo import models, fields


class CashRequestTicketsApplication(models.TransientModel):
    _name = 'cash.request.tickets.application'
    _description = 'Create Cash Request Application'


    status = fields.Selection([
        ('draft', 'DRAFT'),
        ('Paid', 'PAID'),
        ('bill submit', 'BILL SUBMIT'),
        ('close', 'CLOSE'),
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

