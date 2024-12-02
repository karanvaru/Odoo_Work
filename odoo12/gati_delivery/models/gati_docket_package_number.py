from odoo import models,fields


class GatiDocketPackageNumber(models.Model):
    _name = 'gati.docket.package.number'
    _description = 'Gati Docket Package Number'

    name = fields.Integer(string="Number")
    type = fields.Selection([('docket', 'Docket'), ('packet', 'Packet')], string='Type')
    is_used = fields.Boolean(string="Is Used?")
    act_weight = fields.Float(string="Actual Weight")