# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class RentalDropOption(models.Model):
    _name = 'rental.drop.option.custom'
    _description ='Rental Product Drop Option'

    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
