from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    inter_branch_transfer_id = fields.Many2one(
        "inter.branch.transfer",
        string="Branch Transfer",
    )
