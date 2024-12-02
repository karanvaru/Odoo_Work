# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2024 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields,api,_
from odoo.exceptions import UserError,ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    state = fields.Selection([('draft','Draft'),('approved', 'Approved')],string="Approve Status",default="draft",tracking=True)
    
    
    def action_verify(self):
        for rec in self:
            rec.state = 'approved'
                
    def action_draft(self):
        for rec in self:
            rec.state = 'draft'



