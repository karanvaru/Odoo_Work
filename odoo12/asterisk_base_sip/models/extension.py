import logging
from odoo import models, fields, api, _

logger = logging.getLogger(__name__)


class SipExtension(models.Model):
    _inherit = 'asterisk_base.extension'

    sip_user_dial_timeout = fields.Integer(string='Dial Timeout', default=30)

    def open_extension(self):
        self.ensure_one()
        if self.app_model == 'asterisk_base_sip.peer':
            view = self.env.ref(
                'asterisk_base_sip.asterisk_base_sip_peer_user_form')
            return super(SipExtension, self).open_extension(view_id=view.id)
        else:
            return super(SipExtension, self).open_extension()
