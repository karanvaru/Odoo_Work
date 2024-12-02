from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gati_cust_vend_code = fields.Char(string="Gati Customer/Vendor Code", help="Technical field that will use while requesting shipment to Gati.")
