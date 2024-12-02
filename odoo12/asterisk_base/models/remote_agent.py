import logging
from odoo import models, api

logger = logging.getLogger(__name__)


class AsteriskBaseAgent(models.Model):
    _inherit = 'remote_agent.agent'
    _description = 'Asterisk Base Agent'

    def adjust_permissions(self):
        self.ensure_one()
        super(AsteriskBaseAgent, self).adjust_permissions()
        if not self.user.has_group(
                'asterisk_common.group_asterisk_agent'):
            service_group = self.env.ref(
                'asterisk_common.group_asterisk_agent')
            service_group.write({'users': [(4, self.user.id)]})
