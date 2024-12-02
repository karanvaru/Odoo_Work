from odoo import api, fields, models, _


class MobileService(models.Model):
    _inherit = 'mobile.invoice'

    advance_payment_method = fields.Selection([
        ('advance', 'Deposit'),
        ('full_amount', 'Full amount')],
        string='Invoice method',
        default='advance'
    )