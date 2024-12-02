# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    category_type = fields.Selection(
        selection=[
            ('rental', 'Rental'),
            ('service', 'Service'),
            ('parts', 'Parts'),
            ('sale', 'Sales')
        ],
        string='Category Type',
        # required=True
    )

    @api.model_create_multi
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if res.category_type:
            sequence = self.env['quote.sequence.mapping'].search([('category_type', '=', res.category_type)], limit=1)
            if sequence:
                res.update({
                    'journal_id': sequence.journal_id.id
                })
            else:
                raise ValidationError(_('Set Sequence and Journal For Category Type %s') % (res.category_type))
        return res

    @api.onchange('category_type')
    def onchange_journal(self):
        sequence = self.env['quote.sequence.mapping'].search([('category_type', '=', self.category_type)], limit=1)
        self.journal_id = sequence.journal_id.id
