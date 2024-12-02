# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def count_rma(self):
        """
            Count RMA
        """
        for rec in self:
            rec.rma_count = len(rec.rma_ids) if rec.rma_ids else 0

    rma_count = fields.Integer(string="# RMA", compute='count_rma')
    rma_ids = fields.One2many('rma.issue', 'partner_id', string="RMA")

    @api.multi
    def action_view_rma(self):
        """
            Show RMA
        """
        if self.rma_ids:
            action = self.env.ref('sync_rma.rma_issue').read()[0]
            if len(self.rma_ids) > 1:
                action['domain'] = [('id', 'in', self.rma_ids.ids)]
            elif len(self.rma_ids) == 1:
                action['views'] = [(self.env.ref('sync_rma.ram_issue_view_form').id, 'form')]
                action['res_id'] = self.rma_ids.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action
