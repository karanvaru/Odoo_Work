from odoo import models,fields,api

class AmazonPaymentSettlement(models.Model):
    _name = 'amazon.payment.settlement'
    _description = 'Amazon Payment Settlement'

    order_id = fields.Many2one('sale.order', 'Order ID')
    sales_shop_id = fields.Many2one('sale.shop')
    product_id = fields.Many2one('product.product')

    date = fields.Char('date/time')
    settlement_id = fields.Char('Settlement ID')
    type = fields.Char('Type')
    sku = fields.Char('SKU')
    description = fields.Char('Description')
    quantity = fields.Char('Quantity')
    marketplace = fields.Char('Marketplace')
    account_type = fields.Char('Account Type')
    fulfillment = fields.Char('Fulfillment')
    order_city = fields.Char('Order City')
    order_state = fields.Char('Order State')
    order_postal = fields.Char('Order Postal')
    product_sales = fields.Char('Product Sales')
    shipping_credits = fields.Char('Shipping Credits')
    promotional_rebates = fields.Char('Promotional Rebates')
    total_sales_tax_liable = fields.Char('Total Sales Tax Liable (GST before adjusting TCS)')
    tcs_cgst = fields.Char('TCS-CGST')
    tcs_sgst = fields.Char('TCS-SGST')
    tcs_igst = fields.Char('TCS-IGST')
    tds = fields.Char('TDS (Section 194-O)')
    selling_fees = fields.Char('Selling Fees')
    fba_fees = fields.Char('FBA fees')
    other_transaction_fees = fields.Char('Other Transaction Fees')
    other = fields.Char('Other')
    total = fields.Char('Total')










