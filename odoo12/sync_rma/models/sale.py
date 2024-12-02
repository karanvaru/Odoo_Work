# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "SaleOrder"

    @api.multi
    def _repair_count(self):
        """
            Count RMA
        """
        for sale in self:
            count_repairs = self.env['rma.issue'].search([('associated_so', '=', sale.id)])
            sale.rma_issue_count = len(count_repairs)

    rma_issue_count = fields.Integer(compute="_repair_count", string="RMA Issue Count", copy=False)
    rma_issue_id = fields.Many2one('rma.issue', string="RMA")

    @api.multi
    def get_rma_issue(self):
        """
            Show RMA
        """
        self.ensure_one()
        issue_ids = self.env['rma.issue'].search([('associated_so', '=', self.id)])
        if issue_ids:
            form_view = self.env.ref('sync_rma.ram_issue_view_form')
            tree_view = self.env.ref('sync_rma.view_rma_tree_view')
            result  = {
                'name': 'Issue',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'rma.issue',
                'views': [(tree_view.id,'tree'), (form_view.id, 'form')],
                'domain': [('id', 'in', issue_ids.ids)],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'nodestroy': True
            }
            if len(issue_ids) > 1:
                result['domain'] = [('id', 'in', issue_ids.ids)]
            elif len(issue_ids) == 1:
                result['views'] = [(form_view.id, 'form')]
                result['res_id'] = issue_ids.ids[0]
            else:
                result = {'type': 'ir.actions.act_window_close'}
            return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "SaleOrder line"

    issue_line_id = fields.Many2one('rma.issue.line', string="RMA")
