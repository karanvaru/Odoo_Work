import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from ..utils import remove_empty_lines, is_debug_mode_enabled
from ..utils import render_conf_template, get_default_server


logger = logging.getLogger(__name__)

DIALPLAN_TYPES = [
    ('standard', 'Standard'),
    ('service', 'Service')
]


# TODO: Remove this model after updates.
class DialplanVariable(models.Model):
    _name = 'asterisk_base.dialplan_variable'
    _description = 'Dialplan Variables'

    name = fields.Char(required=True)
    value = fields.Char()
    is_dynamic = fields.Boolean(string='Dynamic?')


class Dialplan(models.Model):
    _name = 'asterisk_base.dialplan'
    _description = "Dialplan"

    dialplan_type = fields.Selection(DIALPLAN_TYPES, required=True,
                                     default='standard', string='Type')
    server = fields.Many2one(
        comodel_name='asterisk_base.server', required=True,
        default=get_default_server)
    name = fields.Char()  # TODO: required=True)
    extension = fields.Many2one('asterisk_base.extension')
    exten = fields.Char(related='extension.number', readonly=False)
    note = fields.Text()
    lines = fields.One2many(
        'asterisk_base.dialplan_line', inverse_name='dialplan')
    is_custom = fields.Boolean(string="Custom")
    is_protected = fields.Boolean(string='Read Only')
    custom_dialplan = fields.Text(string='Dialplan')
    custom_context = fields.Char(string='Entry Context')
    context = fields.Char(compute='_get_context')
    dialplan = fields.Text(compute='_get_dialplan', inverse='_set_dialplan')
    # TODO: Remove after updates.
    variables = fields.Many2many('asterisk_base.dialplan_variable')

    _sql_constraints = [
        ('custom_context_uniq', 'unique (custom_context)',
            _('The entry context must be unique !')),
    ]

    @api.model
    def create(self, vals):
        # We do not allow edit custom dialplan on create because we need to
        # give user a hint about entry context.
        if vals.get('is_custom') and vals.get('custom_context'):
            vals['dialplan'] = ';\n[{}] ; {}'.format(
                vals['custom_context'], vals['name'])
        res = super(Dialplan, self).create(vals)
        if res and not self.env.context.get('no_build_conf'):
            if res.exten:
                self.env['asterisk_base.extension'].create_extension_for_obj(
                    res, exten_type=res.dialplan_type)
            self.build_conf()
        return res

    def write(self, vals):
        if 'exten' in vals:
            for rec in self:
                rec.extension and rec.extension.unlink()
        res = super(Dialplan, self).write(vals)
        if ('install_mode' not in self.env.context and
                not is_debug_mode_enabled()):
            for rec in self:
                if rec.is_protected:
                    raise ValidationError(
                        _('Activate developer mode to change '
                          'a protected dialplan!'))
        if 'exten' in vals:
            for rec in self:
                if rec.exten:
                    model = self.env['asterisk_base.extension']
                    model.create_extension_for_obj(rec)
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base.extension'].build_conf()
        return res

    def unlink(self):
        for rec in self:
            # Check if it is a read only dialplan
            if rec.is_protected and ('install_mode' not in self.env.context and
                    not is_debug_mode_enabled()):
                raise ValidationError(
                    _('Activate developer mode to delete a '
                      'protected dialplan!'))
            if rec.extension:
                rec.extension.unlink()
        res = super(Dialplan, self).unlink()
        if res:
            self.build_conf()
            self.env['asterisk_base.extension'].build_conf()
        return res

    def build_extension(self):
        # Render extension from template
        self.ensure_one()
        return self.env['ir.qweb'].with_context({'lang': 'en_US'}).render(
            'asterisk_base.dialplan_extension',
            {'rec': self}).decode('utf-8')

    def build_dialplan(self):
        self.ensure_one()
        if self.is_custom:
            return '{}\n'.format(self.custom_dialplan)
        else:
            ret_lines = [
                ';',
                '[dialplan-{}]; {}'.format(self.id, self.name)
            ]
            prio = 1
            for line in self.lines:
                if not line.label:
                    ret_lines.append('exten => {},{},{}({})'.format(
                        self.exten, prio, line.app,
                        line.app_data if line.app_data else ''))
                else:
                    ret_lines.append('exten => {},{}({}),{}({})'.format(
                        self.exten, prio, line.label, line.app,
                        line.app_data if line.app_data else ''))
                prio += 1
            ret_lines.append('\n')
            return '\n'.join(ret_lines)

    @api.model
    def build_conf(self):
        dialplans = self.env['asterisk_base.dialplan'].search([], order='id')
        for server in dialplans.mapped('server'):
            conf_data = ''
            for dp in dialplans.filtered(lambda r: r.server == server):
                conf_data += dp.build_dialplan() or ''
                conf_data += '\n\n'
                conf_data = render_conf_template(conf_data, dp)
            conf = self.env['asterisk_base.conf'].get_or_create(
                server.id, 'extensions_odoo_dialplan.conf')
            conf.content = '{}'.format(
                remove_empty_lines(conf_data))
            conf.include_from('extensions.conf')

    @api.onchange('lines', 'is_custom', 'custom_context')
    def _get_dialplan(self):
        for rec in self:
            rec.dialplan = rec.build_dialplan()

    def _set_dialplan(self):
        for rec in self:
            rec.custom_dialplan = rec.dialplan

    def _get_context(self):
        for rec in self:
            if not rec.is_custom:
                rec.context = 'dialplan-{}'.format(rec.id)
            else:
                rec.context = rec.custom_context


class DialplanLine(models.Model):
    _name = 'asterisk_base.dialplan_line'
    _order = 'sequence'
    _description = "Dialplan line"

    name = fields.Char(compute='_get_name')
    dialplan = fields.Many2one('asterisk_base.dialplan')
    exten = fields.Char()
    sequence = fields.Integer()
    app = fields.Char()
    app_data = fields.Char()
    label = fields.Char()

    def _get_name(self):
        for rec in self:
            rec.name = '{}({})'.format(rec.app, rec.app_data or '')
