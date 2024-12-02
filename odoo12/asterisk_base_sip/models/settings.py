import logging
from odoo import fields, models, api, _
from odoo.tools import ormcache
from odoo.addons.asterisk_base_sip.models.peer import CHANNEL_TYPES

logger = logging.getLogger(__name__)


class SipSettings(models.Model):
    _inherit = 'asterisk_common.settings'

    default_sip_channel_type = fields.Selection(
        CHANNEL_TYPES, default='sip', required=True,
        string='Default Channel Type')
