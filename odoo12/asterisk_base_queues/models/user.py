import logging
from odoo import models, fields, api, tools, _

logger = logging.getLogger(__name__)


class AsteriskUser(models.Model):
    _inherit = 'asterisk_common.user'

    queue_interface = fields.Char()
