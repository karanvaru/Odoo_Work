# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class Repair(models.Model):
    _inherit = 'repair.order'
    _description = 'Repair order'

    @api.multi
    def _rma_count(self):
        """
            Count RMA
        """
        for repair in self:
            repair.rma_issue_count = len(repair.issue_id) if repair.issue_id else 0

    rma_issue_count = fields.Integer(compute="_rma_count", string="RMA Issue Count", copy=False)
    issue_id = fields.Many2one('rma.issue', string='RMA')
    issue_line_id = fields.Many2one('rma.issue.line', string="Issue Line")

    @api.multi
    def get_rma_issue(self):
        """
            Show RMA
        """
        self.ensure_one()
        action = self.env.ref('sync_rma.rma_issue').read()[0]
        if len(self.issue_id) > 1:
            action['domain'] = [('id', '=', self.issue_id.id)]
        elif len(self.issue_id) == 1:
            action['views'] = [(self.env.ref('sync_rma.ram_issue_view_form').id, 'form')]
            action['res_id'] = self.issue_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
