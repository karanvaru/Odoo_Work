from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_invoice(self):
        invoice = super(SaleOrder, self)._prepare_invoice()
        invoice.update({
            'is_custom_rental_invoice': self.is_custom_rental_quote,
        })
        return invoice


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _prepare_invoice_line(self, **optional_values):
        invoice = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        invoice.update({
            'custom_start_datetime': self.custom_start_datetime,
            'custom_end_datetime': self.custom_end_datetime,
        })
        return invoice
