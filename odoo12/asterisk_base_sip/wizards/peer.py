import json
import logging
from odoo import models, fields


logger = logging.getLogger(__name__)


class PeerOptionWizard(models.TransientModel):
    _name = 'asterisk_base_sip.peer_option_wizard'
    _description = 'Set Option'

    option = fields.Char(required=True)
    value = fields.Char()

    def do_change(self):
        peers = self.env['asterisk_base_sip.peer'].browse(
            self._context.get('active_ids', []))
        value = self.value
        if value and value[0] == '[' and value[-1:] == ']':
            # Many2many field update
            value = json.loads(value.lower())
        peers.write({self.option: value})
        return {}
