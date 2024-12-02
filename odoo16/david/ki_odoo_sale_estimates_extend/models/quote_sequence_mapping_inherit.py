from odoo import fields, models, api, _


class QuoteSequencePapping(models.Model):
    _inherit = 'quote.sequence.mapping'

    estimate_sequence_id = fields.Many2one(
        'ir.sequence',
        string="Estimate Sequence",
        required=True
    )
