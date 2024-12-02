# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class QuoteSequenceMapping(models.Model):
    _name = "quote.sequence.mapping"

    category_type = fields.Selection(
        selection=[
            ('rental', 'Rental'),
            ('service', 'Service'),
            ('parts', 'Parts'),
            ('sale', 'Sales')
        ],
        string='Category Type',
        required=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        string="Journal",
        domain="[('type', '=', 'sale'), ('category_type', '=', category_type)]",
        required=True
    )
    sequence_id = fields.Many2one(
        'ir.sequence',
        string="Sequence",
        required=True
    )

    @api.model_create_multi
    def create(self, vals):
        res = super(QuoteSequenceMapping, self).create(vals)
        cat_type = self.env['quote.sequence.mapping'].search_count([('category_type', '=', res.category_type)])
        if cat_type > 1:
            raise ValidationError(_("Category Type Should Be Unique"))
        return res
