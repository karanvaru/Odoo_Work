import logging
import string
from collections import namedtuple

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.asterisk_base.utils import remove_empty_lines
from odoo.addons.asterisk_base.utils import get_default_server
from .help import *

logger = logging.getLogger(__name__)

JOINEMPTY_CHOICES = [
    ('yes', 'yes (can join a queue with no members)'),
    ('no', 'no (cannot join a queue with no members)'),
    ('strict', 'strict (cannot join a queue with only unavailable members)'),
    ('loose', 'loose (paused queue members do not count as unavailable)'),
]

YESNO_CHOICES = [
    ('yes', _('Yes')),
    ('no', _('No')),
]



class Queue(models.Model):
    _name = 'asterisk_base_queues.queue'
    _description = 'Queue'

    name = fields.Char(required=True)
    server = fields.Many2one(comodel_name='asterisk_base.server',
                             required=True, default=get_default_server)
    extension = fields.Many2one('asterisk_base.extension')
    exten = fields.Char(related='extension.number', readonly=False,
                        store=True)
    # Queue cmd options
    ringinuse = fields.Boolean(
        string='Ring in Use',
        help='Avoid sending calls to members whose devices'
             ' are known to be in use')
    announce_frequency = fields.Integer(default=30)
    announce_holdtime = fields.Selection(YESNO_CHOICES)
    timeout = fields.Integer(default=15)
    continue_on_hangup = fields.Boolean(
        help='Continue in the dialplan if the callee hangs up (c)')
    # [queue] options
    strategy = fields.Selection([('ringall', 'Ring all'),
                                 ('leastrecent', 'Least recent'),
                                 ('fewestcalls', 'Fewest calls'),
                                 ('random', 'Random'),
                                 ('rrmemory', 'Rrmemory'),
                                 ('linear', 'Linear'),
                                 ('wrandom', 'Wrandom')],
                                default='ringall', required=True)
    ring_timeout = fields.Integer(
        required=True, default=15,
        help='How long do we let the phone ring before we consider this a '
             'timeout. Timeout in seconds when calling an agent.')
    musicclass = fields.Char(default='default', string='Music Class')
    joinempty = fields.Selection(JOINEMPTY_CHOICES, string='Join Empty',
                                 default='yes', required=True)
    leavewhenempty = fields.Boolean(string='Leave When Empty')
    keepstats = fields.Boolean(string='Keep Stats',
                               help='Keep queue statistics during a reload.')
    maxlen = fields.Integer(
        default=0, required=True, string='Max Length',
        help='Maximum number of people waiting in the queue (0 for unlimited)')
    servicelevel = fields.Integer(
        required=True, default=60, string='Service Level',
        help='Used for service level statistics (calls answered within '
             'service level time frame)')
    reportholdtime = fields.Boolean(
        string='Report Hold Time',
        help="Report the caller's hold time to the member before they are "
             "connected to the caller")
    options = fields.Char(default='htC', help=HELP_QUEUE_OPTIONS)
    static_members = fields.One2many(
        'asterisk_base_queues.queue_member', 'queue',
        domain=[('is_static', '=', True)])
    dynamic_members = fields.One2many(
        'asterisk_base_queues.queue_member', 'queue',
        domain=[('is_static', '=', False)]
    )
    is_user_joined = fields.Boolean(compute='_is_user_joined')
    # Queue status attributes
    abandoned = fields.Char(readonly=True)
    calls = fields.Char(readonly=True)
    completed = fields.Char(readonly=True)
    holdtime = fields.Char(readonly=True, string='Hold Time')
    max_call = fields.Char(readonly=True)
    service_level = fields.Char(readonly=True)
    service_level_perf = fields.Char(readonly=True)
    service_level_perf2 = fields.Char(readonly=True)
    talk_time = fields.Char(readonly=True)
    weight = fields.Char(readonly=True)
    timeout_exten = fields.Many2one(
        'asterisk_base.extension', ondelete='restrict')
    full_exten = fields.Many2one(
        'asterisk_base.extension', ondelete='restrict')
    join_empty_exten = fields.Many2one(
        'asterisk_base.extension', ondelete='restrict')
    leave_empty_exten = fields.Many2one(
        'asterisk_base.extension', ondelete='restrict')
    join_unavail_exten = fields.Many2one(
        'asterisk_base.extension', ondelete='restrict')
    leave_unavail_exten = fields.Many2one(
        'asterisk_base.extension', ondelete='restrict')
    continue_exten = fields.Many2one(
        'asterisk_base.extension', ondelete='restrict')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('The queue name must be unique !')),
    ]

    @api.model
    def create(self, vals):
        res = super(Queue, self).create(vals)
        self.env['asterisk_base.extension'].create_extension_for_obj(res)
        if not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base.extension'].build_conf()
        return res

    def write(self, vals):
        res = super(Queue, self).write(vals)
        if not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base.extension'].build_conf()
        return res

    def unlink(self):
        for rec in self:
            if rec.extension:
                rec.extension.unlink()
        res = super(Queue, self).unlink()
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base.extension'].build_conf()
        return res

    @api.constrains('name')
    def check_name(self):
        allowed_chars = string.ascii_letters + string.digits + '_-'
        for l in self.name:
            if l not in allowed_chars:
                raise ValidationError(_('Queue name must be only letters, '
                                        'digits, - or _'))

    def build_extension(self):
        self.ensure_one()
        return self.env['ir.qweb'].with_context({'lang': 'en_US'}).render(
            'asterisk_base_queues.extension', {'rec': self}).decode('utf-8')

    def _is_user_joined(self):
        for rec in self:
            rec.is_user_joined = rec.server.asterisk_user in [
                k.user for k in rec.dynamic_members]

    def apply(self):
        self.ensure_one()
        self.build_conf()
        self.server.apply_changes(notify_uid=self.env.user.id)

    def reload(self):
        self.ensure_one()
        self.server.reload_action(module='chan_sip')

    def build_conf(self):
        # Create queue settings for server if missing.
        self.env['asterisk_base_queues.settings'].check_servers_settings()
        conf_dict = {}
        for rec in self.env['asterisk_base_queues.queue'].search([]):
            # Build queues general settings
            server_queue_settings = self.env[
                'asterisk_base_queues.settings'].search(
                    [('server', '=', rec.server.id)])
            if rec.server.id not in conf_dict:
                conf_dict[rec.server.id] = self.env['ir.qweb'].with_context(
                    {'lang': 'en_US'}).render(
                    'asterisk_base_queues.queue_settings', {
                        'rec': server_queue_settings
                    }).decode('utf-8')
            # Build queues
            static_members = [k.interface for k in rec.static_members]
            conf_dict[rec.server.id] += self.env['ir.qweb'].with_context(
                {'lang': 'en_US'}).render(
                'asterisk_base_queues.queue', {
                    'rec': rec,
                    'static_members': static_members}).decode('utf-8')
        # Clear conf files first (when we remove peers)
        for c in self.env['asterisk_base.conf'].search(
                [('name', '=', 'queues_odoo.conf')]):
            c.with_context(conf_no_update=True).content = ''
        # Create conf files
        for server_id in conf_dict.keys():
            conf = self.env['asterisk_base.conf'].get_or_create(
                server_id, 'queues_odoo.conf')
            conf.content = '{}'.format(
                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('queues.conf')

    def join(self):
        for rec in self:
            if not rec.server.asterisk_user.queue_interface:
                raise ValidationError(_('You must set Queue interface first!'))
            if rec.is_user_joined:
                self.env.user.asterisk_notify(
                    'You are already in the queue!')
                continue
            data = {
                'command': 'nameko_rpc',
                'service': '{}_ami'.format(
                    rec.server.system_name),
                'method': 'send_action',
                'callback_model': 'asterisk_base_queues.queue',
                'callback_method': 'join_response',
                'args': [{
                    'Action': 'QueueAdd',
                    'Queue': rec.name,
                    'Interface': rec.server.asterisk_user.queue_interface,
                }],
                'status_notify_uid': self.env.uid,
                'pass_back': {
                    'uid': self.env.user.id,
                    'queue': rec.id,
                    'asterisk_user': rec.server.asterisk_user.id},
            }
            rec.server.send(data)

    @api.model
    def join_response(self, data):

        def _add_dynamic_operator(this_object, queue_id, asterisk_user_id, uid):
            this_object.env['asterisk_base_queues.queue_member'].create({
                'queue': queue_id,
                'user': asterisk_user_id,
                'is_static': False,
            })
            this_object.env['remote_agent.agent'].reload_view(
                uid=uid,
                model='asterisk_base_queues.queue')

        # Case 1: Result = False
        uid = data['pass_back']['uid']
        try:
            res = data['result'][0]
        except TypeError:
            self.env['res.users'].asterisk_notify(
                _('No response from agent. Please make sure it is running.'),
                uid=uid
            )
            return False
        q = self.env['asterisk_base_queues.queue'].browse(
            data['pass_back']['queue'])
        asterisk_user = self.env['asterisk_common.user'].browse(
            data['pass_back']['asterisk_user'])
        is_static_member = asterisk_user in [k.user for k in q.static_members]
        is_dynamic_member = asterisk_user in [k.user for k in q.dynamic_members]
        # Case 2: Already there and user is static
        if res.get('Response') == 'Error' and \
                'Already there' in res.get('Message'):
            # Check if it is static interface
            if is_static_member:
                self.env['res.users'].asterisk_notify(
                    _('User has been already added as static member!'),
                    uid=uid)
                return False
            # Case 3: Already there and user is dynamic
            elif is_dynamic_member:
                return True
            else:
                _add_dynamic_operator(self, q.id, asterisk_user.id, uid)
                self.env['res.users'].asterisk_notify(
                    _('User added successfully'), uid=uid)
                return True
        # Case 4: Generic Error
        elif res.get('Response') == 'Error':
            self.env['res.users'].asterisk_notify(
                _('Join queue error: {}').format(res.get('Message')),
                uid=uid
            )
            return False
        # Server returned Success but anyway let check what we have in Odoo.
        # Case 5: Success but user is static locally
        if is_static_member:
            self.env['res.users'].asterisk_notify(
                _("Apply changes to add the static user!"), uid=uid)
            return False
        elif is_dynamic_member:
            # NOthing to do here
            return True
        else:
            # Case 6: Success. Create user
            _add_dynamic_operator(self, q.id, asterisk_user.id, uid)
            self.env['res.users'].asterisk_notify(
                _('User added successfully'), uid=uid)
            return True

    def leave(self):
        for rec in self:
            if not rec.server.asterisk_user.queue_interface:
                raise ValidationError(_('You must set Queue interface first!'))
            if not rec.is_user_joined:
                self.env.user.asterisk_notify(
                    'You have already left the queue!')
                continue
            asterisk_user = rec.server.asterisk_user
            rec.dynamic_members.filtered(
                lambda rec: rec.user == asterisk_user).unlink()

    @api.model
    def leave_response(self, data):
        queue = data.get('pass_back', {}).get('queue')
        user = data.get('pass_back', {}).get('asterisk_user')
        uid = data['pass_back']['uid']
        try:
            res = data['result'][0]
        except TypeError:
            self.env['res.users'].asterisk_notify(
                _('No response from agent. Please make sure it is running.'),
                uid=uid
            )
            return False
        if res.get('Response') == 'Error':
            self.env['res.users'].asterisk_notify(
                'Leave queue error: {}'.format(res.get('Message')),
                uid=uid)
            return False
        queue_member = self.env['asterisk_base_queues.queue_member'].search(
            [('queue.id', '=', queue), ('user.id', '=', user)],
            limit=1)
        if queue_member:
            queue_member.unlink()
        self.env['remote_agent.agent'].reload_view(
            uid=uid,
            model='asterisk_base_queues.queue')
        return True

    @staticmethod
    def _update_status(agent, queue, uid, callback_method):
        data = {
            'command': 'nameko_rpc',
            'service': '{}_ami'.format(queue.server.system_name),
            'method': 'send_action',
            'callback_model': 'asterisk_base_queues.queue',
            'callback_method': callback_method,
            'args': [{
                'Action': 'QueueStatus',
                'Queue': queue.name,
            }],
            'pass_back': {
                'uid': uid,
                'queue': queue.id
            }
        }
        agent.send_agent(queue.server.system_name, data)

    def check_queue_status(self):
        for rec in self:
            self._update_status(
                agent=self.env['remote_agent.agent'],
                queue=rec,
                uid=self.env.user.id,
                callback_method='update_status_response'
            )

    def check_users_status(self):
        for rec in self:
            self._update_status(
                agent=self.env['remote_agent.agent'],
                queue=rec,
                uid=self.env.user.id,
                callback_method='update_users_response'
            )

    @api.model
    def update_status_response(self, data):
        uid = data['pass_back']['uid']
        res = data['result']
        if not res:
            self.env['res.users'].asterisk_notify(
                _('No response from agent. Please make sure it is running.'),
                uid=uid
            )
            return False
        this_queue = self.env['asterisk_base_queues.queue'].browse(
            data.get('pass_back').get('queue')).sudo()
        logger.debug("This queue: {}".format(this_queue.name))
        for event in res:
            if event.get('Event') == 'QueueParams' \
                    and event.get('Queue') == this_queue.name:
                logger.debug('Found event: {}'.format(event))
                this_queue.with_context(no_build_conf=True).write({
                    'abandoned': event.get('Abandoned'),
                    'calls': event.get('Calls'),
                    'completed': event.get('Completed'),
                    'holdtime': event.get('Holdtime'),
                    'max_call': event.get('Max'),
                    'service_level': event.get('ServiceLevel'),
                    'service_level_perf': event.get('ServiceLevelPerf'),
                    'service_level_perf2': event.get('ServiceLevelPerf2'),
                    'talk_time': event.get('TalkTime'),
                    'weight': event.get('Weight'),
                })
                self.env['remote_agent.agent'].reload_view(
                    uid=uid,
                    model='asterisk_base_queues.queue')
        return True

    @api.model
    def update_users_response(self, data):
        uid = data['pass_back']['uid']
        res = data['result']
        if not res:
            self.env['res.users'].asterisk_notify(
                _('No response from agent. Please make sure it is running.'),
                uid=uid
            )
            return False
        q_users = [e for e in res if e.get('Event') == 'QueueMember'
                   and e.get('Membership') == 'dynamic']
        try:
            queue = self.env['asterisk_base_queues.queue'].search([
                ('name', '=', q_users[0].get('Queue'))
            ])
        except IndexError:
            # No dynamic queue members found
            queue = False
            for event in res:
                if 'Queue' in event.keys():
                    queue = self.env['asterisk_base_queues.queue'].search([
                        ('name', '=', event.get('Queue'))
                    ])
                    break
            if not queue:
                return False
            for member in queue.dynamic_members:
                member.unlink()
            self.env['remote_agent.agent'].reload_view(
                uid=uid,
                model='asterisk_base_queues.queue')
            return True
        # Adding users that are in Asterisk, not in Odoo
        for event in q_users:
            member = self.env['asterisk_base_queues.queue_member'].search([
                ('interface', '=', event.get('StateInterface')),
                ('queue.name', '=', event.get('Queue'))
            ])
            logger.debug('For event {} found user {}'.format(event, member))
            if not member:
                user = self.env['asterisk_common.user'].search([
                    ('queue_interface', '=', event.get('StateInterface'))],
                    limit=1)
                self.env['asterisk_base_queues.queue_member'].create({
                    'user': user.id,
                    'queue': queue.id,
                    'is_static': event.get('Membership') == 'static'
                })
        # Removing users that are not in Asterisk, but are in Odoo
        for member in queue.dynamic_members:
            event = [e for e in q_users if e.get('StateInterface')
                     == member.interface]
            logger.debug('Found event: {}'.format(event))
            if not event:
                member.unlink()
        self.env['remote_agent.agent'].reload_view(
            uid=uid,
            model='asterisk_base_queues.queue')
        return True
