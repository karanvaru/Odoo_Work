from odoo import models, fields, api, _


class IrCronInherit(models.Model):
    _inherit = 'ir.cron'

    reddot_specific = fields.Boolean(
        string="Is Reddot Specific?"
    )