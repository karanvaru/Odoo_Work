import logging
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
import uuid

logger = logging.getLogger(__name__)


class AsteriskUserChannel(models.Model):
    _name = 'asterisk_common.user_channel'
    _rec_name = 'channel'
    _description = 'Asterisk User Channel'

    channel = fields.Char(required=True)
    # Store originate_context here.
    context = fields.Char()
    asterisk_user = fields.Many2one('asterisk_common.user', required=True,
                                    ondelete='cascade')
    user = fields.Many2one(related='asterisk_user.user', readonly=True)
    agent = fields.Many2one(related='asterisk_user.agent', readonly=True)
    system_name = fields.Char(related='asterisk_user.agent.system_name',
                              readonly=True, store=True)
    originate_enabled = fields.Boolean(default=True, string="Originate")
    originate_context = fields.Char(
        default=lambda self: self._get_default_context(),
        string='Context', required=True,
        compute='_get_originate_context', inverse='_set_originate_context')

    _sql_constraints = [
        ('system_channel_uniq', 'unique (system_name,channel)',
            _('The channel is already defined for this System!')),
    ]

    def create(self, create_vals):
        if type(create_vals) is not list:
            create_vals = [create_vals]
        for vals in create_vals:
            try:
                if 'channel' in vals and vals['channel']:
                    chan, name = vals['channel'].split('/')
                    vals['channel'] = '{}/{}'.format(chan.upper(), name)
            except Exception:
                logger.error('Bad channel format: %s', vals['channel'])
                raise ValidationError(
                    _('Bad channel format. Example: SIP/101.'))
        return super(AsteriskUserChannel, self).create(vals)

    def write(self, vals):
        try:
            if 'channel' in vals and vals['channel']:
                chan, name = vals['channel'].split('/')
                vals['channel'] = '{}/{}'.format(chan.upper(), name)
        except Exception:
            raise ValidationError(_('Bad channel format. Example: SIP/101.'))
        return super(AsteriskUserChannel, self).write(vals)

    def _get_default_context(self):
        return self.env['asterisk_common.settings'].get_param(
            'originate_context', 'from-internal')

    def _get_originate_context(self):
        for rec in self:
            rec.originate_context = rec.context

    def _set_originate_context(self):
        for rec in self:
            rec.context = rec.originate_context


