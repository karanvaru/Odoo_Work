# -*- coding: utf-8 -*-

from odoo import models, fields

class RepairCategory(models.Model):
    _name = 'repair.category.custom'
    _description = "Repair Category"

    name = fields.Char(
        string="Name",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
