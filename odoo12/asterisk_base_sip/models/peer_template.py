import logging
import string
from odoo import fields, models, api, _
from odoo.addons.asterisk_base.utils import remove_empty_lines
from odoo.exceptions import ValidationError
from .peer import CHANNEL_TYPES, PEER_TYPES

logger = logging.getLogger(__name__)


class PeerTemplate(models.Model):
    _name = 'asterisk_base_sip.peer_template'
    _description = 'SIP Peer Template'
    _order = 'name'

    name = fields.Char(required=True)
    section_name = fields.Char(compute='_get_section_name')
    note = fields.Text()
    options = fields.One2many(
        'asterisk_base_sip.peer_template_option', inverse_name='template')
    common_options = fields.One2many(
        'asterisk_base_sip.peer_template_option', inverse_name='template',
        domain=[('param_type', '=', 'common')])
    individual_options = fields.One2many(
        'asterisk_base_sip.peer_template_option', inverse_name='template',
        domain=[('param_type', '=', 'individual')])
    channel_type = fields.Selection(
        CHANNEL_TYPES, required=True, string='Channel',
        default=lambda self: self._get_default_channel_type())
    peer_type = fields.Selection(
        PEER_TYPES, required=True, default='user', string='Type')
    write_protected = fields.Boolean()

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('The name must be unique !')),
    ]

    @api.model
    def create(self, vals):
        res = super(PeerTemplate, self).create(vals)
        if res:
            self.build_conf()
        return res

    def write(self, vals):
        # Check if the template is write protected.
        for rec in self:
            if rec.write_protected and 'write_protected' not in vals:
                if self.env.context.get('install_mode'):
                    logger.info(
                        'Ignoring update of %s template: write protected.',
                        rec.name)
                else:
                    raise ValidationError(
                        _('SIP template is write protected!'))
        res = super(PeerTemplate, self).write(vals)
        if res:
            self.build_conf()
        return res

    def unlink(self):
        res = super(PeerTemplate, self).unlink()
        if res:
            self.build_conf()
        return res

    @api.constrains('name')
    def _check_name(self):
        allowed_chars = string.ascii_letters + string.digits + '_- '
        for l in self.name:
            if l not in allowed_chars:
                raise ValidationError(_('Template name must be only letters, '
                                        'digits, space, - or _'))

    def _get_section_name(self):
        for rec in self:
            rec.section_name = rec.name.replace(' ', '_').lower()

    def _get_default_channel_type(self):
        if self.env.context.get('install_mode') or self.env.context.get(
                'module') == 'asterisk_base_sip':
            return 'sip'
        return self.env['asterisk_common.settings'].get_param(
            'default_sip_channel_type')

    @api.model
    def build_conf(self):
        if self.env.context.get('no_build_conf'):
            logger.debug('No_build_conf set, return.')
            return False
        templates = self.search([])
        servers = self.env['asterisk_base.server'].search([])
        for server in servers:
            conf = self.env['asterisk_base.conf'].get_or_create(
                server.id, 'sip_odoo_templates.conf')
            data = ''
            for t in templates:
                data += self.env['ir.qweb'].with_context(
                    {'lang': 'en_US'}).render(
                    'asterisk_base_sip.template', {'rec': t}).decode('utf-8')
                data += ';'
            conf.content = '{}'.format(remove_empty_lines(data))
            conf.include_from('sip.conf')
        return True


class PeerTemplateOption(models.Model):
    _name = 'asterisk_base_sip.peer_template_option'
    _description = 'SIP Peer Template'
    _rec_name = 'param'
    _order = 'sequence'

    template = fields.Many2one('asterisk_base_sip.peer_template',
                               required=True, ondelete='cascade')
    sequence = fields.Integer(requred=True, default=100)
    param = fields.Char(required=True)
    value = fields.Char(required=True)
    comment = fields.Char()
    param_type = fields.Selection(
        [('common', 'Common'), ('individual', 'Individual')], required=True,
        default='common')

    _sql_constraints = [
        ('param_uniq', 'unique (template,param)',
            _('This param is already defined!')),
    ]
