from odoo import api, fields, models
import base64
import requests
import xlrd
import io
from datetime import datetime
from odoo.exceptions import ValidationError


class ChannelPaymentSettlement(models.TransientModel):
    _name = "channel.payment.settlement"
    _description = "Channel Payment Settlement"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'shop_id'

    shop_id = fields.Many2one('sale.shop', string="Shop",required=True)
    import_date = fields.Datetime(string='Import Date', tracking=True)
    user_id = fields.Many2one('res.users', string="User", tracking=True)
    line_ids = fields.One2many('channel.payment.settlement.lines', 'payment_settlement_id')
    file_name = fields.Binary(string="File Name", required=False)

    def download_sample(self):
        self.ensure_one()
        lines_id = self.env['attachment.sample.file'].search([
            ('shop_id', '=', self.shop_id.id),
            ('file_type', '=', 'payment_settlement')
        ], limit=1)
        if lines_id.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': "/web/content/?model=ir.attachment&id=" + str(
                    lines_id.attachment_id.id) + "&filename_field=name&field=datas&download=true&name=" + lines_id.attachment_id.name
            }

    def action_preview(self):
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
                number = row_vals[header_list[0].index('Order ID')]
                sub = number
                sale_order = self.env['sale.order'].search([('client_order_ref','=',sub),('shop_id','=',
                                                                                          self.shop_id.id)])
                order = row_vals[header_list[0].index('Order Date')]
                order_date = xlrd.xldate_as_tuple(order, workbook.datemode)
                order_date = str(order_date[0]) + '/' + str(order_date[1]) + '/' + str(order_date[2]) + ' ' + str(
                    order_date[3]) + ":" + str(order_date[4]) + ':' + str(order_date[5])
                order_date = datetime.strptime(order_date, "%Y/%m/%d %H:%M:%S")
                dispatch = row_vals[header_list[0].index('Dispatch Date')]
                dispatch_date = xlrd.xldate_as_tuple(dispatch, workbook.datemode)
                dispatch_date = str(dispatch_date[0]) + '/' + str(dispatch_date[1]) + '/' + str(dispatch_date[2])
                dispatch_date = datetime.strptime(dispatch_date, "%Y/%m/%d")
                payment = row_vals[header_list[0].index('Payment Date')]
                payment_date = xlrd.xldate_as_tuple(payment, workbook.datemode)
                payment_date = str(payment_date[0]) + '/' + str(payment_date[1]) + '/' + str(payment_date[2])
                payment_date = datetime.strptime(payment_date, "%Y/%m/%d")
                vals = {
                    'payment_settlement_id': self.id,
                    'order_reference': sub,
                    'order_id' : sale_order and sale_order.id,
                    'order_date': order_date,
                    'dispatch_date': dispatch_date,
                    'product_name': row_vals[header_list[0].index('Product Name')],
                    'sku': row_vals[header_list[0].index('Supplier SKU')],
                    'live_orders_status': row_vals[header_list[0].index('Live Order Status')],
                    'product_gst': row_vals[header_list[0].index('Product GST %')],
                    'listing_price': row_vals[header_list[0].index('Listing Price (Incl. GST & Commission)')],
                    'quantity': row_vals[header_list[0].index('Quantity')],
                    'transaction_id': row_vals[header_list[0].index('Transaction ID')],
                    'payment_date': payment_date,
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
                self.env['channel.payment.settlement.lines'].create(vals)
        self.update({
            'user_id': self.env.user,
            'import_date': datetime.today(),
        })

    def action_validate(self):
        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodestring(self.file_name)
            )
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows

        type_ids = self.env['payment.settlement.head.type'].search([])
        TYPE_DICT = {}
        for e in type_ids:
            TYPE_DICT[e.name] = e
        header_list = []
        ids_list=[]
        for row in range(number_of_rows):
            if row == 0:
                row_vals = sheet.row_values(row)
                header_list.append(row_vals)
        for rec in header_list[0]:
            if rec not in TYPE_DICT:
                type_id = self.env['payment.settlement.head.type'].create({'name': rec})
                TYPE_DICT[type_id.name] = type_id
        for row in range(number_of_rows):
            if row >= 1:
                row_vals = sheet.row_values(row)
                number = row_vals[header_list[0].index('Order ID')]
                sub = number
                sale_id = self.env['sale.order'].search(
                    [('sub_order_no', '=', sub),
                     ('sales_shop_id', '=', self.shop_id.id),
                     ])
                vals = {
                    'shop_id': self.shop_id.id,
                    'order_reference': sub,
                    'transaction_id': row_vals[header_list[0].index('Invoice ID')],
                    'order_id': sale_id.id or False,
                    'sale_total_amount': sale_id.amount_total or 0.0,
                    'final_settlement_amount': row_vals[header_list[0].index('Sale Amount (Rs.)')]

                }
                payment_transaction_id = self.env['payment.settlement.transaction'].create(vals)
                ids_list.append(payment_transaction_id.id)
                order_date = False
                for j in TYPE_DICT:
                    if j == 'Order Date' or j == 'Dispatch Date' or j == 'Payment Date':
                        order = row_vals[header_list[0].index(j)]
                        order_date = order
                        #order_date = xlrd.xldate_as_tuple(order, workbook.datemode)
                        # order_date = str(order_date[0]) + '/' + str(order_date[1]) + '/' + str(
                        #     order_date[2]) + ' ' + str(
                        #     order_date[3]) + ":" + str(order_date[4]) + ':' + str(order_date[5])
                    else:
                        order_date = row_vals[header_list[0].index(j)]
                    payment_transaction_id.write({
                        'line_ids': [(0, 0, {
                            'type_id': TYPE_DICT[j].id,
                            'value': order_date
                        })]
                    })

        act = self.env.ref('mtrmp_sales_shop.actions_payment_settlement_transaction').read([])[0]
        act['domain'] = [('id', 'in', ids_list)]
        return act


