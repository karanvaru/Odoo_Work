from odoo import models, fields


class UserDetails(models.TransientModel):
    _name = 'user.details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Create Application Wizard'

    status = fields.Selection([
        ('draft', 'Draft'),
        ('credentials', 'Credentials'),
        ('live', 'Live'),
        ('cancel', 'Cancel'),
        ('close', 'Close'),
    ], string='Status')
    reason = fields.Text(string='Congratulations')
    user_name = fields.Char(string='User Name', required=True, track_visibility='always')
    password = fields.Char('Password', required=True, track_visibility='always')

    def button_confirmed(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        self.status = 'credentials'
        active_record.update({

            'state': self.status,
            'credentials_ids': [
                    (0, 0, {'user_name': self.user_name, 'password': self.password})]
        })
