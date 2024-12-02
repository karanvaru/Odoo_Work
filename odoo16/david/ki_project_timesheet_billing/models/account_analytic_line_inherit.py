from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    is_invoice = fields.Boolean(
        string="Is Invoice",
        store=True,
    )