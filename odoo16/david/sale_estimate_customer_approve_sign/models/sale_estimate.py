# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class AccountAnalyticLine(models.Model):
    _inherit = 'sale.estimate'
    
    custom_signature = fields.Binary(
        string='Signature',
        copy=False,
        readonly = True
    )
    custom_signed_on = fields.Datetime(
        string='Sign On',
        copy=False,
        readonly = True
    )
    custom_signed_by = fields.Char(
        string='Sign By',
        copy=False,
        readonly = True
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: