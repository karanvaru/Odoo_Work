import base64
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


logger = logging.getLogger(__name__)


class AsteriskConf(models.Model):
    _name = 'asterisk_base.conf'
    _description = 'Configuration Files'
    _rec_name = 'name'
    _order = 'name'

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, copy=False)
    server = fields.Many2one(comodel_name='asterisk_base.server', required=True,
                             ondelete='cascade')
    content = fields.Text()
    is_updated = fields.Boolean(string=_('Updated'))
    sync_date = fields.Datetime(readonly=True)
    sync_uid = fields.Many2one('res.users', readonly=True, string='Sync by')
    version = fields.Integer(default=1, required=True,
                             index=True, readonly=True)
    
    _sql_constraints = []

    @api.model
    def create(self, vals):
        if not self.env.context.get('conf_no_update'):
            vals['is_updated'] = True
        rec = super(AsteriskConf, self).create(vals)
        return rec

    @api.constrains('name', 'active')
    def check_name(self):
        existing = self.env[
            'asterisk_base.conf'].search(
            [('name', '=', self.name), ('server', '=', self.server.id)])
        if len(existing) > 1:
            raise ValidationError(
                'This filename already exists on this server!')

    def write(self, vals):
        if 'name' in vals:
            raise ValidationError(
                _('Rename not possible. Create a new file and copy & paste.'))
        no_update = vals.get(
            'content') and self.env.context.get('conf_no_update')
        if 'content' in vals and not no_update:
            vals['is_updated'] = True
        if 'content' in vals and 'version' not in vals and not no_update:
            # Inc version
            for rec in self:
                vals['version'] = rec.version + 1
                super(AsteriskConf, rec).write(vals)
        else:
            super(AsteriskConf, self).write(vals)
        return True

    def unlink(self):
        for rec in self:
            if not rec.active:
                super(AsteriskConf, rec).unlink()
            else:
                rec.active = False
                self.unlink_on_asterisk()
        return True

    def unlink_on_asterisk(self):
        names = self.mapped('name')
        servers = self.mapped('server')
        for server in servers:
            server.agent.send({
                'command': 'nameko_rpc',
                'service': '{}_files'.format(self.server.system_name),
                'method': 'delete_config',
                'args': [names],
                'status_notify_uid': self.env.uid,
            })        

    def refresh_button(self):
        return True

    def toggle_active(self):
        for rec in self:
            rec.write({'active': not rec.active})

    @api.model
    def get_or_create(self, server_id, name, content=''):
        # First try to get existing conf
        conf = self.env['asterisk_base.conf'].search(
            [('server', '=', server_id), ('name', '=', name)])
        if not conf:
            # Create a new one
            data = {'server': server_id, 'name': name, 'content': content}
            conf = self.env['asterisk_base.conf'].create(data)
        return conf

    def include_from(self, from_name):
        self.ensure_one()
        from_conf = self.env['asterisk_base.conf'].search(
            [('name', '=', from_name), ('server', '=', self.server.id)])
        if not from_conf or not from_conf.content:
            logger.warning(
                'File %s not found or empty, ignoring #tryinclude.', from_name)
            return
        # Check if include is already there.
        conf_basename = from_name.split('.')[0]
        include_string = '#tryinclude {}_odoo*.conf'.format(conf_basename)
        if (include_string not in from_conf.content):
            from_conf.content += '\n{}\n'.format(include_string)

    def upload_conf_button(self):
        self.upload_conf(notify_uid=self.env.uid)

    def upload_conf(self, notify_uid=None):
        # Upload conf to server
        self.ensure_one()
        self.server.agent.send({
            'command': 'nameko_rpc',
            'service': '{}_files'.format(self.server.system_name),
            'method': 'put_config',
            'args': [self.name,
                     base64.b64encode(self.content.encode()).decode()],
            'callback_method': 'upload_conf_response',
            'callback_model': 'asterisk_base.conf',
            'status_notify_uid': notify_uid,
            'pass_back': {'res_id': self.id},
            'timeout': '30',
        })

    @api.model
    def upload_conf_response(self, response):
        if response.get('error'):
            return False
        conf = self.browse(response['pass_back']['res_id'])
        conf.write({
            'is_updated': False,
            'sync_date': fields.Datetime.now(),
            'sync_uid': self.env.user.id,
        })
        return True

    def download_conf_button(self):
        self.download_conf(notify_uid=self.env.uid)

    def download_conf(self, notify_uid=None):
        self.ensure_one()
        self.server.agent.send({
            'command': 'nameko_rpc',
            'service': '{}_files'.format(self.server.system_name),
            'method': 'get_config',
            'args': [self.name],
            'callback_method': 'download_conf_response',
            'callback_model': 'asterisk_base.conf',
            'pass_back': {'res_id': self.id},
            'status_notify_uid': notify_uid,
        })

    @api.model
    def download_conf_response(self, response):
        if response.get('error'):
            return False
        conf = self.browse(response['pass_back']['res_id'])
        conf.with_context({'conf_no_update': True}).write({
            'content': base64.b64decode(
                response['result']['file_data'].encode()).decode('latin-1'),
            'sync_date': fields.Datetime.now(),
            'sync_uid': self.env.user.id})
        return True
