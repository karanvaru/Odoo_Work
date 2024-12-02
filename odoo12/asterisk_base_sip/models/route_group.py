from odoo import fields, models, api, _
from odoo.addons.asterisk_base.utils import remove_empty_lines
from odoo.addons.asterisk_base.utils import get_default_server


class SipRouteGroup(models.Model):
    _name = 'asterisk_base_sip.route_group'
    _description = 'SIP Route Group'

    name = fields.Char(required=True)
    server = fields.Many2one(
        comodel_name='asterisk_base.server', required=True, ondelete='cascade',
        default=get_default_server)
    note = fields.Text()
    routes = fields.Many2many(comodel_name='asterisk_base_sip.route',
                              relation='asterisk_base_sip_route_groups',
                              column1='group_id', column2='route_id')
    routes_count = fields.Integer(string=_('Routes'),
                                  compute='_get_routes_count')
    include_extensions = fields.Boolean(default=True)
    is_user_default = fields.Boolean(string='Default for Users')
    is_peer_default = fields.Boolean(string='Default for Peers')
    is_trunk_default = fields.Boolean(string='Default for Trunks')

    @api.model
    def create(self, vals):
        rec = super(SipRouteGroup, self).create(vals)
        if rec and not self.env.context.get('no_build_conf'):
            self.build_conf()
        return rec

    def write(self, vals):
        res = super(SipRouteGroup, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
            # Check context of trunk
        return res

    def unlink(self):
        res = super(SipRouteGroup, self).unlink()
        if res:
            self.build_conf()
        return res

    def _get_routes_count(self):
        for rec in self:
            rec.routes_count = len(rec.routes)

    def build_conf(self):
        conf_dict = {}
        for rec in self.search([]):
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = ''
            rendered = self.env['ir.qweb'].with_context(
                {'lang': 'en_US'}).render(
                'asterisk_base_sip.route_group', {'rec': rec})
            conf_dict[rec.server.id] += '{}'.format(
                rendered.decode('utf-8'))
        # Create conf files
        for server_id in conf_dict.keys():
            # First try to get existing conf
            conf = self.env['asterisk_base.conf'].get_or_create(
                server_id, 'extensions_odoo_route_group.conf')
            # Set conf content
            conf.content = '{}'.format(
                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')
