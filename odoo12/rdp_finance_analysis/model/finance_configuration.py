from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class OfficeLocation(models.Model):
    _name = "office.location"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Office Location"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    code =fields.Char('Code',required = True)

class TranscationCategory(models.Model):
    _name = "transaction.category"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transaction Category"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    type_id = fields.Many2one('transaction.category.type')


class TranscationSubCategory(models.Model):
    _name = "transaction.sub.category"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transaction Sub Category"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    

class TranscationCategoryType(models.Model):
    _name = "transaction.category.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transaction Category Type"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    transaction_category_ids = fields.Many2many('transaction.category', string='Transaction Category Type',track_visibility=True)
    parent_category_id = fields.Many2one('parent.category.type')


class ParentCategoryType(models.Model):
    _name = "parent.category.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Parent Category Type"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    

