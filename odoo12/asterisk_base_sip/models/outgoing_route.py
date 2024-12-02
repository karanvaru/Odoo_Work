#-*- encoding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from odoo.addons.asterisk_base.utils import remove_empty_lines

logger = logging.getLogger(__name__)


class OutgoingRouteGroup(models.Model):
    _name = 'asterisk_base_sip.outgoing_route_group'
    _description = 'Outgoing Route Group'

    name = fields.Char(required=True)
