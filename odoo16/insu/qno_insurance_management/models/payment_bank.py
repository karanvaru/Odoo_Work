from odoo import api, fields, models, _


class PaymentBank(models.Model):
    _name = 'payment.bank'

    name = fields.Char(
        string="Name",
        required=True
    )
