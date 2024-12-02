import logging
from odoo import models, api

logger = logging.getLogger(__name__)


class AsteriskAgent(models.Model):
    _inherit = 'remote_agent.agent'
    _description = 'Asterisk Calls Agent'

    def adjust_permissions(self):
        self.ensure_one()
        super(AsteriskAgent, self).adjust_permissions()
        if not self.user.has_group(
                'asterisk_common.group_asterisk_agent'):
            service_group = self.env.ref(
                'asterisk_common.group_asterisk_agent')
            service_group.write({'users': [(4, self.user.id)]})

    def ping_asterisk_request(self):
        self.ensure_one()
        self.send({
            'command': 'nameko_rpc',
            'service': '{}_ami'.format(self.system_name),
            'method': 'ping',
            'callback_model': 'remote_agent.agent',
            'callback_method': 'ping_asterisk_reply',
            'pass_back': {'uid': self.env.uid},
        })

    @api.model
    def ping_asterisk_reply(self, data):
        if data.get('pass_back', {}).get('uid'):
            self.env['bus.bus'].sendone(
                'remote_agent_notification_{}'.format(
                    data['pass_back']['uid']), {'message': 'Asterisk Pong',
                                                'title': 'Asterisk Calls'})
        return True
