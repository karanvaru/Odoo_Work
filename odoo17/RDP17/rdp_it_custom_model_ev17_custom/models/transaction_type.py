from odoo import models, fields, _, api

class TranscationCategoryType(models.Model):
    _name = "transaction.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transaction Type"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    transaction_category_ids = fields.Many2many('transaction.category', string='Transaction Category',track_visibility=True)
