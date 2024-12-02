# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'printnode.mixin', 'printnode.scenario.mixin']

    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()

        if res:
            self.print_scenarios(action='print_invoice_document_after_validation')

        return res
