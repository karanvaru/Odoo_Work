from odoo import api, fields, models, _


class ChecklistNameLine(models.Model):
    _inherit = 'checklist.name.line'

    comment = fields.Text(
        string="Comments",
    )
