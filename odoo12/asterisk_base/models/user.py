import logging
from odoo import fields, models, api, _
from ..utils import remove_empty_lines, get_default_server
from .extension import get_next_number

logger = logging.getLogger(__name__)


class AsteriskBaseUser(models.Model):
    _inherit = 'asterisk_common.user'

    server = fields.Many2one(
        comodel_name='asterisk_base.server', required=True,
        default=get_default_server)
    agent = fields.Many2one(related='server.agent', store=True, required=False)
    extension = fields.Many2one('asterisk_base.extension')
    extension_name = fields.Char(compute='_get_extension_name')
    exten = fields.Char(
        default=get_next_number, related='extension.number',
        readonly=False, store=True)

    @api.model
    def create(self, vals):
        res = super(AsteriskBaseUser, self).create(vals)
        self.env['asterisk_base.extension'].create_extension_for_obj(res)
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk_base.extension'].build_conf()
        return res

    def write(self, vals):
        res = super(AsteriskBaseUser, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
        return res

    def unlink(self):
        for rec in self:
            if rec.extension:
                rec.extension.unlink()
        res = super(AsteriskBaseUser, self).unlink()
        if res:
            self.build_conf()
        return res

    def _get_extension_name(self):
        for rec in self:
            rec.extension_name = rec.user.name

    def build_conf(self):
        # To override.
        pass
