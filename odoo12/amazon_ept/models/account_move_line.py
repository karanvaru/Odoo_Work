from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    seller_id = fields.Many2one("amazon.seller.ept", "Seller")
    amazon_instance_id = fields.Many2one("amazon.instance.ept", string="Amazon Instance")
