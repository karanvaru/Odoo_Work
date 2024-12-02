from odoo import models,fields,api

class FlipKartPaymentSettlement(models.Model):
    _name = 'flipkart.payment.settlement'
    _description = 'Flipkart Payment Settlement'

    order_id = fields.Many2one('sale.order')
    order_item_id = fields.Char("Order Item ID")
    product_id = fields.Many2one('product.product')
    seller_sku = fields.Char("Seller SKU")
    quantity = fields.Char("Quantity")

    total_sale_amount = fields.Char("Sale Amount")
    total_offer_amount = fields.Char("Total Offer Amount")
    customer_share = fields.Char("My share")
    customer_addons_amount = fields.Char("Customer Add-ons Amount (Rs.)")
    marketplace_fees = fields.Char("Marketplace Fees")
    total_taxes = fields.Char("Total taxes")
    offer_adjustment = fields.Char("Offer Adjustment")
    neft_id = fields.Char("NEFT ID")
    neft_type = fields.Char("NEFT TYPE")
    payment_date = fields.Char("Payment Date")
    bank_settlement_value = fields.Char("Bank Settlement Value (Rs.)")
    input_gst_tcs_credit = fields.Char("Input GST+TCS credits")
    income_tax_credit = fields.Char("Input Tax Credits")
    protection_fund = fields.Char("Protection Fund")
    refund_amount = fields.Char("Refund")
    tier = fields.Char("Tier")
    commission_rate = fields.Char("Commission Rate")
    commission = fields.Char("Commission (Rs.)")
    fixed_fees = fields.Char("Fixed Fee  (Rs.)")
    collection_fees = fields.Char("Collection Fee (Rs.)")
    pick_pack_fees = fields.Char("Pick And Pack Fee (Rs.)")
    shipping_fees = fields.Char("Shipping Fee (Rs.)")
    reverse_shipping_fees = fields.Char("Reverse Shipping Fee (Rs.)")
    no_cost_emi_Reimbursement = fields.Char("No cost EMI fee Reimbursement")
    installation_fees = fields.Char("Installation Fees")
    tech_visit_fees = fields.Char("Tech Visit Fees")
    uninstall_packing_fees = fields.Char("Uninstallation & Packaging Fee (Rs.)")
    customer_addon_amount_recovery = fields.Char("Customer Add-ons Amount Recovery (Rs.)")
    franchisee_fees = fields.Char("Franchise Fee (Rs.)")
    shopsy_marketing_fees = fields.Char("Shopsy Marketing Fee (Rs.)")
    product_cancellation_fee = fields.Char("Product Cancellation Fee ")
    tcs = fields.Char("TCS ")
    tds = fields.Char("TDS ")
    gst_on_mp_fees = fields.Char("GST on MP Fees ")
    offer_amount_settled_as_discount_in_mp_fee = fields.Char("Offer amount settled as Discount in MP Fee ")
    item_gst_rate = fields.Char("Item GST Rate (%)")
    discount_in_mp_fees = fields.Char("Discount in MP fees")
    gst_on_discount = fields.Char("GST on Discount")
    total_discount_in_mp_fees = fields.Char("Total Discount in MP Fee")
    dead_weight = fields.Char("Dead Weight (kgs)")
    total_volume = fields.Char("Length*Breadth*Height")
    volumetric_weight = fields.Char("Volumetric Weight (kgs)")
    chargeable_weight_source = fields.Char("Chargeable Weight Source")
    chargeable_weight_type = fields.Char("Chargeable Weight Type")
    chargeable_wt_slab = fields.Char("Chargeable Wt. Slab (In Kgs)")
    shipping_zone = fields.Char("Shipping Zone")
    order_date = fields.Char("Order Date")
    dispatch_date = fields.Char("Dispatch Date")
    fulfilment_type = fields.Char("Fulfilment Type")

    product_sub_category = fields.Char("Product Sub Category")
    additional_information = fields.Char("Additional Information")
    return_type = fields.Char("Return Type")
    shopsy_order = fields.Char("Shopsy Order")
    item_return_status = fields.Char("Item Return Status")
    invoice_id = fields.Char("Invoice ID")
    invoice_date = fields.Char("Invoice Date")
    buyer_sale_amount = fields.Char("Buyer Sale Amount")
    buyer_offer_amount = fields.Char("Buyer Offer amount")
    amount_free_shipping = fields.Char("Amount Free shipping")
    amount_non_free_shipping = fields.Char("Amount Non Free shipping")
    my_totoal_share = fields.Char("My totoal share")
    my_total_shipping_share = fields.Char("My total shipping share")
    my_total_non_shipping_share = fields.Char("My total non shipping share")
    my_total_non_shipping_offer_share = fields.Char("My total non shipping offer share")
