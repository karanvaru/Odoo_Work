from odoo import models, fields, api
import datetime

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    bank_account_no = fields.Char(string='Bank Account No', compute='compute_bank_account_number')
    jit_production_date = fields.Datetime(string='JIT / Production-1:*',required=True)
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Low'), ('2', 'High'), ('3', 'Very High')],)

    @api.depends('partner_id')
    def compute_bank_account_number(self):
        for rec in self:
            bank_accounts = rec.partner_id.bank_ids.filtered(lambda x: x.acc_number)
            if bank_accounts:
                # Filter the records based on some criteria
                filtered_accounts = bank_accounts.sorted(key=lambda x: x.id)
                # Get the first record from the filtered recordset
                bank_account = filtered_accounts[0]
                rec.bank_account_no = bank_account.acc_number
            else:
                rec.bank_account_no = False
