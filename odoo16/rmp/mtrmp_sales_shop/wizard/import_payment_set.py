from odoo import models, fields, api, _
import base64
import requests
import xlrd
import io
from datetime import datetime
from odoo.exceptions import ValidationError


class ImportPaymentSettlement(models.TransientModel):
    _name = "import.payment.settlement"
    _description = "Import Payment Settlement"

    file_name = fields.Binary(
        string="File Name",
    )

    @api.model
    def default_get(self, fields):
        res = super(ImportPaymentSettlement, self).default_get(fields)

        active_model = self._context.get('active_model')
        if active_model == 'channel.payment.settlement':
            active_id = self.env.context.get('active_id', [])
            record = self.env[active_model].browse(active_id)
            res.update({
                'file_name': record.file_name
            })
        return res
    
    def import_payment_settlement(self):
        active_id = self._context.get('active_id', False)
        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodestring(self.file_name)
            )
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        header_list = []
        for row in range(number_of_rows):
            if row == 1:
                row_vals = sheet.row_values(row)
                header_list.append(row_vals)
            if row >= 3:
                row_vals = sheet.row_values(row)
                number = row_vals[header_list[0].index('Sub Order No')].split('_')
                sub = number[0]
                vals = {
                    'payment_settlement_id': active_id,
                    'order_reference': sub,
                    'product_name': row_vals[header_list[0].index('Product Name')],
                    'sku': row_vals[header_list[0].index('Supplier SKU')],
                    'live_orders_status': row_vals[header_list[0].index('Live Order Status')],
                    'product_gst': row_vals[header_list[0].index('Product GST %')],
                    'listing_price': row_vals[header_list[0].index('Listing Price (Incl. GST & Commission)')],
                    'quantity': row_vals[header_list[0].index('Quantity')],
                    'transaction_id': row_vals[header_list[0].index('Transaction ID')],
                    # 'payment_date': row_vals[header_list[0].index('Payment Date')],
                    # 'payment_date': datetime.strptime(int(row_vals[header_list[0].index('Payment Date'))], "%d %b, %Y"),
                    'final_amount': row_vals[header_list[0].index('Final Settlement Amount')],
                    'price_types': row_vals[header_list[0].index('Price type')],
                    'total_sale_amount': row_vals[header_list[0].index('Total Sale Amount (Incl. Commission & GST)')],
                    'sale_return_amount': row_vals[header_list[0].index('Sale Return Amount (Incl. GST)')],
                    'shipping_revenue': row_vals[header_list[0].index('Shipping Revenue (Incl. GST)')],
                    'shipping_return_amount': row_vals[header_list[0].index('Shipping Return Amount (Incl. GST)')],
                    'return_premium': row_vals[header_list[0].index('Return premium (incl GST)')],
                    'return_premium_incl_gst': row_vals[header_list[0].index('Return premium (incl GST) of Return')],
                    'commission_percentage': row_vals[header_list[0].index('Meesho Commission Percentage')],
                    'commission_amount': row_vals[header_list[0].index('Meesho Commission (Excl. GST)')],
                    'return_shipping_charge': row_vals[header_list[0].index('Return Shipping Charge (Excl. GST)')],
                    'gst_compensation': row_vals[header_list[0].index('GST Compensation (PRP Shipping)')],
                    'shipping_charge': row_vals[header_list[0].index('Shipping Charge (Excl. GST)')],
                    'support_service_charge': row_vals[
                        header_list[0].index('Other Support Service Charges (Excl. GST)')],
                    'support_service_charge_waivers': row_vals[
                        header_list[0].index('Other Support Service Charges Waivers (Excl. GST)')],
                    'net_support_service_charge': row_vals[
                        header_list[0].index('Net Other Support Service Charges (Excl. GST)')],
                    'igst_on_meesho_commision': row_vals[header_list[0].index('IGST on Meesho Commission')],
                    'igst_on_shipping_charge': row_vals[header_list[0].index('IGST on Shipping Charge')],
                    'igst_on_return_shipping_charge': row_vals[header_list[0].index('IGST on Return Shipping Charge')],
                    'igst_on_net_other_shipping_charge': row_vals[
                        header_list[0].index('IGST on Net Other Support Service Charges')],
                    'tcs': row_vals[header_list[0].index('TCS (IGST)')],
                    'tcs_cgst_sgst': row_vals[header_list[0].index('TCS (CGST + SGST)')],
                    'tds_rate': row_vals[header_list[0].index('TDS Rate')],
                    'tds_amount': row_vals[header_list[0].index('TDS Amount')],
                    'compensation': row_vals[header_list[0].index('Compensation (No GST)')],
                    'recovery': row_vals[header_list[0].index('Recovery (No GST)')]
                }
                print("vals____________",vals)
                self.env['channel.payment.settlement.lines'].create(vals)
        payment_set_id = self.env['channel.payment.settlement'].browse(active_id)
        payment_set_id.update({
            'user_id': self.env.user,
            'import_date': datetime.today(),
        })
