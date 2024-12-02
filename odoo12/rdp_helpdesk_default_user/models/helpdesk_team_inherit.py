from odoo import models, fields, api


class HelpdeskTeamInherit(models.Model):
    _inherit = "helpdesk.team"

    default_assign_user_id = fields.Many2one(
        'res.users',
        'Default User',
        store=True,
    )

    user_ids = fields.Many2many(
        'res.users',
        compute='compute_user_ids'
    )

    @api.depends('member_ids')
    def compute_user_ids(self):
        if self.member_ids:
            self.user_ids = self.member_ids.ids
        else:
            user = self.env['res.users'].search([])
            self.user_ids = user.ids
