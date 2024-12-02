# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleShop(models.Model):
    _inherit = "sale.shop"

    fees_account_mapping_ids = fields.One2many(
        'fees.account.mapping',
        'sale_shop_id',
        string="Fees Accounting Mapping"
    )

    payment_journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
    )

    #     payment_method_id = fields.Many2one(
    #         'account.payment.method',
    #         required=False,
    #         string='Payment Method'
    #     )

    payment_method_line_id = fields.Many2one(
        'account.payment.method.line',
        required=True,
        string='Payment Method'
    )

    is_create_invoice = fields.Boolean(
        string="Create Auto Invoice"
    )
    short_code = fields.Char(
        string="Short code"
    )

    @api.constrains('fees_account_mapping_ids')
    def check_type(self):
        for rec in self.fees_account_mapping_ids:
            if rec.post_type == rec.refund_post_type:
                raise UserError(_('invoice post type and refund post type should not be same!'))
