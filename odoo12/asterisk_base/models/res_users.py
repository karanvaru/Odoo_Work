import logging
from odoo import models, fields, api, tools, registry, release, _
from odoo.exceptions import ValidationError, UserError

logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    asterisk_server = fields.One2many('asterisk_base.server',
                                      inverse_name='user')

    @api.model
    def astbase_notify(self, message, title='Asterisk Base', uid=None,
                       sticky=False, level='info'):
        if not uid:
            uid = self.env.user.id
        self.env['bus.bus'].sendone(
            'remote_agent_notification_{}'.format(uid),
            {'message': message, 'title': title,
             'level': level, 'sticky': sticky})
        return True

