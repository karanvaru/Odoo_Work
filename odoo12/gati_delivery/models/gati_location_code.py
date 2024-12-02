from odoo import models,fields,api


class GatiDocketPackageNumber(models.Model):
    _name = 'gati.location.code'
    _description = 'Gati Location Code'

    name = fields.Char(string="Location")
    location_code = fields.Char(string="Location Code")
    gati_ou = fields.Char(string="Gati OU")
    service_type = fields.Char(string="Service Type")
    distance = fields.Char(string="Distance")
    pincode = fields.Char(string="Pincode")
