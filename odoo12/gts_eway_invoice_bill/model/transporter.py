from odoo import fields, models, api, _
from odoo.exceptions import UserError

import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    transporter = fields.Boolean("Is Transporter?", tracking=2)


# class EwayTransportation(models.Model):
#     _name = 'eway.transportation'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#
#     name = fields.Char("Transporter Name", tracking=2, required=True)
#     trans_id = fields.Char("Transporter ID", tracking=2, required=True)
#     email = fields.Char("Email ID", tracking=2, required=True)
#     mobile = fields.Char("Mobile No", tracking=2, required=True)
#     street = fields.Char("Street 1", tracking=2, required=True)
#     street2 = fields.Char("Street 2", tracking=2, required=True)
#     city = fields.Char("City", tracking=2, required=True)
#     zip = fields.Char("Zip", tracking=2, required=True)
#     country_id = fields.Many2one('res.country', "Country", tracking=2, required=True)
#     state_id = fields.Many2one('res.country.state', "State", tracking=2, required=True)
#
#     @api.constrains('mobile', 'email')
#     def validate_transport_date(self):
#         if len(self.mobile) < 10 and (self.mobile).isdigit() is False:
#             raise UserError(_('Invalid Phone Number'))
#         if self.email:
#             match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
#             if not match:
#                 raise UserError(_('Invalid Email Id !'))
#         return True
#
#     @api.onchange('state_id')
#     def _onchange_state(self):
#         if self.state_id:
#             self.country_id = self.state_id.country_id.id
