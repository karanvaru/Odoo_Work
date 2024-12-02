from datetime import datetime, timedelta
import json
try:
    import humanize
    HUMANIZE = True
except ImportError:
    HUMANIZE = False
import logging
import os
import random
import requests
import string
import time
from urllib.parse import urlparse, urlunparse
import uuid

from odoo import models, fields, api, registry, _
from odoo.exceptions import ValidationError
from odoo.addons.bus.models.bus import dispatch

from .agent_state import STATES

logger = logging.getLogger(__name__)

DEFAULT_PASSWORD_LENGTH = os.getenv('AGENT_DEFAULT_PASSWORD_LENGTH', '10')
CHANNEL_PREFIX = 'remote_agent'


class Agent(models.Model):
    _name = 'remote_agent.agent'
    _description = 'Remote Agent'
    _rec_name = 'system_name'

    system_name = fields.Char(required=True,
                              default=lambda r: r._get_default_system_name())
    version = fields.Char(readonly=True)
    note = fields.Text()
    alarm = fields.Text(readonly=True)
    token = fields.Char(groups="")
    bus_timeout = fields.Integer(default=10)
    bus_enabled = fields.Boolean(default=True)
    http_enabled = fields.Boolean(string=_('HTTP(s) Enabled'))
    http_url = fields.Char(string=_('HTTP(s) URL'))
    http_timeout = fields.Integer(string=_('HTTP(s) Timeout'), default=10)
    http_ssl_verify = fields.Boolean(string=_('SSL Verify'),
                                     help=_("Verify agent's certificate"))
    user = fields.Many2one('res.users', ondelete='restrict', required=True)
    states = fields.One2many(comodel_name='remote_agent.agent_state',
                             inverse_name='agent')
    state_count = fields.Integer(compute='_get_state_count')
    state = fields.Selection(STATES, store=True, compute='_get_current_state')
    state_changed = fields.Datetime(compute='_get_state_changed')
    state_changed_human = fields.Char(compute='_get_state_changed_human',
                                      string=_('State Changed'))
    state_icon = fields.Char(compute='_get_state_changed_icon')
    last_online = fields.Datetime(compute='_get_last_online')
    last_online_human = fields.Char(compute='_get_last_online_human',
                                    string=_('Last Online'))

    _sql_constraints = [
        ('system_name_uniq', 'unique(system_name)',
            _('This system name already exists!')),
        ('user_uniq', 'unique("user")',
            _('This user is already used!')),
    ]

    def _get_default_system_name(self):
        return '{}'.format(uuid.uuid4().hex)

# Model and UI methods #

    def refresh_view_button(self):
        return True

    @api.depends('states')
    def _get_current_state(self):
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id)], limit=1, order='id desc')
            rec.state = state_changed[
                0].state if state_changed else 'offline'

    def _get_state_changed(self):
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id)], limit=1, order='id desc')
            rec.state_changed = state_changed[
                0].create_date if state_changed else False

    def _get_state_changed_human(self):
        global HUMANIZE
        if HUMANIZE:
            try:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    humanize.i18n.activate(to_translate)
            except Exception:
                HUMANIZE = False
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id)], limit=1, order='id desc')
            if state_changed:
                if HUMANIZE:
                    rec.state_changed_human = humanize.naturaltime(
                        fields.Datetime.from_string(
                            state_changed[0].create_date))
                else:
                    rec.state_changed_human = state_changed[0].create_date
            else:
                rec.state_changed_human = ''

    def _get_state_changed_icon(self):
        for rec in self:
            if rec.state == 'online':
                rec.state_icon = '<span class="fa fa-chain"/>'
            else:
                rec.state_icon = '<span class="fa fa-chain-broken"/>'

    def _get_last_online(self):
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id), ('state', '=', 'online')],
                limit=1, order='id desc')
            rec.last_online = state_changed[0].create_date if \
                state_changed else False

    def _get_last_online_human(self):
        try:
            if HUMANIZE:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    humanize.i18n.activate(to_translate)
            for rec in self:
                if HUMANIZE:
                    rec.last_online_human = humanize.naturaltime(
                        fields.Datetime.from_string(
                            rec.last_online)) if rec.last_online else ''
                else:
                    rec.last_online_human = rec.last_online
        except Exception:
            logger.exception('Humanize error:')
            for rec in self:
                rec.last_online_human = rec.last_online

    def _get_state_count(self):
        for rec in self:
            rec.state_count = len(rec.states)

    def generate_password(length=DEFAULT_PASSWORD_LENGTH):
        try:
            length = int(length)
        except ValueError:
            logger.warning('Bad DEFAULT_PASSWORD_LENGTH: %s',
                           DEFAULT_PASSWORD_LENGTH)
            length = 10
        chars = string.ascii_letters + string.digits
        password = ''
        while True:
            password = ''.join(map(lambda x: random.choice(
                chars), range(length)))
            if filter(lambda c: c.isdigit(), password) and \
                    filter(lambda c: c.isalpha(), password):
                break
        return password

    def adjust_permissions(self):
        self.ensure_one()
        # Set to Portal
        if not self.user.has_group(
                'base.group_portal'):
            # Reset user role
            self.user.write({'groups_id': [
                (3, self.env.ref('base.group_user').id),
                (4, self.env.ref('base.group_portal').id)
            ]})
        if not self.user.has_group('asterisk_common.group_asterisk_agent'):
            ast_group = self.env.ref('asterisk_common.group_asterisk_agent')
            ast_group.write({'users': [(4, self.user.id)]})

