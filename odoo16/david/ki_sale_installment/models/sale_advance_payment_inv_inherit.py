# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    advance_payment_method = fields.Selection(
        selection_add=[
            ('installment_invoice', 'Create Installment Invoice'),
        ],
        ondelete={'installment_invoice': 'cascade'},
    )

    def _create_invoices(self, sale_orders):
        res = super(SaleAdvancePaymentInvInherit, self)._create_invoices(sale_orders)
        if self.advance_payment_method == "installment_invoice":
            if sale_orders.sale_installment_plan_id:
                advance = sale_orders.amount_total * sale_orders.sale_installment_plan_id.advance / 100
                res.update({
                    'invoice_date': fields.date.today(),
                    'custom_sale_id': sale_orders.id,
                })
                for rec in res.invoice_line_ids:
                    rec.update({
                        'product_id': sale_orders.sale_installment_plan_id.product_id.id,
                        'product_uom_id': sale_orders.sale_installment_plan_id.product_id.uom_id.id,
                        'price_unit': advance,
                        'name': "Advance %s " %(str(sale_orders.sale_installment_plan_id.advance) + '%' )
                    })

                remain_val = sale_orders.amount_total - advance
                remain_val_div = remain_val / sale_orders.sale_installment_plan_id.installment_number
                count = 1
                for inv in range(sale_orders.sale_installment_plan_id.installment_number):
                    move_dict = sale_orders._prepare_invoice()
                    invoice = self.env['account.move'].create(move_dict)
                    date_inv = fields.date.today() + relativedelta(months=inv + 1)
                    invoice.update({
                        'invoice_date': date_inv,
                        'custom_sale_id': sale_orders.id,
                    })
                    res.invoice_line_ids.copy(default={'move_id': invoice.id,
                                                       'price_unit': remain_val_div,
                                                       'product_id': sale_orders.sale_installment_plan_id.product_id.id,
                                                       'product_uom_id': sale_orders.sale_installment_plan_id.product_id.uom_id.id,
                                                       'name': "Installment No: - %s" %(count)
                                                       })
                    count += 1
                account_assents = self.env['account.asset.asset']
                for assents in sale_orders.order_line:
                    if not assents.is_downpayment:
                        if assents.product_id.asset_category_id:
                            account_assents.create({
                                'name': assents.product_id.name,
                                'category_id': assents.product_id.asset_category_id.id,
                                'value': assents.price_subtotal,
                                'sale_line_id': assents.id,
                            })
                        else:
                            raise ValidationError("Add asset type on product before creating invoice!")
        return res
