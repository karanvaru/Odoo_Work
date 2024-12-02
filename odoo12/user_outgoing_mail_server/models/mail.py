# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import osv

class Message(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _inherit = 'mail.message'

    @api.model
    def _get_default_outgoing_server(self):
        if self.env.user.use_own_mail_server:
            mail_server  = self.env['ir.mail_server'].sudo().search([('user_id','=',self.env.user.id)],limit=1)
            if mail_server.id != False:
                return mail_server
            else:
                raise osv.except_osv(('Outgoing Mail Server of this user is not set.'), ('Please contact your Administrator to set your Outgoing Mail Server into the system.'))

                UserError(_("Unable to send email, please configure the sender's outgoing mail server."))

    mail_server_id = fields.Many2one('ir.mail_server', 'Outgoing mail server',default=_get_default_outgoing_server)