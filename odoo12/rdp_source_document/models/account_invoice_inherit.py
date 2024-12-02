from odoo import fields, models, api, _

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        invoice = super(AccountInvoiceInherit, self).action_move_create()
        if self.move_id:
            self.move_id.update({
                'custom_source_document': self.origin
            })

        return invoice