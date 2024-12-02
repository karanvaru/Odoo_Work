from odoo import models, fields, _, api

class RecordCategory(models.Model):
    _name = "record.category"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Record Category"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    record_type_ids = fields.Many2many('record.type', string='Record Type',track_visibility=True)

