from odoo import fields, models, api


class UnitQuantityCode(models.Model):
    _name = 'unit.quantity.code'

    name = fields.Char("Unit")
    code = fields.Char("Code")
    uom = fields.Many2one('uom.uom', string="Unit Of Measure")
