from odoo import fields, api, models, _

class TranscationCategory(models.Model):
    _name = "transaction.category"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transaction Category"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    # type_id = fields.Many2one('transaction.type')


