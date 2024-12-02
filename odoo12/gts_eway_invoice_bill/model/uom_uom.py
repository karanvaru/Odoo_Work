# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UoM(models.Model):
    _inherit = "uom.uom"

    # As per Ewaybill Rules you need to Specify Eway Bill Code foe the UOM.
    uom_mapping_id = fields.Many2one('uom.mapping', "Ewaybill Code", help="Ewaybill Master code for the UOM")
