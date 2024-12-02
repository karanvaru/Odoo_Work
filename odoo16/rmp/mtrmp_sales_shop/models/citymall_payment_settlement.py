from odoo import models,fields,api

class FlipKartPaymentSettlement(models.Model):
    _name = 'citymall.payment.settlement'
    _description = 'Citymall Payment Settlement'

    order_id = fields.Many2one('sale.order', 'Order ID')
    sales_shop_id = fields.Many2one('sale.shop')
    product_id = fields.Many2one('product.product')

    order_code = fields.Char('Order')
    order_date = fields.Char()
    dispatch_date = fields.Char()
    return_date_of_delivery_to_seller = fields.Char()
    month_of_return_date_of_delivery_to_seller = fields.Char()
    payment_date = fields.Char()
    product_name = fields.Char()
    sku_id = fields.Char()
    live_order_status = fields.Char()
    product_gst = fields.Char()
    listing_price = fields.Char()
    quantity = fields.Char()
    transaction_id = fields.Char()
    final_settlement_amount	 = fields.Char()
    total_sale_amount = fields.Char()
    sale_return_amount = fields.Char()
    shipping_revenue = fields.Char()
    forward_shipping_fee_without_gst = fields.Char()
    shipping_return_amount = fields.Char()
    return_shipping_fee_without_gst = fields.Char()
    platform_fee = fields.Char()
    penalty = fields.Char()
    shipping_charge = fields.Char()
    return_shipping_charge = fields.Char()
    tcs = fields.Char()
    tds = fields.Char()

