from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group('ki_spv_project_extension.group_project_dealer'):
            args += [('project_id.dealer_id','=',self.env.user.partner_id.id)]
        return super(ProjectTask, self).search(args, offset, limit, order, count)

