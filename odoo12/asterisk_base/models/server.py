# -*- coding: utf-8 -*-
import base64
from datetime import datetime
import logging
from odoo import api, models, fields, release, _
from odoo.exceptions import ValidationError
try:
    import humanize
    HUMANIZE = False  # Fix bug with translation FileNotFound.
except ImportError:
    HUMANIZE = False

logger = logging.getLogger(__name__)


class AsteriskServer(models.Model):
    _name = 'asterisk_base.server'
    _description = "Asterisk Server"

    name = fields.Char(required=True)
    agent = fields.Many2one(comodel_name='remote_agent.agent', required=True)
    user = fields.Many2one(related='agent.user', readonly=True)
    asterisk_user = fields.Many2one('asterisk_common.user',
                                    compute='_get_asterisk_user')
    system_name = fields.Char(related='agent.system_name', readonly=True)
    note = fields.Text()
    conf_files = fields.One2many(comodel_name='asterisk_base.conf',
                                 inverse_name='server')
    conf_count = fields.Integer(compute=lambda self: self._conf_count())
    sync_date = fields.Datetime(readonly=True)
    sync_uid = fields.Many2one('res.users', readonly=True, string='Sync by')
    cli_area = fields.Char(string="Console", compute='_get_cli_area')
    last_online = fields.Datetime(related='agent.last_online')
    last_online_human = fields.Char(related='agent.last_online_human')
    language = fields.Char(default='en')
    console_url = fields.Char(default=lambda x: x.get_default_console_url())
    init_conf_sync = fields.Boolean(
        string='Initial sync done?',
        help='Uncheck to receive files from Asterisk on next boot.')
    conf_sync = fields.Boolean(
        string='Config Sync',
        default=True,
        help='Upload files to Asterisk on Asterisk / Agent start',
    )
    conf_sync_direction = fields.Selection(selection=[
        ('asterisk_to_odoo', 'Asterisk -> Odoo'),
        ('odoo_to_asterisk', 'Odoo -> Asterisk')],
        default='odoo_to_asterisk',
        help='Where to send .conf files on every Agent / Asterisk start.'
    )

    _sql_constraints = [
        ('agent_uniq', 'UNIQUE(agent)',
            _('This Agent is already used!')),
    ]

    def _conf_count(self):
        for rec in self:
            rec.conf_count = self.env['asterisk_base.conf'].search_count(
                [('server', '=', rec.id)])

    def _get_last_online_human(self):
        for rec in self:
            if HUMANIZE:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    humanize.i18n.activate(to_translate)
                rec.last_online_human = humanize.naturaltime(
                    fields.Datetime.from_string(rec.last_online))
            else:
                rec.last_online_human = rec.last_online

    def _get_cli_area(self):
        for rec in self:
            rec.cli_area = '/asterisk_base/console/{}'.format(rec.id)

    def get_default_console_url(self):
        try:
            if release.version_info > (10,):
                from urllib.parse import urlparse
            else:
                from urlparse import urlparse
            url = urlparse(
                self.env['ir.config_parameter'].get_param('web.base.url'))
            return '{}s://{}:30000/'.format(url.scheme.replace('http', 'ws'),
                                            url.netloc.split(':')[0])
        except Exception:
            logger.exception('Get default console URL error:')
            return 'ws://127.0.0.1:30000/'

    def apply_changes_button(self):
        self.apply_changes(notify_uid=self.env.user.id)

    def apply_changes(self, notify_uid=None):
        self.ensure_one()
        changed_configs = self.env['asterisk_base.conf'].search(
            [('server', '=', self.id), ('is_updated', '=', True)])
        for conf in changed_configs:
            conf.upload_conf(notify_uid=notify_uid)
        if changed_configs:
            self.reload_action(notify_uid=notify_uid, delay=0.5)
        else:
            self.env['res.users'].astbase_notify(
                _('System {} no changes detected.').format(self.system_name))
            return False

    @api.model
    def apply_all_changes(self, notify_uid=None):
        for server in self.search([]):
            server.apply_changes(notify_uid=notify_uid)
        return True

    def upload_all_conf(self, auto_reload=False):
        self.ensure_one()
        data = {}
        for rec in [k for k in self.conf_files if k.content]:
            data[rec.name] = base64.b64encode(rec.content.encode()).decode()
        self.agent.send({
            'command': 'nameko_rpc',
            'service': '{}_files'.format(self.agent.system_name),
            'method': 'put_all_configs',
            'args': [data],
            'callback_method': 'upload_all_conf_response',
            'callback_model': 'asterisk_base.server',
            'pass_back': {'notify_uid': self.env.user.id,
                          'auto_reload': auto_reload},
        })
        self.conf_files.write({'is_updated': False})
        self.write({'sync_date': fields.Datetime.now(),
                    'sync_uid': self.env.uid})

    @api.model
    def upload_all_conf_response(self, response):
        if self.response_has_error(response):
            return False
        uid = response.get('pass_back', {}).get('notify_uid')
        if uid:
            self.env['res.users'].astbase_notify(
                _('Config files upload complete.'), uid=uid)
        if response.get('pass_back', {}).get('auto_reload'):
            self.env.user.asterisk_server.reload_action()
        return True

    def download_all_conf(self):
        try:
            self.ensure_one()
        except ValueError as e:
            if 'Expected singleton: asterisk_base.server()' in str(e):
                raise Exception(
                    'Odoo account %s is not set to Remote Agent.', self.env.uid)
        self.agent.send({
            'command': 'nameko_rpc',
            'service': '{}_files'.format(self.agent.system_name),
            'method': 'get_all_configs',
            'callback_method': 'download_all_conf_response',
            'callback_model': 'asterisk_base.server',
            'pass_back': {'notify_uid': self.env.user.id},
        })

    @api.model
    def download_all_conf_response(self, response):
        if self.response_has_error(response):
            return False
        files = response.get('result')
        server = self.env.user.asterisk_server
        for file, data in files.items():
            conf = self.env[
                'asterisk_base.conf'].with_context(
                conf_no_update=True).get_or_create(server.id, file)
            conf.write({
                'content': base64.b64decode(data['file_data'].encode()),
                'sync_date': fields.Datetime.now(),
                'sync_uid': self.env.uid,
            })
        # Update last sync
        server.write({'sync_date': fields.Datetime.now(),
                    'init_conf_sync': True,
                    'sync_uid': self.env.uid})
        uid = response.get('pass_back', {}).get('notify_uid')
        if uid:
            self.env['res.users'].astbase_notify(
                _('Config files download complete.'), uid=uid)
        return True

    def open_console_button(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/asterisk_base/console/{}".format(self.id),
            "target": "new",
        }

    def reload_button(self):
        self.reload_action(notify_uid=self.env.uid)

    def reload_action(self, module=None, notify_uid=None, delay=0):
        self.ensure_one()
        action = {'Action': 'Reload'}
        if module:
            action['Module'] = module
        self.agent.send({
            'command': 'nameko_rpc',
            'delay': delay,
            'service': '{}_ami'.format(self.agent.system_name),
            'method': 'send_action',
            'args': (action,),
            'status_notify_uid': self.env.uid,
            'pass_back': {'notify_uid': notify_uid}})

    @api.model
    def response_has_error(self, response):
        uid = response.get('pass_back', {}).get('notify_uid')
        if response.get('error'):
            if uid:
                self.env['res.users'].astbase_notify(
                    response['error']['message'], level='warning', uid=uid)
            else:
                logger.error(response['error']['message'])
            return True
        else:
            return False

    @api.model
    def on_fully_booted(self, event):
        logger.info(
            'System {} FullyBooted, uptime: {}, Last reload: {}.'.format(
                event.get('SystemName'), event.get('Uptime'),
                event.get('LastReload')))
        server = self.env.user.asterisk_server
        if not server.conf_sync:
            logger.info('Not syncing Asterisk config files, not enabled.')
            return True
        if server.conf_sync_direction == 'odoo_to_asterisk':
            # Check if there was a first config upload
            if not server.init_conf_sync:
                logger.info('Getting all .conf files from %s for the 1-st time...',
                            server.system_name)
                server.download_all_conf()
            else:
                logger.info('Sending .conf files to Asterisk system %s...',
                            server.system_name)
                server.upload_all_conf()
                server.reload_action(delay=3)
        else:
            # Get configs from Asterisk
            logger.info('Getting all .conf files from Asterisk system %s...',
                        server.system_name)
            server.download_all_conf()
        return True

    def send(self, data, timeout=None, silent=False):
        self.ensure_one()
        self.agent.send(data, timeout=timeout, silent=silent)

    def _get_asterisk_user(self):
        for rec in self:
            rec.asterisk_user = self.env['asterisk_common.user'].search(
                [('user', '=', self.env.user.id),
                 ('server', '=', rec.id)])
