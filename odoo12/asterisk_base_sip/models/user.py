import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.asterisk_base.utils import remove_empty_lines

logger = logging.getLogger(__name__)


class BaseSipUserChannel(models.Model):
    _inherit = 'asterisk_common.user_channel'
    _order = 'sequence'

    sip_peer = fields.Many2one('asterisk_base_sip.peer',
                               ondelete='cascade')
    ring_enabled = fields.Boolean(default=True, string='Ring')
    ring_timeout = fields.Integer(default=30)
    sequence = fields.Integer(default=100, index=True)
    originate_context = fields.Char(required=False,
                                    compute='_get_originate_context')

    def _get_originate_context(self):
        for rec in self:
            if rec.sip_peer:
                rec.originate_context = rec.sip_peer.context
            else:
                rec.originate_context = rec.context

    def _set_originate_context(self):
        for rec in self:
            if not self.env.context.get('from_peer') and rec.sip_peer:
                raise ValidationError(
                    _('Use SIP -> Peers menu to change peer context'))
            else:
                rec.context = rec.originate_context

    def create(self, create_vals):
        if type(create_vals) is not list:
            create_vals = [create_vals]
        for vals in create_vals:
            if not self.env.context.get('from_peer') and vals.get(
                    'channel') and 'SIP' in vals['channel'].upper():
                raise ValidationError(
                    _('You must create SIP peers from SIP -> Peers menu.'))
        return super(BaseSipUserChannel, self).create(vals)

    def write(self, vals):
        if not self.env.context.get('from_peer') and 'channel' in vals \
                and 'SIP' in vals['channel'].upper():
            raise ValidationError(
                _('You must edit SIP peers from SIP -> Peers menu.'))
        return super(BaseSipUserChannel, self).write(vals)

    def unlink(self):
        for rec in self:
            if not self.env.context.get('from_peer') and  \
                    rec.channel and 'SIP' in rec.channel.upper():
                raise ValidationError(
                    _('You must delete SIP peers from SIP -> Peers menu.'))
        return super(BaseSipUserChannel, self).unlink()


class BaseSipUser(models.Model):
    _inherit = 'asterisk_common.user'

    accountcode = fields.Char(compute='_get_accountcode')
    route_groups = fields.Many2many(
        'asterisk_base_sip.route_group',
        required=True,
        relation='asterisk_base_sip_user_route_groups')
    callerid_numbers = fields.One2many(
        'asterisk_base_sip.translation', string='CallerID Translations',
        inverse_name='src_user', readonly=True)
    dialplan = fields.Text(compute='_get_dialplan')
    ring_channels = fields.One2many(
        'asterisk_common.user_channel', string='Channels',
        inverse_name='asterisk_user')
    call_waiting = fields.Boolean()
    # VoiceMail
    vm_enabled = fields.Boolean(string="VoiceMail")
    vm_on_busy_enabled = fields.Boolean(string="On Busy")
    vm_on_unavail_enabled = fields.Boolean(string='On Unavailable')
    vm_email = fields.Char(string='E-Mail Address')
    vm_direct_call_enabled = fields.Boolean(string='Direct Mailbox Call')
    vm_max_length = fields.Integer(default=120, string='Max Message Duration')
    vm_max_messages = fields.Integer(default=30, string='Max Messages / Inbox')
    # Call forward
    cf_on_busy_enabled = fields.Boolean('On Busy')
    cf_on_busy_number = fields.Char(string='On Busy Number')
    cf_on_unavail_enabled = fields.Boolean('On Unavailable')
    cf_on_unavail_number = fields.Char(string='On Unavailable Number')
    cf_uncond_enabled = fields.Boolean('Unconditional')
    cf_uncond_number = fields.Char(string='Unconditional Number')

    @api.onchange('exten', 'vm_enabled',
                  'vm_on_unavail_enabled', 'vm_on_busy_enabled',
                  'cf_on_busy_number', 'cf_on_busy_enabled',
                  'cf_on_unavail_number', 'cf_on_unavail_enabled',
                  'cf_uncond_number', 'cf_uncond_enabled')
    def _get_dialplan(self):
        for rec in self:
            data = self.env['ir.qweb'].with_context({'lang': 'en_US'}).render(
                'asterisk_base_sip.user_dialplan',
                {'rec': rec}).decode('utf-8')
            rec.dialplan = remove_empty_lines(data)

    def build_extension(self):
        self.ensure_one()
        return self.env['ir.qweb'].with_context({'lang': 'en_US'}).render(
            'asterisk_base_sip.dialplan_extension',
            {'rec': self}).decode('utf-8')

    @api.model
    def build_conf(self):
        users = self.env['asterisk_common.user'].search([])
        for server in users.mapped('server'):
            conf_data = ''
            for u in users.filtered(lambda r: r.server == server):
                conf_data += u.dialplan
                conf_data += '\n\n'
            conf = self.env['asterisk_base.conf'].get_or_create(
                server.id, 'extensions_odoo_user.conf')
            conf.content = '{}'.format(
                remove_empty_lines(conf_data))
            conf.include_from('extensions.conf')

    def _get_extension_name(self):
        for rec in self:
            rec.extension_name = rec.user.name

    @api.onchange('agent', 'server')
    def _reset_route_groups(self):
        if not self.server:
            self.route_groups = False
        else:
            if not self.route_groups or self._origin.server != self.server:
                groups = self.env['asterisk_base_sip.route_group'].search(
                    [('server', '=', self.server.id),
                     ('is_user_default', '=', True)])
                self.route_groups = groups
            return {'domain': {
                'route_groups': [('server', '=', self.server.id)]}}
        
    @api.onchange('user', 'cf_onbusy_enabled', 'cf_on_unavail_enabled',
                  'cf_uncond_enabled')
    def _change_vm_and_cf(self):
        try:
            if not self.user:
                return
            # VoiceMail
            if not self.vm_email or \
                    self._origin.vm_email == \
                    self._origin.user.partner_id.email:
                self.vm_email = self.user.partner_id.email
            # Get user's number
            old_number = self._origin.user.partner_id.mobile_normalized or \
                self._origin.user.partner_id.phone_normalized
            new_number = self.user.partner_id.mobile_normalized or \
                self.user.partner_id.phone_normalized
            # CF on Unconditional
            if not self.cf_on_busy_number or \
                    self._origin.cf_on_busy_number == old_number:
                self.cf_on_busy_number = new_number
            # CF on Unavailable
            if not self.cf_on_unavail_number or \
                    self._origin.cf_on_unavail_number == old_number:
                self.cf_on_unavail_number = new_number
            # CF Unconditional
            if not self.cf_uncond_number or \
                    self._origin.cf_uncond_number == old_number:
                self.cf_uncond_number = new_number
        except Exception:
            logger.exception('Change VM & CF error:')

    @api.constrains('vm_enabled', 'vm_on_busy_enabled', 'vm_on_unavail_enabled')
    def _require_b_or_u(self):
        if self.vm_enabled and not (
                self.vm_on_busy_enabled or self.vm_on_unavail_enabled):
            raise ValidationError("Please select when to enable the voicemail.")

    @api.onchange('vm_enabled')
    def _set_b_and_u(self):
        if self.vm_enabled:
            self.vm_on_unavail_enabled = True
            self.vm_on_busy_enabled = True
        else:
            self.vm_on_unavail_enabled = False
            self.vm_on_busy_enabled = False

    def get_ring_channels_dial_string(self):
        # Called from conf templates to get  dial string for all channels.
        self.ensure_one()
        if self.ring_channels:
            return '&'.join(
                [k.channel for k in self.ring_channels if k.ring_enabled])
        else:
            return ''

    def _get_accountcode(self):
        for rec in self:
            rec.accountcode = 'user-{}'.format(rec.id)

    def get_ring_channels_timeout(self):
        # Called from conf templates to get max timeout of all channels
        self.ensure_one()
        return max([k.ring_timeout for k in self.ring_channels] or [60])
