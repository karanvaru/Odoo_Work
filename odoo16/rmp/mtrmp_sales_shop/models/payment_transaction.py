from odoo import api, fields, models


class ChannelPaymentSettlementTransaction(models.Model):
    _name = "payment.settlement.transaction"
    _description = "Channel Payment Settlement Transaction"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'shop_id'

    shop_id = fields.Many2one('sale.shop', string="Shop", required=True)
    order_reference = fields.Char(string="Order Reference", required=True)
    order_id = fields.Many2one('sale.order',string="Order",)
    transaction_id = fields.Char(string='Transaction ID')
    sale_total_amount = fields.Float(string="Sale Total Amount")
    final_settlement_amount = fields.Float(stirng="Final Settlement Amount")

    status = fields.Selection([('amount_match', 'Amount  Match'),
         ('amount_match_diff', 'Amount Match Difference'),
         ('not_in_settlement', 'Not in Settlement'),
         ('not_in_erp', 'Not in ERP')],
        string="Status", compute='_compute_status')
    line_ids = fields.One2many('payment.settlement.transaction.lines', 'payment_transaction_id',)

    @api.depends("order_id", "sale_total_amount", "final_settlement_amount")
    def _compute_status(self):
        for rec in self:
            rec.status = ''
            if rec.order_id and not rec.order_id.payment_transaction_settlement_id:
                rec.status = 'not_in_settlement'
            elif rec.order_id and rec.sale_total_amount == rec.final_settlement_amount:
                rec.status = 'amount_match'
            elif rec.order_id and rec.sale_total_amount != rec.final_settlement_amount:
                rec.status = 'amount_match_diff'
            elif not rec.order_id:
                rec.status = 'not_in_erp'


class PaymentSettlementTransactionLines(models.Model):
    _name = "payment.settlement.transaction.lines"
    _description = "Payment Settlement Transaction Lines"

    payment_transaction_id = fields.Many2one('payment.settlement.transaction')
    product_id = fields.Many2one('product.product')
    type_id = fields.Many2one('payment.settlement.head.type', string="Type", required=True)
    order_reference = fields.Char(string="Order Reference", store=True)
    order_id = fields.Many2one('sale.order',string="Order")
    transaction_id = fields.Char(string='Transaction ID', related='payment_transaction_id.transaction_id')
    value = fields.Char(string="Value")
    amount = fields.Float(string="Amount")


class PaymentSettlementHeadType(models.Model):
    _name = "payment.settlement.head.type"
    _description = "Payment Settlement head Type"

    name = fields.Char(string="Name", required=True)
