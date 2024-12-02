import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.asterisk_base.utils import remove_empty_lines

logger = logging.getLogger(__name__)


class Translation(models.Model):
    _name = 'asterisk_base_sip.translation'
    _description = 'Number Translation'

    name = fields.Char(compute='_get_name', string='Description')
    translation_type = fields.Selection(
        string='Type',
        default='src',
        selection=[
            ('src', 'Source'), ('dst', 'Destination')],
        required=True)
    src = fields.Char(string='Source')
    src_user = fields.Many2one('asterisk_common.user', string='User')
    src_accountcode = fields.Char(related='src_user.accountcode')
    src_channel = fields.Char(string='Channel')
    src_replace = fields.Char(string='Replace')
    src_prefix = fields.Char(string='Prefix')
    src_skip = fields.Char(
        string='Skip',
        help=_('Skip tells Asterisk how many digits to skip off the front of the value.\n'
               'For example, if NUMBER were set to a value of 98765, then ${NUMBER:2}\n'
               'would tell Asterisk to remove the first two digits and return 765.\n'
               'If the skip field is negative, Asterisk will instead return the specified\n'
               'number of digits from the end of the number. As an example, if\n'
               'NUMBER were set to a value of 98765, then ${NUMBER:-2} would\n'
               'tell Asterisk to return the last two digits of the variable, or 65.'))
    src_skip_length = fields.Char(
        string='Length',
        help=_('Length - Asterisk will return at most the specified\n'
               'number of digits. As an example, if NUMBER were set to a value\n'
               'of 98765, then ${NUMBER:0:3} would tell Asterisk not to skip any\n'
               'characters in the beginning, but to then return only the three\n'
               'characters from that point, or 987. By that same token,\n'
               '${NUMBER:1:3} would return 876.'))
    src_result = fields.Char(compute='_get_src_result')
    # Destination number
    dst = fields.Char(string='Destination')
    dst_replace = fields.Char(string='Replace')
    dst_prefix = fields.Char(string='Prefix', default='')
    dst_skip = fields.Char(
        string='Skip',
        help=_('Skip tells Asterisk how many digits to skip off the front of the value.\n'
               'For example, if NUMBER were set to a value of 98765, then ${NUMBER:2}\n'
               'would tell Asterisk to remove the first two digits and return 765.\n'
               'If the skip field is negative, Asterisk will instead return the specified\n'
               'number of digits from the end of the number. As an example, if\n'
               'NUMBER were set to a value of 98765, then ${NUMBER:-2} would\n'
               'tell Asterisk to return the last two digits of the variable, or 65.'))
    dst_skip_length = fields.Char(
        string='Length',
        help=_('Length - Asterisk will return at most the specified\n'
               'number of digits. As an example, if NUMBER were set to a value\n'
               'of 98765, then ${NUMBER:0:3} would tell Asterisk not to skip any\n'
               'characters in the beginning, but to then return only the three\n'
               'characters from that point, or 987. By that same token,\n'
               '${NUMBER:1:3} would return 876.'))
    dst_result = fields.Char(compute='_get_dst_result')
    # Used in routes
    routes = fields.One2many('asterisk_base_sip.route',
                             compute='_get_routes')

    def _get_name(self):
        for rec in self:
            if rec.translation_type == 'src' and rec.src_user:
                rec.name = '{}: {}'.format(rec.src_user.name, rec.src_result)
            elif rec.translation_type == 'src':
                rec.name = rec.src_result
            # Now do same with dst
            else:
                rec.name = rec.dst_result

    def _get_routes(self):
        for rec in self:
            ids = []
            # Search for src translations
            ids += self.env['asterisk_base_sip.route'].search([
                ('src_translations', '=', rec.id)]).ids
            ids += self.env['asterisk_base_sip.route'].search([
                ('dst_translations', '=', rec.id)]).ids
            rec.routes = [(6, 0, ids)]

    def _get_src_result(self):
        for rec in self:
            if rec.src_replace:
                rec.src_result = rec.src_replace
            else:
                res = '{}:'.format(
                    rec.src_prefix) if rec.src_prefix else ''
                res += '${{EXTEN:{}'.format(rec.src_skip)
                if rec.src_skip_length:
                    res += ':{}'.format(rec.src_skip_legth)
                res += '}'
                rec.src_result = res

    def _get_dst_result(self):
        for rec in self:
            if rec.dst_replace:
                rec.dst_result = rec.dst_replace
            else:
                res = '{}'.format(
                    rec.dst_prefix) if rec.dst_prefix else ''
                res += '${EXTEN'
                if rec.dst_skip:
                    res += ':{}'.format(rec.dst_skip)
                if rec.dst_skip_length:
                    res += ':{}'.format(rec.dst_skip_length)
                res += '}'
                rec.dst_result = res

    @api.constrains('dst_skip', 'dst_skip_length',
                    'src_skip', 'src_skip_length')
    def _check_skip(self):
        if (self.dst_skip and not self.dst_skip.isdigit()) or (
                self.src_skip and not self.src_skip.isdigit()):
            raise ValidationError(_('skip digits must be an integer value!'))
        if (self.dst_skip_length and not self.dst_skip_length.isdigit()) or (
                self.src_skip_length and not self.src_skip_length.isdigit()):
            raise ValidationError(
                _('skip digits length must be an integer value!'))

    @api.onchange('src_skip', 'dst_skip')
    def _reset_length(self):
        if not self.src_skip:
            self.src_skip = False
            self.src_skip_length = False
        if not self.dst_skip:
            self.dst_skip = False
            self.dst_skip_length = False

    @api.model
    def create(self, vals):
        rec = super(Translation, self).create(vals)
        if rec and not self.env.context.get('no_build_conf'):
            self.env['asterisk_base_sip.route_group'].build_conf()
        return rec

    def write(self, vals):
        res = super(Translation, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.env['asterisk_base_sip.route_group'].build_conf()
        return res

    def unlink(self):
        res = super(Translation, self).unlink()
        if res and not self.env.context.get('no_build_conf'):
            self.env['asterisk_base_sip.route_group'].build_conf()
        return res
