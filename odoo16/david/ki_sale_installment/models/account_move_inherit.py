from odoo import models, fields


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    custom_sale_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        readonly=True,
        copy=False,
    )


