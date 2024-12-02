import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.asterisk_base.utils import remove_empty_lines
from odoo.addons.asterisk_base.utils import get_default_server

logger = logging.getLogger(__name__)

DESTINATION_TYPES = [
    ('exten', 'Extension'),
    ('sip_trunk', 'SIP trunk'),
    ('block', 'Block'),
    ('dialplan', 'Dialplan')
]


class SipRoute(models.Model):
    _name = 'asterisk_base_sip.route'
    _description = "SIP Route"
    _order = 'sequence'

    sequence = fields.Integer(default=0, required=True)
    # A mirror of sequence to show in tree view.
    prio = fields.Integer(compute='_get_prio', store=True)
    name = fields.Char(required=True)
    icon = fields.Html(compute='_get_icon', string='T')
    lang = fields.Char(default=lambda self: self._get_default_lang(),
                       string='Language',
                       help='Two digits lang code, for example: en')
    dst = fields.Char(
        required=True,
        string='Destination number',
        help=(
            'pattern: \n'
            'X matches any digit from 0-9. \n'
            'Z matches any digit from 1-9.\n'
            'N matches any digit from 2-9.\n'
            '[1237-9] matches any digit or letter in the brackets'
            '(in this example, 1,2,3,7,8,9)\n'
            '[a-z] matches any lower case letter.\n'
            '[A-Z] matches any UPPER case letter.\n'
            '. wildcard, matches one or more characters.\n'
            '! wildcard, matches zero or more characters immediately.\n'))
    src = fields.Char(
        string='Source number (Caller ID)',
        help=(
            'pattern: \n'
            'X matches any digit from 0-9. \n'
            'Z matches any digit from 1-9.\n'
            'N matches any digit from 2-9.\n'
            '[1237-9] matches any digit or letter in the brackets'
            '(in this example, 1,2,3,7,8,9)\n'
            '[a-z] matches any lower case letter.\n'
            '[A-Z] matches any UPPER case letter.\n'
            '. wildcard, matches one or more characters.\n'
            '! wildcard, matches zero or more characters immediately.\n'))
    src_translations = fields.Many2many(
        'asterisk_base_sip.translation',
        relation='asterisk_base_sip_src_routes_translations',
        domain=[('translation_type', '=', 'src')],
        string='Source Number Translation')
    dst_translations = fields.Many2many(
        'asterisk_base_sip.translation',
        relation='asterisk_base_sip_dst_routes_translations',
        domain=[('translation_type', '=', 'dst')],
        string='Destination Number Translation')
    note = fields.Text()
    server = fields.Many2one(
        comodel_name='asterisk_base.server', required=True,
        default=get_default_server)
    groups = fields.Many2many(comodel_name='asterisk_base_sip.route_group',
                              relation='asterisk_base_sip_route_groups',
                              column2='group_id', column1='route_id',
                              required=True)
    destination_type = fields.Selection(DESTINATION_TYPES, required=True,
                                        string='Type')
    block_type = fields.Selection([
        ('busy', 'Play busy signal'),
        ('ring', 'Ring forever'),
        ('monkeys', 'Play monkeys')], default='busy')
    exten = fields.Many2one('asterisk_base.extension')
    dialplan = fields.Many2one('asterisk_base.dialplan')
    built_dialplan = fields.Text(compute='_get_dialplan', string='Dialplan')
    sip_trunk = fields.Many2one('asterisk_base_sip.peer',
                                string='SIP Trunk',
                                domain=[('peer_type', '=', 'trunk')])
    sip_trunk_dial_timeout = fields.Integer(
        string='Dial Timeout', default='60')
    sip_trunk_dial_options = fields.Char(
        string='Dial Options', default='T',
        help='[Syntax]\n'
            'Dial(Technology/Resource[&Technology2/Resource2[&...]][,timeout[,options[,URL]]])\n'
            ' - A(x): x - The file to play to the called party\n'
            ' - b([[context^]exten^]priority[(arg1[^...][^argN])]): Before initiating an\n'
            '   outgoing call, "Gosub"" to the specified location using the newly created\n'
            '    channel.  The "Gosub will be executed for each destination channel.\n'
            'Who will dare to complete the list? :-)'
    )
    recording_enabled = fields.Boolean(string='Record Calls')
    partner_lookup_enabled = fields.Boolean(
        default=True, string="Look Up Partners")
    fail_over_route = fields.Many2one('asterisk_base_sip.route')

    @api.onchange('server')
    def _reset_groups(self):
        self.groups = False

    @api.onchange('dst', 'src')
    def _upper_dst(self):
        if self.dst:
            self.dst = self.dst.upper()
        if self.src:
            self.src = self.src.upper()

    def _get_icon(self):
        for rec in self:
            if rec.destination_type == 'sip_trunk':
                rec.icon = '<span class="fa fa-phone"/>'
            elif rec.destination_type == 'dialplan':
                rec.icon = '<span class="fa fa-list-ol"/>'
            elif rec.destination_type == 'exten':
                rec.icon = '<span class="fa fa-users"/>'
            elif rec.destination_type == 'block':
                rec.icon = '<span class="fa fa-ban"/>'
            else:
                rec.icon = 'U'

    @api.depends('sequence')
    def _get_prio(self):
        for rec in self:
            rec.prio = rec.sequence

    @api.model
    def create(self, vals):
        rec = super(SipRoute, self).create(vals)
        if rec and not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base_sip.route_group'].build_conf()
            # Update SIP peers conf & ext
            self.env['asterisk_base_sip.peer'].build_conf()
        return rec

    def write(self, vals):
        res = super(SipRoute, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base_sip.route_group'].build_conf()
            # Update SIP peers conf & ext
            self.env['asterisk_base_sip.peer'].build_conf()
        return res

    def unlink(self):
        res = super(SipRoute, self).unlink()
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base_sip.route_group'].build_conf()
            # Update SIP peers conf & ext
            self.env['asterisk_base_sip.peer'].build_conf()
        return res

    def _get_dialplan(self):
        for rec in self:
            res = self.env['ir.qweb'].with_context(
                {'lang': 'en_US'}).render(
                'asterisk_base_sip.route', {'rec': rec}).decode('utf-8')
            rec.built_dialplan = remove_empty_lines(res)

    def build_conf(self):
        conf_dict = {}
        for rec in self.search([]):
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = ''
            conf_dict[rec.server.id] += rec.built_dialplan
        # Create conf files
        for server_id in conf_dict.keys():
            # First try to get existing conf
            conf = self.env['asterisk_base.conf'].get_or_create(
                server_id, 'extensions_odoo_route.conf')
            # Set conf content
            conf.content = '{}'.format(
                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')

    def _get_default_lang(self):
        try:
            return self.env.user.lang.split('_')[0]
        except Exception:
            pass

