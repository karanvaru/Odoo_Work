from odoo import fields, models, api


class HelpdeskCategoriesInherit(models.Model):
    _inherit = 'helpdesk.categories'
    _description = 'Helpdesk Categories Inherit'

    helpdesk_types_ids = fields.Many2many(
        'helpdesk.types',
        string="Type"
    )
