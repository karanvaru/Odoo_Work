from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = "project.project"

    dealer_id = fields.Many2one(
        'res.partner',
        string="Dealer",
        copy=False
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group('ki_spv_project_extension.group_project_dealer'):
            args += [('dealer_id', '=', self.env.user.partner_id.id)]
        return super(ProjectProject, self).search(args, offset, limit, order, count)

