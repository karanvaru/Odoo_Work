from odoo import fields, api, models, _

class RecordCategoryType(models.Model):
    _name = "record.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Record Category"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)


