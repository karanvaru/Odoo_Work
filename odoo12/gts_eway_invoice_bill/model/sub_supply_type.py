from odoo import fields, models, api


class SubSupplyType(models.Model):
    _name = 'sub.supply.type'

    name = fields.Char(string='name')
    code = fields.Char(string='code')