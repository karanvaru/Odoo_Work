import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class QueueMember(models.Model):
    _name = 'asterisk_base_queues.queue_member'
    _order = 'user'
    _description = 'Queue Member'

    user = fields.Many2one('asterisk_common.user', required=True,
                           ondelete='cascade')
    queue = fields.Many2one('asterisk_base_queues.queue', required=True,
                            ondelete='cascade')
    interface = fields.Char(related='user.queue_interface', readonly=True)
    is_static = fields.Boolean()

    _sql_constraints = [
        ('user_uniq', 'unique ("user",queue)',
            _('The user is already in the queue!')),
    ]

    def unlink(self):
        for rec in self:
            if rec.is_static and (not self.env.context.get('no_build_conf')):
                rec.queue.build_conf()
            else:
                rec.send_queue_leave_request()
        self.env['asterisk_base.extension'].sudo().build_conf()
        return super(QueueMember, self).unlink()

    def create(self, vals):
        rec = super(QueueMember, self).create(vals)
        for member in rec:
            if member.is_static and not self.env.context.get('no_build_conf'):
                member.queue.build_conf()
        self.env['asterisk_base.extension'].sudo().build_conf()
        return rec

    def send_queue_leave_request(self):
        for record in self:
            data = {
                'command': 'nameko_rpc',
                'service': '{}_ami'.format(
                    record.user.server.system_name),
                'method': 'send_action',
                'callback_model': 'asterisk_base_queues.queue',
                'callback_method': 'leave_response',
                'args': [{
                    'Action': 'QueueRemove',
                    'Queue': record.queue.name,
                    'Interface': record.interface
                }],
                'pass_back': {
                    'uid': self.env.user.id,
                    'queue': record.queue.id,
                    'asterisk_user': record.user.id}
            }
            self.env['remote_agent.agent'].send_agent(
                record.user.server.system_name, data
            )

    @api.constrains('user')
    def _check_user_interface(self):
        for rec in self:
            if not rec.interface:
                raise ValidationError(_('You must set Queue interface first!'))
