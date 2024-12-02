from odoo import models, fields


class AccountAssetAssetInherit(models.Model):
    _inherit = 'account.asset.asset'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Line',
        readonly=True,
        copy=False,
    )