# Remote communication methods #
    @api.model
    def send_agent(self, system_name, message, silent=False):
        agent = self.search([('system_name', '=', system_name)])
        if not agent and not silent:
            raise ValidationError(_('Agent {} not found!'.format(system_name)))
        return agent[0].send(message, silent=silent)

    def send(self, message, timeout=None, silent=False):
        if self.env.context.get('install_mode'):
            logger.info('Not sending to Agents in install mode.')
            return
        self.ensure_one()
        if not timeout:
            timeout = self.http_timeout
        # Unpack if required
        if type(message) != dict:
            message = json.loads(message)
        if self.http_enabled:
            # Use Agent HTTP interface to communicate
            try:
                r = requests.post(
                    self.http_url,
                    json=message,
                    headers={'X-Token': self.token},
                    timeout=timeout,
                    verify=self.http_ssl_verify)
                # Test for good response.
                r.raise_for_status()
            except Exception:
                if not silent:
                    raise
        elif self.bus_enabled:
            # Use Odoo bus for communication
            message['token'] = self.sudo(True).token
            if type(message) == dict:
                message = json.dumps(message)
            self.env['bus.bus'].sendone('{}/{}'.format(CHANNEL_PREFIX,
                                        self.system_name), message)
        else:
            raise ValidationError(_('You should enable either bus or HTTP!'))

    def call(self, message, timeout=None, silent=False):
        self.ensure_one()
        if self.http_enabled:
            return self.call_http(message, timeout=timeout, silent=silent)
        elif self.bus_enabled:
            return self.call_bus(message, timeout=timeout, silent=silent)
        else:
            raise ValidationError(_('You should enable either bus or HTTP!'))

    def call_http(self, message, timeout=None, silent=False):
        self.ensure_one()
        if not timeout:
            timeout = self.http_timeout
        try:
            r = requests.post(self.http_url, timeout=timeout, json=message,
                              headers={'X-Token': self.sudo().token},
                              verify=self.http_ssl_verify)
            r.raise_for_status()
            self.sudo().update_state(
                state='online',
                note='{} reply'.format(message['command']))
            return r.json()
        except Exception as e:
            self.sudo().update_state(
                state='offline',
                note='{} not replied: {}'.format(
                    message['command'], str(e)))
            return {}

    def call_bus(self, message, timeout=None, silent=False):
        self.ensure_one()
        if not timeout:
            timeout = self.bus_timeout
        channel = '{}/{}'.format(CHANNEL_PREFIX, self.system_name)
        reply_channel = '{}/{}'.format(channel, uuid.uuid4().hex)
        message.update(
            {'reply_channel': reply_channel, 'token': self.sudo().token})
        # Send in separate transaction so that we could get an reply.
        with api.Environment.manage():
            with registry(self.env.cr.dbname).cursor() as new_cr:
                env = api.Environment(new_cr, self.env.uid, self.env.context)
                env['bus.bus'].sendone(channel, json.dumps(message))
                new_cr.commit()
        # Poll is done is separate transaction in bus.bus so we don't do it.
        if dispatch:
            # Gevent instance
            agent_reply = dispatch.poll(self.env.cr.dbname,
                                        [reply_channel],
                                        last=0, timeout=timeout)
        else:
            # Cron instance
            started = datetime.utcnow()
            to_end = started + timedelta(seconds=timeout)
            agent_reply = None
            while datetime.now() < to_end:
                with api.Environment.manage():
                    with registry(self.env.cr.dbname).cursor() as new_cr:
                        env = api.Environment(
                            new_cr, self.env.uid, self.env.context)
                        rec = env['bus.bus'].sudo().search(
                            [('create_date', '>=', started.strftime(
                                '%Y-%m-%d %H:%M:%S')),
                             ('channel', '=', '"{}"'.format(reply_channel))])
                        if not rec:
                            time.sleep(0.25)
                        else:
                            logger.debug(
                                'Got reply within %s seconds',
                                (datetime.now() - started).total_seconds()),
                            agent_reply = [{'message':
                                            json.loads(rec[0].message)}]
                            break
        if agent_reply:
            # Update agent state
            self.sudo(True).update_state(
                state='online',
                note='{} reply'.format(message['command']))
            # Convert result message to dict
            reply_message = agent_reply[0]['message']
            if type(reply_message) != dict:
                json.loads(reply_message)
            return reply_message
        # No reply recieved
        else:
            self.sudo(True).update_state(
                state='offline',
                note='{} not replied'.format(message['command']))
            return {}

    @api.model
    def reload_view(self, uid=None, model=None):
        if not uid:
            uid = self.env.uid
        self.env['bus.bus'].sendone(
            'remote_agent_notification_{}'.format(uid),
            {'reload': True, 'model': model})
        return True

    def restart(self):
        self.ensure_one()
        self.call({'command': 'restart',
                   'notify_uid': self.env.user.id})

    def ping_button(self):
        self.ensure_one()
        self.call({'command': 'ping',
                   'notify_uid': self.env.user.id})

    def clear_alarm_button(self):
        self.ensure_one()
        self.alarm = False

