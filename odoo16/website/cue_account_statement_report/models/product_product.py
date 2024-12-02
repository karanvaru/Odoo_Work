from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    capex_category_id = fields.Many2one(
        'capex.category',
        string='FS Category'
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    capex_category_id = fields.Many2one(
        'capex.category',
        string='FS Category'
    )
