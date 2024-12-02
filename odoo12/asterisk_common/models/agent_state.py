from datetime import datetime, timedelta
import logging
from odoo import models, fields, api

logger = logging.getLogger(__name__)

STATES = [
    ('offline', 'Offline'),
    ('online', 'Online'),
]


class AgentState(models.Model):
    _name = 'remote_agent.agent_state'
    _description = 'Agent State'
    _order = 'id desc'
    _rec_name = 'create_date'

    create_date = fields.Datetime(index=True)
    agent = fields.Many2one('remote_agent.agent', required=True,
                            ondelete='cascade')
    state = fields.Selection(STATES, required=True, index=True)
    note = fields.Text()


    @api.model
    def vacuum(self, days=15):
        now = datetime.now() - timedelta(days=days)
        states = self.search(
            [('create_date', '<', fields.Datetime.to_string(now))])
        states.unlink()
