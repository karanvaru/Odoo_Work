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
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for invoice in self:
            if invoice.partner_id.state != 'approved' and invoice.move_type == 'in_invoice':
                raise UserError("The selected Partner Must be Approved to Post the Vendor Bill!")
            elif invoice.partner_id.state != 'approved':
                raise UserError("The selected Partner Must be Approved to Post the Invoice!")
        return super(AccountInvoice, self).action_post()