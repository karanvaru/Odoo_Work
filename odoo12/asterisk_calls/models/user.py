import logging
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
import uuid

logger = logging.getLogger(__name__)


# For upgrade puprose. Remove later.
class OldAsteriskUser(models.Model):
    _name = 'asterisk_calls.user'


class AsteriskUser(models.Model):
    _inherit = 'asterisk_common.user'

    missed_calls_notify = fields.Boolean(
        help=_('Notify user on missed calls.'))
    open_partner_form = fields.Boolean(default=True,
        help=_('Open partner form on incoming calls from partner'))
    call_popup_is_enabled = fields.Boolean(
        string=_('Call Popup'), default=True)
    call_popup_is_sticky = fields.Boolean(string=_('Sticky Messages'))
    calls_count = fields.Integer(compute='_get_calls_count', string="Calls")

    @api.model
    @tools.ormcache('exten', 'system_name')
    def get_res_user_id_by_exten(self, exten, system_name):
        astuser = self.search([
            ('exten', '=', exten), ('system_name', '=', system_name)], limit=1)
        logger.debug('GET RES USER BY EXTEN %s at %s: %s',
                     exten, system_name, astuser)
        return astuser.user.id

    @api.model
    @tools.ormcache('channel', 'system_name')
    def get_res_user_id_by_channel(self, channel, system_name):
        user_channel = self.env['asterisk_common.user_channel'].search([
            ('channel', '=', channel),
            ('system_name', '=', system_name)], limit=1)
        logger.debug('GET RES USER BY CHANNEL %s at %s: %s',
                     channel, system_name, user_channel.asterisk_user)
        return user_channel.asterisk_user.user.id

    def _get_calls_count(self):
        for rec in self:
            rec.calls_count = self.env['asterisk_calls.call'].search_count(
                ['|', ('dst_user', '=', rec.id), ('src_user', '=', rec.id)])
