# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import models, fields,api,_
import random, string
class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'


    aff_visit_id = fields.One2many('affiliate.visit','act_invoice_id',string="Report")


    @api.multi
    def action_invoice_paid(self):
      to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
      if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
          raise UserError(_('Invoice must be validated in order to set it to register payment.'))
      if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
          raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
      _logger.info("-----to_pay_invoices-%r------",to_pay_invoices.aff_visit_id)
      # change affiliate visit state to paid when the invoice get paid by invoice model
      for visit in to_pay_invoices.aff_visit_id:
        if visit:
          visit.state = 'paid'
      return to_pay_invoices.write({'state': 'paid'})



   