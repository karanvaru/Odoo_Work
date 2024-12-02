import logging
from odoo import models, fields, api, tools, release, _
from odoo.exceptions import ValidationError, UserError

logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = 'res.users'

    remote_agent = fields.One2many('remote_agent.agent', inverse_name='user')
    asterisk_users = fields.One2many(
        'asterisk_common.user', inverse_name='user', readonly=True)
    asterisk_channels = fields.One2many(
        'asterisk_common.user_channel',
        compute='_get_asterisk_channels')
    # Primary user & system used to originate clic2dial calls.
    asterisk_user = fields.Many2one('asterisk_common.user', store=True,
                                    compute='_get_asterisk_user')

    @api.model
    def asterisk_notify(self, message, title='PBX', uid=None,
                        sticky=False, warning=False):
        if not uid:
            uid = self.env.user.id
        self.env['bus.bus'].sendone(
            'remote_agent_notification_{}'.format(uid),
            {'message': message, 'title': title,
             'sticky': sticky, 'warning': warning})

    @api.depends('asterisk_users')
    def _get_asterisk_user(self):
        for rec in self:
            found = False
            for asterisk_user in rec.asterisk_users:
                if asterisk_user.is_primary_system:
                    rec.asterisk_user = asterisk_user.id
                    found = True
                    continue
            if not found:
                rec.asterisk_user = False

    def _get_asterisk_channels(self):
        for rec in self:
            if not self.env.user.has_group(
                    'asterisk_common.group_asterisk_user'):
                rec.asterisk_channels = (6, 0, [])
            else:
                res = []
                for asterisk_user in rec.asterisk_users:
                    res.append([k.id for k in asterisk_user.channels])
                rec.asterisk_channels = (6, 0, res)
