from odoo import models, fields, api


class HelpdeskTicketInherit(models.Model):
    _inherit = "helpdesk.ticket"

    @api.multi
    def write(self, vals):
        res = super(HelpdeskTicketInherit, self).write(vals)
        if 'team_id' in vals:
            team = self.env['helpdesk.team'].browse(vals['team_id'])
            if team:
                self.user_id = team.default_assign_user_id.id

        return res
