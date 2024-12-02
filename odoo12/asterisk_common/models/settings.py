import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import ormcache

logger = logging.getLogger(__name__)

ORIGINATE_FORMAT_TYPES = [
    ('e164', _('E.164 Format')),
    ('out_of_country', _('Out of Country Format')),
    ('no_format', _('No Formatting')),
]


class AsteriskSettings(models.Model):
    _name = 'asterisk_common.settings'
    _description = 'Asterisk Settings'

    name = fields.Char(compute='_get_name')
    originate_strip_plus = fields.Boolean(default=True)
    originate_timeout = fields.Integer(default=60, required=True)
    originate_format = fields.Selection(
        ORIGINATE_FORMAT_TYPES, default='e164', required=True,
        help='Select how to format partner numbers on originate.')
    originate_prefix = fields.Char(help='Add prefix to numbers on originate.')
    originate_context = fields.Char(
        default='from-internal', required=True,
        help='Default context to set when creating user mapping.')
    originate_partner_callerid = fields.Boolean(
        default=True,
        help="Set partner's caller ID on originate leg (click2dial).")
    permit_ip_addresses = fields.Char(
        string=_('Permit IP address(es)'),
        help=_('Comma separated list of IP addresses permitted to query caller'
               ' ID number, etc. Leave empty to allow all addresses.'))

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super(AsteriskSettings, self).create(vals)

    def write(self, vals):
        self.clear_caches()
        return super(AsteriskSettings, self).write(vals)

    def _get_name(self):
        # name fields in open_settings_form does not work. Why?
        for rec in self:
            rec.name = _('Settings')

    def open_settings_form(self, module='common'):
        rec = self.env['asterisk_common.settings'].search([])
        if not rec:
            rec = self.sudo().create({})
        else:
            rec = rec[0]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'asterisk_common.settings',
            'res_id': rec.id,
            'view_id': self.env.ref(
                'asterisk_{}.{}_settings_form'.format(module, module)).id,
            'name': _('{} Settings').format(module.capitalize()),
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    @api.model
    @ormcache('param')
    def get_param(self, param, default=False):
        try:
            data = self.search([])
            if not data:
                data = self.sudo().create({})
            else:
                data = data[0]
            logger.debug(
                'ASTERISK BASE SETTING PARAM: %s DATA: %s DEFAULT: %s',
                param, getattr(data, param, False), default)
            return getattr(data, param, default)
        except Exception as e:
            logger.warning('Get param error: %s', str(e))
            return default

    @api.model
    def bus_sendone(self, channel, message):
        # RPC method called from the Agent
        self.env['bus.bus'].sendone(channel, message)
        return True

    @api.model
    def on_agent_start(self):
        # Called from Agent after Odoo connection has been estabslied.
        logger.info('Asterisk Agent has been started.')
        self.env.user.remote_agent.update_state(force_create=True)
        return True

    def reformat_numbers(self):
        for rec in self.env['res.partner'].with_context(
                no_clear_cache=True).search([]):
            if rec.phone:
                rec.phone = rec._format_number(
                    rec.phone, format_type='international')
            if rec.mobile:
                rec.mobile = rec._format_number(
                    rec.mobile, format_type='international')
        self.env['res.partner'].pool.clear_caches()

    def reload_events(self):
        for agent in self.env['remote_agent.agent'].search([]):
            logger.info(
                'Sending reload events command to %s', agent.system_name)
            agent.send({'command': 'reload_events',
                        'notify_uid': self.env.uid})
