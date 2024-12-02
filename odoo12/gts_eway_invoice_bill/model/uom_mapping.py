from odoo import fields, models, api


class UomMapping(models.Model):
    _name = 'uom.mapping'

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True)
