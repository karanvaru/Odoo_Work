# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def invoice_refund(self):
        context = dict(self._context or {})
        if context.get("active_model") == "rma.rma":
            rma_obj = self.env["rma.rma"].browse(context.get("params", {}).get("id", False))
            if rma_obj:
                if not rma_obj.order_id.invoice_ids :
                    raise Warning('Invoice can not be refund because Order "' + rma_obj.order_id.name+ '" has no invoice.')
                only_out_invoice_ids = []
                for inv in rma_obj.order_id.invoice_ids:
                    if inv.type == "out_invoice":
                        only_out_invoice_ids.append(inv.id)
                only_out_invoice_ids.sort()
                context["active_id"] = only_out_invoice_ids[0]
                context["active_ids"] = only_out_invoice_ids
                context["active_model"] = "account.invoice"
                context["rma_id"] = rma_obj.id

        if not context.get("active_id"):
            raise osv.except_osv(_('Warning!'), _('Order %s has no invoice to refund.'(
                self.env["rma.rma"].browse(context.get("rma_id", False)))))
        return super(AccountInvoiceRefund, self.with_context(context)).invoice_refund()
