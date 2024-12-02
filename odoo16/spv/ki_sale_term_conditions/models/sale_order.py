# -*- coding: utf-8 -*-

from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    term_condition_id = fields.Many2one(
        'sale.term.condition',
        string='T & C Template',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        }
    )

    @api.onchange('term_condition_id')
    def _onchange_term_condition(self):
        for order in self:
            order.note = order.term_condition_id.description
