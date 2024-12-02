from odoo import fields, models, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    _description = "Sales Advance Payment Invoice"

    @api.model
    def _create_invoices(self, sale_orders):
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
        if sale_orders.record_type_id:
            res.record_type_id = sale_orders.record_type_id.id
        if sale_orders.record_category_id:
            res.record_category_id = sale_orders.record_category_id.id
        return res