# RPC Calls from Agent #
    @api.model
    def bus_sendone(self, channel, message):
        # Override sendone as original method does not return value for RPC
        self.env['bus.bus'].sendone(channel, message)
        return True

    @api.model
    def update_token(self, token):
        agent = self.env.user.remote_agent
        if not agent:
            logger.error('Agent not found for user %s!', self.env.user)
            return False
        else:
            agent.token = token
            agent.update_state()
            return True

    @api.model
    def update_system_name(self, system_name):
        # Called from the Agent to set its system name before polling.
        agent = self.env.user.remote_agent
        if not agent:
            logger.error('Agent not found for user %s!', self.env.user.name)
            return False
        else:
            agent.system_name = system_name
            return True

    def update_state(self, state='online', note=False, force_create=False):
        # Method called from Agent to update its state on start.
        self.ensure_one()
        state_changed = self.env['remote_agent.agent_state'].search([
            ('agent', '=', self.id)], limit=1, order='id desc')
        # Create online state if previous state was offline
        if (force_create or not state_changed or
                (state_changed and state_changed.state != state)):
            self.env['remote_agent.agent_state'].create(
                {'agent': self.id, 'note': note, 'state': state})
        return True

    @api.model
    def set_alarm(self, system_name, message):
        agent = self.search([('system_name', '=', system_name)])
        agent.alarm = message
        return True

    @api.model
    def clear_alarm(self, system_name, message):
        # TODO: alarm message in event log
        agent = self.search([('system_name', '=', system_name)])
        agent.alarm = False
        return True