class ChannelPaymentSettlementLines(models.TransientModel):
    _name = "channel.payment.settlement.lines"
    _description = "Channel Payment Settlement Lines"

    payment_settlement_id = fields.Many2one('channel.payment.settlement')
    order_reference = fields.Char(string="Order Reference", required=True)
    order_id = fields.Many2one('sale.order')
    order_date = fields.Datetime(string="Order Date")
    dispatch_date = fields.Date(string="Dispatch Date")
    product_name = fields.Char(string='Product Name')
    sku = fields.Char(string='Supplier SKU')
    live_orders_status = fields.Char(string="Live Order Status")

    product_gst = fields.Integer(string="Product GST %")
    listing_price = fields.Float(string='Listing Price')
    quantity = fields.Integer(string='Quantity')
    transaction_id = fields.Char(string='Transaction ID')
    payment_date = fields.Date(stirng='Payment Date')
    final_amount = fields.Float(stirng='Final Settlement Amount')
    price_types = fields.Char(string='Price type')
    total_sale_amount = fields.Float(string="Total Sale Amount")
    sale_return_amount = fields.Float(string="Sale Return Amount")
    shipping_revenue = fields.Float(string="Shipping Revenue")
    shipping_return_amount = fields.Float(string="Shipping Return Amount")
    return_premium = fields.Float(string="Return premium")
    return_premium_incl_gst = fields.Float(string="Return premium (incl GST) of Return")
    commission_percentage = fields.Float(string="Meesho Commission Percentage(%)")
    commission_amount = fields.Float(string="Meesho Commission")
    return_shipping_charge = fields.Float(string="Return Shipping Charge")
    gst_compensation = fields.Float(string="GST Compensation")
    shipping_charge = fields.Float(string="Shipping Charge")
    support_service_charge = fields.Float(string="Other Support Service Charges")
    support_service_charge_waivers = fields.Float(string="Other Support Service Charges Waivers")
    net_support_service_charge = fields.Float(string="Net Other Support Service Charges")
    igst_on_meesho_commision = fields.Float(string="IGST on Meesho Commission")
    igst_on_shipping_charge = fields.Float(string="IGST on Shipping Charge")
    igst_on_return_shipping_charge = fields.Float(string="IGST on Return Shipping Charge")
    igst_on_net_other_shipping_charge = fields.Float(string="IGST on Net Other Support Service Charges")
    tcs = fields.Float(string="TCS (IGST)")
    tcs_cgst_sgst = fields.Float(string="TCS (CGST + SGST)")
    tds_rate = fields.Char(string="TDS Rate")
    tds_amount = fields.Float(string="TDS Amount")
    compensation = fields.Float(string="Compensation")
    recovery = fields.Float(string="Recovery")
