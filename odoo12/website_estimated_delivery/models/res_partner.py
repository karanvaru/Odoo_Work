# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _

class res_partner(models.Model):
    _inherit = 'res.partner'
   
    partner_pincode = fields.Char(string='Pincode')
    