class AsteriskUser(models.Model):
    _name = 'asterisk_common.user'
    _order = 'user'
    _rec_name = 'user'
    _description = _('Asterisk User')

    exten = fields.Char()
    user = fields.Many2one('res.users', required=True,
                           ondelete='cascade',
                           # Exclude shared users
                           domain=[('share', '=', False)])
    name = fields.Char(related='user.name', readonly=True)
    lang = fields.Char(default=lambda self: self._get_default_lang(),
                       string='Language',
                       help='Two digits lang code, for example: en')
    agent = fields.Many2one('remote_agent.agent', string='System',
                            required=True, ondelete='restrict',
                            default=lambda self: self._get_default_agent())
    system_name = fields.Char(related='agent.system_name', stored=True)
    partner = fields.Many2one(related='user.partner_id', readonly=True)
    is_primary_system = fields.Boolean(default=True, string='Primary')
    channels = fields.One2many('asterisk_common.user_channel',
                               inverse_name='asterisk_user')
    originate_vars = fields.Text(
        default='SIPADDHEADER=Alert-Info: Auto Answer',
        string='Variables',
        help=_('Examples:\nSIPADDHEADER=Alert-Info: Auto Answer\n'
               'PJSIP_HEADER(add,Alert-Info)=Auto Answer'))

    _sql_constraints = [
        ('exten_uniq', 'unique (exten,agent)',
         _('The phone extension @ agent must be unique !')),
        ('user_uniq', 'unique ("user",agent)',
         _('The user @ agent must be unique !')),
        ('primary_uniq', 'unique ("user",is_primary_system)',
         _('The primary system is already defined!')),
    ]

    @api.model
    def create(self, vals):
        user = super(AsteriskUser, self).create(vals)
        asterisk_user_group = self.env.ref(
            'asterisk_common.group_asterisk_user')
        if user.user not in asterisk_user_group.users:
            asterisk_user_group.sudo().users = [(4, user.user.id)]
        if user and not self.env.context.get('no_clear_cache'):
            self.pool.clear_caches()
        return user

    def write(self, values):
        res = super(AsteriskUser, self).write(values)
        if res and not self.env.context.get('no_clear_cache'):
            self.pool.clear_caches()
        return res

    def unlink(self):
        res = super(AsteriskUser, self).unlink()
        if res and not self.env.context.get('no_clear_cache'):
            self.pool.clear_caches()
        return res

    def _get_default_agent(self):
        agents = self.env['remote_agent.agent'].search([])
        if len(agents) == 1:
            return agents[0].id

    def _get_default_lang(self):
        try:
            return self.env.user.lang.split('_')[0]
        except Exception:
            pass

    def open_user_settings(self):
        rec = self.env['asterisk_common.user'].search(
            [('user', '=', self.env.user.id)])
        if not rec:
            raise ValidationError(_('Asterisk user is not configured!'))
        elif len(rec) == 1:
            # One user at one agent is defined, open the form.
            rec = rec[0]
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'asterisk_common.user',
                'res_id': rec.id,
                'view_id': self.env.ref(
                    'asterisk_common.user_settings_form').id,
                'name': _('User Settings'),
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }
        else:
            # Many users are defined, open list view.
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'asterisk_common.user',
                'views': [
                    (self.env.ref(
                        'asterisk_common.user_settings_list').id, 'tree'),
                    (self.env.ref(
                        'asterisk_common.user_settings_form').id, 'form')],
                'name': _('User Settings'),
                'domain': "[('user', '=', uid)]",
                'view_mode': 'tree,form',
                'view_type': 'form',
                'target': 'current',
            }

    def _get_originate_vars(self):
        self.ensure_one()
        try:
            if not self.originate_vars:
                return []
            return [k for k in self.originate_vars.split('\n') if k]
        except Exception:
            logger.exception('Get originate vars error:')
            return []

    @api.model
    def originate_call(self, number, model=None, res_id=None,
                       system_name='asterisk', variables={}):
        if not number:
            raise ValidationError(_('Phone number not set!'))
        if not self.env.user.asterisk_user:
            raise ValidationError(_("PBX user is not configured!"))
        format_type = self.env['asterisk_common.settings'].get_param(
            'originate_format', 'e164')
        # Format number if required
        if format_type != 'no_format' and model and res_id:
            logger.debug('FORMAT NUMBER FOR MODEL %s', model)
            obj = self.env[model].browse(res_id)
            if getattr(obj, '_format_number', False):
                number = obj._format_number(number, format_type=format_type)
                logger.debug('MODEL FORMATTED NUMBER: {}'.format(number))
        else:
            logger.debug('FORMAT NOT ENABLED')
        # Strip formatting if present
        number = number.replace(' ', '')
        number = number.replace('(', '')
        number = number.replace(')', '')
        number = number.replace('-', '')
        if number[0] == '+' and self.env['asterisk_common.settings'].get_param(
                'originate_strip_plus'):
            logger.debug('REMOVING +')
            number = number[1:]
        prefix = self.env['asterisk_common.settings'].get_param(
            'originate_prefix')
        if prefix:
            logger.debug('ADDING ORIGINATE PREFIX %s', prefix)
            number = '{}{}'.format(prefix, number)
        logger.debug('ORIGINATE NUMBER %s', number)
        # Get user defined varaibles headers for auto-answer.
        variables = self.env.user.asterisk_user._get_originate_vars()
        # Set callerid to dialed partner if set in options
        if self.env['asterisk_common.settings'].get_param(
                'originate_partner_callerid'):
            # Save original callerid
            variables.append('OUTBOUND_CALLERID="{}" <{}>'.format(
                self.env.user.name, self.env.user.asterisk_user.exten))
            if model and res_id:
                obj = self.env[model].browse(res_id)
                if hasattr(obj, 'name'):
                    name = obj.name
                else:
                    name = number
                callerid = 'To: {} <{}>'.format(name, number)
            else:
                callerid = 'To: {} <{}>'.format(number, number)
        # Get originate timeout
        originate_timeout = float(self.env[
            'asterisk_common.settings'].get_param('originate_timeout'))
        # Check if user has channels
        if not self.env.user.asterisk_user.channels:
            raise ValidationError('You do not have any channels set up!')
        originate_channels = [k for k in self.env.user.asterisk_user.channels
                              if k.originate_enabled]
        if not originate_channels:
            raise ValidationError(
                _('Enable at least one channel to originate!'))
        # Init channel_ids for all channels to populate originate_channels
        originate_channels_data = {}
        for ch in originate_channels:
            originate_channels_data[ch.channel] = {
                'channel_id': uuid.uuid4().hex,
                'other_channel_id': uuid.uuid4().hex,
            }
        for user_channel in originate_channels:
            # Save in cache originate operation
            channel_id = originate_channels_data[user_channel.channel]['channel_id']
            originate_call_data = {
                'uid': self.env.user.id,
                'channel': channel_id,
                'model': model,
                'res_id': res_id,
                'originate_timeout': originate_timeout,
                'originate_channels': originate_channels_data,
            }
            self.env['kv_cache.cache'].put(
                channel_id, originate_call_data, tag='originated_call',
                serialize='json')
            self.call_originate_request(
                system_name=self.env.user.asterisk_user.agent.system_name,
                exten=self.env.user.asterisk_user.exten,
                context=user_channel.originate_context,
                number=number,
                channel=user_channel.channel,
                channel_id=channel_id,
                other_channel_id=originate_channels_data[
                    user_channel.channel]['other_channel_id'],
                callerid=callerid,
                timeout=originate_timeout,
                variables=variables)

    @api.model
    def call_originate_request(self, system_name='asterisk', exten=None,
                               context=None, number=None, channel=None,
                               channel_id=None, other_channel_id=None,
                               variables=[], callerid='"" <>', timeout=None):
        # Generate channel ID to track it.
        if not channel_id:
            channel_id = uuid.uuid4().hex
        if not other_channel_id:
            other_channel_id = uuid.uuid4().hex
        if not timeout:
            timeout = int(self.env[
                    'asterisk_common.settings'].get_param(
                    'originate_timeout'))
        data = {
            'command': 'nameko_rpc',
            'service': '{}_ami'.format(system_name),
            'method': 'send_action',
            'callback_model': 'asterisk_common.user',
            'callback_method': 'call_originate_response',
            'args': [{
                'Action': 'Originate',
                'Context': context,
                'Priority': '1',
                'Timeout': 1000 * timeout,
                'Channel': channel,
                'Exten': number,
                'Async': 'true',
                'EarlyMedia': 'true',
                'CallerID': callerid,
                'ChannelId': channel_id,
                'OtherChannelId': uuid.uuid4().hex,
                'Variable': variables,
            }],
            'pass_back': {'uid': self.env.user.id},
        }
        self.env.user.asterisk_user.agent.send(data)

    @api.model
    def call_originate_response(self, data):
        result = data.get('result', {})
        uid = data.get('pass_back', {}).get('uid')
        if result and type(result) is list:            
            logger.debug('Originate result: %s', result)
            # Convert messages to o =ne dict.
            res = {}
            for r in result:
                res.update(r)
            if res['Response'] == 'Error' and uid:
                self.env['bus.bus'].sendone(
                    'remote_agent_notification_{}'.format(uid), {
                        'message': res['Message'],
                        'warning': True, 'title': 'Error',
                    })
        elif data.get('error'):
            message = data['error'].get('message') or str(data['error'])
            if uid:
                self.env['bus.bus'].sendone(
                    'remote_agent_notification_{}'.format(uid), {
                        'message': message,
                        'warning': True,
                        'title': 'PBX',
                    })
        return True

    @api.model
    def ami_originate_response(self, data):
        # This comes from Asterisk OriginateResponse AMI message when
        # call originate has been failed.
        resp = data.get('Response')
        reason = data.get('Reason')
        uniqueid = data.get('Uniqueid')
        originate_data = self.env['kv_cache.cache'].get(
            uniqueid, tag='originated_call', serialize='json')
        originate_uid = originate_data.get('uid')
        if resp == 'Failure' and originate_uid:
            self.env['res.users'].asterisk_notify(
                _('Call failed, reason {0}').format(reason),
                uid=originate_uid, warning=True)
        return True
