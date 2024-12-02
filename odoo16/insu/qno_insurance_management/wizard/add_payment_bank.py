from odoo import models, fields, api,_
from odoo.exceptions import UserError


class AddPaymentBankWizard(models.TransientModel):
    _name = "add.payment.bank.wizard"

    bank_id = fields.Many2one(
        'payment.bank',
        string='Payment Bank',
        required=True
    )
    payment_method = fields.Char(
        string="Payment Method",
    )

    def action_approve(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        policy = self.env[active_model].browse(active_id)
        if not policy.policy_number:
            raise UserError(_("Please Add Policy Number Before Add Bank"))
        policy.update({
            'bank_id': self.bank_id.id,
            'payment_method': self.payment_method,
        })
