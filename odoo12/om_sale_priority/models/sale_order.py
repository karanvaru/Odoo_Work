# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class sale_order(models.Model):
    _inherit = "sale.order"
    
    priority = fields.Selection([('0','Low'),('1','Medium'),('2','High'),('3','Very High')], 
                                    string='Priority', 
                                    default='0')
                                    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
