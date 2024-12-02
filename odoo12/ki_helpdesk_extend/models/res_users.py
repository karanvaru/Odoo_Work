from odoo import models, fields, api


class RES_users_helpdesk(models.Model):
    _inherit = 'res.users'

    has_asc_portal_access = fields.Boolean(
        "ASC Portal Access",
        compute="compute_asc_portal_access",
        inverse="inverse_asc_portal_access",
        readonly=False,
        store=False
    )

    @api.depends('groups_id')
    def compute_asc_portal_access(self):
        for rec in self:
            if rec.has_group('ki_helpdesk_extend.group_asc_portal_access') and rec.has_group('base.group_portal'):
                rec.has_asc_portal_access = True
            else:
                rec.has_asc_portal_access = False

    @api.depends('groups_id')
    def inverse_asc_portal_access(self):
        for rec in self:
            if rec.has_asc_portal_access and rec.has_group('base.group_portal'):
                rec.write({
                    'groups_id': [(4, self.env.ref('ki_helpdesk_extend.group_asc_portal_access').id)]
                })
            else:
                rec.write({
                    'groups_id': [(3, self.env.ref('ki_helpdesk_extend.group_asc_portal_access').id)]
                })