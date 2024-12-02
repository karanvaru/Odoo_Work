from odoo import api, fields, _, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        related='invoice_id.record_type_id',
        store=True,
        copy=False
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        related='invoice_id.record_category_id',
        store=True,
        copy=False
    )
