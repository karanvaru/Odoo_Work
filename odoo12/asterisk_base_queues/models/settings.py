import logging
from odoo import fields, models, api, _

logger = logging.getLogger(__name__)


class BaseQueuesSettingsTemplate(models.Model):
    _name = 'asterisk_base_queues.settings_template'
    # TODO: Remove after all upgrades.


class BaseQueuesSettings(models.Model):
    _name = 'asterisk_base_queues.settings'
    _description = 'Queue Settings Template'
    _rec_name = 'server'

    server = fields.Many2one('asterisk_base.server', required=True,
                             ondelete='cascade')
    persistentmembers = fields.Boolean(
        string=_('Persistent Members'),
        help=_("Store each dynamic member in each queue in the astdb so that "
               "when asterisk is restarted, each member will be automatically "
               "read into their recorded queues."),
        default=False
    )
    keepstats = fields.Boolean(
        string=_('Keep Stats'),
        help=_('Keep queue statistics during a reload'),
        default=False
    )
    autofill = fields.Boolean(
        string=_('Autofill Behavior'),
        help=_("If enabled, makes sure that when the waiting callers are "
               "connecting with available members in a parallel fashion until "
               "there are no more available members or waiting callers"),
        default=False
    )
    autopause = fields.Boolean(
        string=_('Autopause Behavior'),
        help=_('If enabled, will pause a queue member if they fail to answer a '
               'call'),
        default=True
    )
    maxlen = fields.Integer(
        string=_('Maximum Queue Length'),
        help=_('Maximum number of people waiting in the queue (0 = unlimited)'),
        default=0
    )
    setinterfacevar = fields.Boolean(
        string=_('Set Interface Var'),
        help=_('If set to yes, just prior to the caller being bridged with a '
               'queue member the following variables will be set: '
               'MEMBERINTERFACE, MEMBERNAME, MEMBERCALLS, MEMBERLASTCALL, '
               'MEMBERPENALTY, MEMBERDYNAMIC, MEMBERREALTIME'),
        default=False
    )
    setqueueentryvar = fields.Boolean(
        string=_('Set Queue Entry Var'),
        help=_('If set to yes, just prior to the caller being bridged with a '
               'queue member the following variables will be set: QEHOLDTIME, '
               'QEORIGINALPOS'),
        default=False
    )
    setqueuevar = fields.Boolean(
        string=_('Set Queue Var'),
        help=_('If set to yes, the following variables will be set just prior '
               'to the caller being bridged with a queue member and just prior '
               'to the caller leaving the queue: QUEUENAME, QUEUEMAX, '
               'QUEUESTRATEGY, QUEUECALLS, QUEUEHOLDTIME, QUEUECOMPLETED, '
               'QUEUEABANDONED, QUEUESRVLEVEL, QUEUESRVLEVELPERF'),
        default=False
    )
    monitor_type = fields.Selection(
        string=_('Monitor Type'),
        selection=[('monitor', _('Monitor')),
                   ('mix_monitor', _('MixMonitor'))],
        help=_('Use the old Monitor or the new MixMonitor to enable recording '
               'of queue member conversations'),
        default='mix_monitor'
    )
    monitor_format = fields.Selection(
        selection=[
            ('gsm', _('GSM')),
            ('wav', _('Wave')),
            ('wav49', _('Wave49'))
        ],
        help=_('Extension for monitor format recording'),
        default='wav'
    )
    membermacro = fields.Char(
        string=_('Member Macro'),
        help=_('If set, run this macro when connected to the queue member you '
               'can override this macro by setting the macro option on the '
               'queue application'),
        default=''
    )
    updatecdr = fields.Boolean(
        string=_('UpdateCDR behavior'),
        help=_('This option is implemented to mimic chan_agents behavior of '
               'populating CDR dstchannel field of a call with an agent name, '
               'which you can set at the login time with AddQueueMember '
               'membername parameter. '),
        default=False
    )
    shared_lastcall = fields.Boolean(
        string=_('Shared Last Call'),
        help=_('Share the lastcall and calls received status for members that '
               'are logged in multiple queues'),
        default=True
    )
    negative_penalty_invalid = fields.Boolean(
        help=_('This option will treat members with a negative penalty as '
               'logged off'),
        default=False
    )
    log_membername_as_agent = fields.Boolean(
        help=_('log_membername_as_agent will cause app_queue to log the '
               'membername rather than the interface for the ADDMEMBER and '
               'REMOVEMEMBER events when a state_interface is set.  The '
               'default value (no) maintains backward compatibility.'),
        default=False
    )
    default_ring_timeout = fields.Integer(default=15)
    default_queue_timeout = fields.Integer(defualt=300)

    @api.model
    def check_servers_settings(self):
        # Check if settings are there and create if required
        servers = self.env['asterisk_base.server'].search([])
        for server in servers:
            queues_settings = self.env['asterisk_base_queues.settings'].search(
                [('server', '=', server.id)])
            if not queues_settings:
                self.env['asterisk_base_queues.settings'].create(
                    {'server': server.id})

    @api.model
    def open_settings(self):
        self.check_servers_settings()
        servers = self.env['asterisk_base.server'].search([])
        if len(servers) > 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'asterisk_base_queues.settings',
                'name': _('Queues settings'),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'asterisk_base_queues.settings',
                'res_id': servers[0].id,
                'name': _('Queue settings'),
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }
