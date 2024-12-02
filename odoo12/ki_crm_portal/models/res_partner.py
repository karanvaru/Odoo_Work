from odoo import models,fields,api

class Res_P(models.Model):
    _inherit ='res.partner'

    is_gem_cust = fields.Boolean(
        "Is GeM Customer",
        default = False
    )