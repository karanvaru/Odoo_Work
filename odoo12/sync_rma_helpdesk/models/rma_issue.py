# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class RmaIssue(models.Model):
    _inherit = 'rma.issue'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', copy=False, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})

    # @api.multi
    # def done_rma(self):
    #     """
    #         Set to done RMA record
    #     """
    #     super(RmaIssue, self).done_rma()
    #     done_stage = self.env['helpdesk.stage'].search([('is_close','=',True)], limit=1)
    #     if done_stage and self.ticket_id:
    #         self.ticket_id.stage_id = done_stage.id
