# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class ResUsers(models.Model):
    """Represents an SMTP server, able to send outgoing emails, with SSL and TLS capabilities."""
    _inherit = "res.users"
    
    use_own_mail_server = fields.Boolean('Use Own Mail Server')
    