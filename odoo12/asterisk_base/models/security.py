import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class AccessList(models.Model):
    _name = 'asterisk_base.access_list'
    _description = 'Access Lists of IP/Nets'
    _order = 'address'

    server = fields.Many2one('asterisk_base.server', required=True,
                             ondelete='cascade')
    name = fields.Char(compute='_get_name')
    address = fields.Char(required=True, index=True)
    netmask = fields.Char()
    address_type = fields.Selection([('ip', 'IP Address'), ('net', 'Network')],
                                    required=True, default='ip')
    access_type = fields.Selection([('allow', 'Allow'), ('deny', 'Deny')],
                                   required=True, default='deny')
    # Comment is required because of ipset regex parsing on Agent.
    comment = fields.Char(required=True, default='No comment')
    is_enabled = fields.Boolean(default=True, string='Enabled')

    def _get_name(self):
        for rec in self:
            rec.name = rec.address if rec.address_type == 'ip' else \
                '{}/{}'.format(rec.address, rec.netmask)

    @api.model
    def create(self, vals):
        # TODO: Handle CSV import?
        res = super(AccessList, self).create(vals)
        self.update_rules()
        return res

    def write(self, vals):
        res = super(AccessList, self).write(vals)
        self.update_rules()
        return res

    def unlink(self):
        res = super(AccessList, self).unlink()
        self.update_rules()
        return res

    @api.model
    def update_rules(self, server_id=None):
        servers_domain = [] if not server_id else [('id', '=', server_id)]
        for server in self.env['asterisk_base.server'].search(servers_domain):
            entries = self.search([('server', '=', server.id),
                                   ('is_enabled', '=', True)])
            rules = []
            for entry in entries:
                rules.append({
                    'address': entry.address,
                    'comment': entry.comment,
                    'netmask': entry.netmask,
                    'address_type': entry.address_type,
                    'access_type': entry.access_type})
            server.agent.send({
                'command': 'nameko_rpc',
                'timeout': 30,
                'service': '{}_security'.format(server.system_name),
                'method': 'update_access_rules',
                'args': (rules,),
                'status_notify_uid': self.env.uid,
            })


class Ban(models.Model):
    _name = 'asterisk_base.access_ban'
    _description = 'Access Bans'
    _order = 'address'

    server = fields.Many2one('asterisk_base.server', required=True,
                             ondelete='cascade')
    address = fields.Char(index=True, required=True)
    timeout = fields.Integer()
    packets = fields.Integer()
    bytes = fields.Integer()
    comment = fields.Char(index=True)

    @api.model
    def reload_bans(self, delay=0):
        for server in self.env['asterisk_base.server'].search([]):
            server.agent.send({
                'command': 'nameko_rpc',
                'service': '{}_security'.format(server.system_name),
                'method': 'get_banned',
                'callback_model': 'asterisk_base.access_ban',
                'callback_method': 'reload_bans_response',
                'status_notify_uid': self.env.uid,
                'pass_back': {'status_notify_uid': self.env.uid},
                'delay': delay,
            })

    @api.model
    def reload_bans_response(self, response):
        # Rely on status_notify_uid to show error message.
        if response.get('error'):
            return False
        # Get the server
        server = self.env.user.asterisk_server
        if not server:
            raise ValidationError('Server not found for account!')
            return False
        # Remove current entries
        self.search(
            [('server', '=', server.id)]).with_context(
            unlink_bans_no_sync=True).unlink()
        # Update with the result
        for row in response['result']:
            self.create({
                'server': server.id,
                'comment': row['comment'],
                'timeout': row['timeout'],
                'bytes': row['bytes'],
                'packets': row['packets'],
                'address': row['address'],
            })
        # Reload view
        self.env['remote_agent.agent'].reload_view(
            uid=response.get('pass_back', {}).get('status_notify_uid'),
            model='asterisk_base.access_ban')
        return True

    def unlink(self):
        if self.env.context.get('unlink_bans_no_sync'):
            return super(Ban, self).unlink()
        entries = {}
        # Populate entries with ip addresses
        for rec in self:
            entries.setdefault(rec.server, []).append(rec.address)
        res = super(Ban, self).unlink()
        # Now send to agent
        if res:
            for server in entries.keys():
                server.agent.send({
                    'command': 'nameko_rpc',
                    'service': '{}_security'.format(server.system_name),
                    'method': 'remove_banned_addresses',
                    'args': (entries[server],),
                    'status_notify_uid': self.env.uid})
        return res

    def add_to_whitelist(self):
        self.ensure_one()
        # Check if address is not denied
        found = self.env['asterisk_base.access_list'].search(
            [('address', '=', self.address)])
        if found:
            found.access_type = 'allow'
        # Not found, add a new one.
        else:
            self.env['asterisk_base.access_list'].create({
                'server': self.server.id,
                'address': self.address,
                'address_type': 'ip',
                'access_type': 'allow',
            })
        # Reload bans after 1 second to allow update rules to complete
        self.reload_bans(delay=1)
