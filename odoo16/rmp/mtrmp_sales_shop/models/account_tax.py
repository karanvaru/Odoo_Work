from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    tags_ids = fields.One2many('account.tax.tag', 'tax_id')
    alternate_tax_id = fields.Many2one('account.tax', string="Alternate Tax")

class AccountTaxTag(models.Model):
    _name = "account.tax.tag"
    _description = "Account Tax Tag"

    tax_id = fields.Many2one('account.tax')
    name = fields.Char(string="Name",required=True)
