import string
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, MissingError
from ..utils import remove_empty_lines

logger = logging.getLogger(__name__)

EXTEN_TYPES = [
    ('standard', 'Standard'),
    ('service', 'Service')
]


def get_next_number(cls):
    def _get_last_number():
        # TODO: override in Asterisk Base to search for all recs in asterisk_base.extension
        start = cls.env[
            'asterisk_common.settings'].get_param('default_exten_start')
        length = cls.env[
            'asterisk_common.settings'].get_param('default_exten_length')
        extens = [
            k['exten'] for k in cls.env['asterisk_common.user'].search_read(
                [], fields={'exten'}) if
            len(k['exten']) == length]
        if not extens:
            return start
        else:
            extens.sort()
            return int(extens[-1])
    last = _get_last_number()
    while True:
        if not cls.search_count([('exten', '=', last)]):
            return last
        else:
            last += 1


class Extension(models.Model):
    _name = 'asterisk_base.extension'
    _order = 'number'
    _description = "Extension"

    name = fields.Char(compute='_get_name')
    exten_type = fields.Selection(
        EXTEN_TYPES, required=True, default='standard')
    server = fields.Many2one(comodel_name='asterisk_base.server',
                             required=True, ondelete='cascade')
    number = fields.Char(required=True, string='Exten')
    app = fields.Char(required=True, readonly=True)
    model = fields.Char(required=True, readonly=True)
    app_model = fields.Char(compute='_get_app_model')
    obj_id = fields.Integer(required=True, readonly=True)
    record_calls = fields.Boolean()
    icon = fields.Html(compute='_get_icon', string='T')

    def _get_icon(self):
        for rec in self:
            if rec.app_model == 'asterisk_common.user':
                rec.icon = '<span class="fa fa-user"/>'
            elif rec.app_model == 'asterisk_base_sip.peer':
                rec.icon = '<span class="fa fa-phone"/>'
            elif rec.app_model == 'asterisk_base.dialplan':
                rec.icon = '<span class="fa fa-list-ol"/>'
            elif rec.app_model == 'asterisk_base_queues.queue':
                rec.icon = '<span class="fa fa-users"/>'
            else:
                rec.icon = 'U'

    @api.model
    def create(self, vals):
        res = super(Extension, self).create(vals)
        if res:
            self.build_conf()
        return res

    def write(self, vals):
        res = super(Extension, self).write(vals)
        if res:
            self.build_conf()
        return res

    def unlink(self):
        res = super(Extension, self).unlink()
        if res:
            self.build_conf()
        return res

    @api.model
    def create_extension_for_obj(self, obj, exten_type='standard'):
        app, model = obj._name.split('.')
        extension = self.with_context(no_build_conf=True).create({
            'server': obj.server.id,
            'app': app,
            'model': model,
            'number': obj.exten,
            'obj_id': obj.id,
            'exten_type': exten_type,
        })
        obj.extension = extension.id
        self.build_conf()

    @api.constrains('number')
    def _check_number(self):
        if not self.number:
            return
        # Check for existance
        count = self.env['asterisk_base.extension'].search_count(
            [('server', '=', self.server.id), ('number', '=', self.number)])
        if count > 1:
            logger.error('Extension number %s is already used.', self.number)
            raise ValidationError(_('This extension number is already used!'))

    def _get_app_model(self):
        for rec in self:
            rec.app_model = '{}.{}'.format(rec.app, rec.model)

    def get_object(self):
        self.ensure_one()
        try:
            return self.env[self.app_model].browse(self.obj_id)
        except KeyError:
            return False

    def _get_name(self):
        for rec in self:
            try:
                obj = self.env[rec.app_model].browse(rec.obj_id)
                rec.name = getattr(
                    obj, 'extension_name', getattr(
                        obj, obj._rec_name))
            except (KeyError, MissingError):
                name = '{} @ {}'.format(rec.number, rec.model)
                if not (
                        self.env.context.get('install_mode') or
                        self.env.context.get('module')):
                    logger.warning('EXTENSION NAME ERROR FOR %s:', name)
                rec.name = name

    @api.model
    def build_conf(self):
        if self.env.context.get('no_build_conf'):
            logger.debug('Extension no_build_conf set, return.')
            return False
        extensions = self.env['asterisk_base.extension'].search([])
        servers = extensions.mapped('server')
        for server in servers:
            conf = self.env['asterisk_base.conf'].get_or_create(
                server.id, 'extensions_odoo.conf')
            dialplan = '[odoo-extensions]\n'
            for ext in extensions.filtered(lambda r: r.server == server):
                dialplan += self.env['ir.qweb'].with_context({'lang':'en_US'}).render(
                    'asterisk_base.extension', {'rec': ext}).decode('utf-8')
                obj = ext.get_object()
                if not obj:
                    if not self.env.context.get('install_mode'):
                        logger.warning('OMITTING EXT CONF %s@%s, NOT READY',
                            ext.number, ext.app_model)
                    continue
                try:
                    if hasattr(obj, 'build_extension'):
                        dialplan += obj.build_extension()
                        dialplan += ';'
                except Exception:
                    logger.exception('Build extension error:')
            conf.content = '{}'.format(remove_empty_lines(dialplan))
            conf.include_from('extensions.conf')
        return True

    def open_extension(self, view_id=None):
        self.ensure_one()
        res = {
            'type': 'ir.actions.act_window',
            'res_model': self.app_model,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'res_id': self.obj_id,
        }
        if view_id:
            res['view_id'] = view_id
        return res
