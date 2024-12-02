from odoo import models, fields, api


class promotion_keyword(models.Model):
    _name = "amazon.promotion.keyword.ept"
    _description = 'amazon.promotion.keyword.ept'

    name = fields.Char("Name", required=True)
