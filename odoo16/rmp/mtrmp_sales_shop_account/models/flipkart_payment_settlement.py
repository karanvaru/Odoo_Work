# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FlipkartPaymentSettlement(models.Model):
    _inherit = "flipkart.payment.settlement"

    @api.model
    def link_with_payment_flipkart_settlement(self):
        # journal = self.env['account.journal'].sudo().search([
        #     ('name', '=', 'Bank'),
        #     ('company_id', '=', self.env.company.id)
        # ], limit=1)
        # payment_method = self.env['account.payment.method.line'].sudo().search([
        #     ('name', '=', 'Manual')
        # ], limit=1)
        for rec in self:
            invoice = rec.order_id.invoice_ids.filtered(
                lambda i: i.state == 'posted' and i.move_type == 'out_invoice'
            )
            if invoice:
                invoice = invoice[0]
            if not invoice:
                continue

            deduction_line_list = []
            sale_amount = float(rec.total_sale_amount)
            journal = rec.order_id.sales_shop_id.payment_journal_id
            payment_method = rec.order_id.sales_shop_id.payment_method_line_id



            for shop in rec.order_id.sales_shop_id.fees_account_mapping_ids:
                deduction_line_dict = {}
                deduction_line_dict['account_id'] = shop.account_id.id
                deduction_line_dict['name'] = "{} - {}".format(rec.order_id.name, shop.account_id.name)
                field_list = []
                for field in shop.field_ids:
                    field_list.append(field.name)
                field_value = rec.sudo().read(field_list, load=False)
                field_value[0].pop("id")
                integer_values = [abs(float(num_str)) for num_str in field_value[0].values()]
                total = sum(integer_values)
                deduction_line_dict['amount'] = total
                sale_amount -= total
                deduction_line_list.append((0, 0, deduction_line_dict))

            payment = rec.env['account.payment.register'].with_context(
                active_ids=invoice.ids,
                active_model='account.move'
            ).sudo().create({
                'journal_id': journal.id,
                'payment_method_line_id': payment_method.id,
                'amount': sale_amount,
                'payment_date': fields.date.today(),
                'communication': invoice.name,
#                 'company_id': invoice.company_id.id,
                'payment_difference_handling': 'reconcile_multi_deduct',
                'deduction_ids': deduction_line_list,
            }).action_create_payments()
            flipcart_payment = self.env['account.payment'].browse(payment['res_id'])
            flipcart_payment.update({
                'flipkart_payment_settlement_id': rec.id
            })
