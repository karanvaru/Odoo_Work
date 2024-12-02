from odoo import models, fields, api


class CommissionTermCondition(models.Model):
    _name = 'commission.term.condition'
    _description = 'Commission Term Condition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
        required=True
    )
    description = fields.Html(
        string="Description"
    )
