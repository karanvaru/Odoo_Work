from email.policy import default
from odoo import models, fields
from datetime import datetime


class ResetCredentials(models.TransientModel):
    _name = 'reset.credentials'
    _description = 'Reset Credentials'

    u_name = fields.Char(string="Username", track_visibility='always')
    passwd = fields.Char(string='Password', track_visibility='always')

    def action_submit(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({
            'credentials_ids': [
                (0, 0, {'user_name': self.u_name, 'password': self.passwd})]

        })

    def action_to_wizard(self):
        print('=')
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({
            'credentials_ids': [(0, 0, {'user_name': self.u_name, 'password': self.passwd})]
        })

# class UserDetails(models.TransientModel):
#     _name = 'user.details'
#     _description = 'Create Application Wizard'
#
#     status = fields.Selection([
#         ('draft', 'Draft'),
#         ('credential', 'Credentials'),
#         ('live', 'Live'),
#         ('cancel', 'Cancel'),
#         ('close', 'Close'),
#     ], string='Status')
#     reason = fields.Text(string='Congratulations')
#     user_name = fields.Char(string='User Name', trackvisibility="always")
#     password = fields.Char('Password', trackvisibility="always")
#
#
#     def button_confirmed(self):
#
#         active_id = self._context.get('active_id')
#         active_model = self._context.get('active_model')
#         active_record = self.env[active_model].browse(active_id)
#         self.status = 'credential'
#         active_record.update({
#
#             'state': self.status
#         })