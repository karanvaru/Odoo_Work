from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    #amazon_order_id = fields.Many2one('sale.order', string='Amazon Sales Reference',required=True,
    # ondelete='cascade')
    #sale_order_line_id = fields.Many2one('sale.order.line', string='OE Order Line',  required=True,
    # ondelete="cascade")
    amazon_order_item_id = fields.Char(string="Amazon Order Item Id")
    line_tax_amount = fields.Float("Line Tax", default=0.0,
                                   digits=dp.get_precision("Product Price"))
    #instance_id=fields.Many2one("amazon.instance.ept",string="Instance",
    # related="order_id.instance_id",required=True,readonly=True)
    amazon_product_id = fields.Many2one("amazon.product.ept", "Amazon Product")
    amazon_order_qty = fields.Float("Amazon Order Qty")
    amz_merchant_adjustment_item_id = fields.Char(string="Merchant Adjustment Item Id",
                                                  default=False)
    amz_order_product_id = fields.Many2one('amazon.product.ept', string='Order Product')
    amz_shipping_charge_ept = fields.Float("Shipping Charge", default=0.0,
                                           digits=dp.get_precision("Product Price"))
    amz_shipping_discount_ept = fields.Float("Shipping Discount", default=0.0,
                                             digits=dp.get_precision("Product Price"))
    amz_gift_wrapper_charge = fields.Float("Gift Wrapper Charge", default=0.0,
                                           digits=dp.get_precision("Product Price"))
    amz_promotion_discount = fields.Float("Promotion Discount", default=0.0,
                                          digits=dp.get_precision("Product Price"))
    amz_shipping_charge_tax = fields.Float("Shipping Charge", default=0.0,
                                           digits=dp.get_precision("Product Price"))
    amz_order_line_tax = fields.Float("Order Line Tax", default=0.0,
                                      digits=dp.get_precision("Product Price"))
    amz_shipping_charge_tax = fields.Float("Shipping Charge Tax", default=0.0,
                                           digits=dp.get_precision("Product Price"))
    amz_gift_wrapper_tax = fields.Float("Tax of Shipping Charge", default=0.0,
                                        digits=dp.get_precision("Product Price"))
    amz_return_reason = fields.Selection([('NoInventory', 'NoInventory'),
                                          ('ShippingAddressUndeliverable',
                                           'ShippingAddressUndeliverable'),
                                          ('CustomerExchange', 'CustomerExchange'),
                                          ('BuyerCanceled', 'BuyerCanceled'),
                                          ('GeneralAdjustment', 'GeneralAdjustment'),
                                          ('CarrierCreditDecision', 'CarrierCreditDecision'),
                                          ('RiskAssessmentInformationNotValid',
                                           'RiskAssessmentInformationNotValid'),
                                          ('CarrierCoverageFailure', 'CarrierCoverageFailure'),
                                          ('CustomerReturn', 'CustomerReturn'),
                                          ('MerchandiseNotReceived', 'MerchandiseNotReceived')
                                          ], string="Return Reason", default="NoInventory")
    amz_promotion_claim_code = fields.Char("Promotion Claim Code")
    amz_merchant_promotion_id = fields.Char("MerchantPromotionID")
    amz_gift_message_text = fields.Text("Gift Message Text")  # for flat report
    amz_gift_wrap_type = fields.Char("gift_wrap_type")  # for flat report
    

    # added by twinkal to merge FBA
    amz_gift_message = fields.Text("Gift Message")
    amz_displayable_comment = fields.Text("Displayable Comment")
    amz_per_unit_declared_value = fields.Float("Per Unit Declared Value",
                                               digits=dp.get_precision("Product Price"),
                                               default=0.0)
    amz_merchant_order_item_id = fields.Char(string="Merchant Item Id")
    amz_merchant_adjustment_item_id = fields.Char(string="Merchant Adjustment Item Id",
                                                  default=False)
    amz_fulfillment_center_id = fields.Many2one('amazon.fulfillment.center',
                                                string='Fulfillment Center')    

    @api.multi
    def get_item_price(self, order_line,seller_id):
        """
        If seller field is_vat_inclusive_activated is set true
        then doesn't add tax of amazon api into price
        @author: Deval Jagad (01/01/2020)
        """
        tax_amount = 0.0
        if not seller_id.is_vat_inclusive_activated:
            tax_amount = float(order_line.get('ItemTax', {}).get('Amount', {}).get('value', 0.0))
        item_price = float(order_line.get('ItemPrice', {}).get('Amount', {}).get('value', 0.0))
        return tax_amount + item_price

    @api.multi
    def get_shipping_price(self, order_line, seller_id):
        """
        If seller field is_vat_inclusive_activated is set true
        then doesn't add tax of amazon api into price
        @author: Deval Jagad (01/01/2020)
        """
        tax_amount = 0.0
        if not seller_id.is_vat_inclusive_activated:
            tax_amount = float(order_line.get('ShippingTax', {}).get('Amount', {}).get('value', 0.0))
        item_price = float(order_line.get('ShippingPrice', {}).get('Amount', {}).get('value', 0.0))
        return tax_amount + item_price

    @api.multi
    def get_gift_wrapper_price(self, order_line, seller_id):
        """
        If seller field is_vat_inclusive_activated is set true
        then doesn't add tax of amazon api into price
        @author: Deval Jagad (01/01/2020)
        """
        tax_amount = 0.0
        item_price = float(order_line.get('GiftWrapPrice', {}).get('Amount', {}).get('value', 0.0))
        if not seller_id.is_vat_inclusive_activated:
            tax_amount = float(order_line.get('GiftWrapTax', {}).get('Amount', {}).get('value', 0.0))
        return tax_amount + item_price

    @api.multi
    def get_item_tax_amount(self, order_line, item_price):
        tax_amount = float(order_line.get('ItemTax', {}).get('Amount', {}).get('value', 0.0))
        return tax_amount

    @api.multi
    def get_shipping_tax_amount(self, order_line, shipping_charge):
        tax_amount = float(order_line.get('ShippingTax', {}).get('Amount', {}).get('value', 0.0))
        return tax_amount

    @api.multi
    def get_gift_wrapper_tax_amount(self, order_line, git_wrapper_charge):
        tax_amount = float(order_line.get('GiftWrapTax', {}).get('Amount', {}).get('value', 0.0))
        return tax_amount

    @api.multi
    def create_sale_order_line(self, order_line, instance, amazon_order, create_service_line=True):
        fulfillment_by = amazon_order.amz_fulfillment_by
        product_details = self.search_or_create_or_update_product(order_line, instance,
                                                                  fulfillment_by)
        prod_order_line = False
        """selling Product Line"""
        amazon_product = product_details.get('sale_product', False)
        if amazon_product:
            item_price = self.get_item_price(order_line,instance.seller_id)
            order_qty = order_line.get('QuantityOrdered', {}).get('value', 0.0)
            title = order_line.get('Title', {}).get('value', False)
            qty_price_dict = self.calculate_order_qty_and_price_based_on_asin_qty(amazon_product,
                                                                                  float(item_price),
                                                                                  float(order_qty))
            tax_amount = self.get_item_tax_amount(order_line, item_price)
            tax_id = False
            order_line_vals = self.create_sale_order_line_vals_amazon(order_line, qty_price_dict,
                                                                      tax_id, amazon_product,
                                                                      amazon_product.product_id and
                                                                      amazon_product.product_id.id,
                                                                      amazon_order, instance, title)
            order_line_vals.update({'line_tax_amount': tax_amount})
            prod_order_line = self.create(order_line_vals)

        if not create_service_line:
            return True
        """Shipment Charge Line"""
        shipment_product = amazon_order.carrier_id and \
                           amazon_order.carrier_id.product_id or \
                           product_details.get('shipment_charge', False)
        shipping_charge_description = product_details.get('shipping_charge_description', False)
        if shipment_product or shipping_charge_description:
            shipping_charge = self.get_shipping_price(order_line, instance.seller_id)
            if shipping_charge > 0.0:
                tax_amount = self.get_shipping_tax_amount(order_line, shipping_charge)
                tax_id = False
                qty_price_dict.update({'order_qty': 1, 'amount_per_unit': shipping_charge})
                order_line_vals = self.create_sale_order_line_vals_amazon(order_line, qty_price_dict,
                                                                          tax_id, False,
                                                                          shipment_product or False,
                                                                          amazon_order, instance, (
                                                                                  shipping_charge_description and
                                                                                  shipping_charge_description) or (
                                                                                  shipment_product and
                                                                                  shipment_product.name or
                                                                                  'Shipping Charge'))
                order_line_vals.update({'is_delivery': True,
                                        'amazon_product_id': amazon_product.id,
                                        'line_tax_amount': tax_amount})
                prod_order_line and prod_order_line.write(
                    {'amz_shipping_charge_ept': shipping_charge, 'amz_shipping_charge_tax': tax_amount})
                self.create(order_line_vals)

        """Shipment Discount Line"""
        shipment_discount_product = product_details.get('shipment_discount_product', False)
        shipping_discount_description = product_details.get('shipping_discount_description', False)
        if shipment_discount_product or shipping_discount_description:
            shipping_discount = float(
                order_line.get('ShippingDiscount', {}).get('Amount', {}).get('value', 0.0))
            qty_price_dict.update({'order_qty': 1, 'amount_per_unit': shipping_discount})
            order_line_vals = self.create_sale_order_line_vals_amazon(order_line, qty_price_dict,
                                                                      False, False,
                                                                      shipment_discount_product or False,
                                                                      amazon_order, instance, (
                                                                              shipping_discount_description and
                                                                              shipping_discount_description) or (
                                                                              shipment_discount_product and
                                                                              shipment_discount_product.name or
                                                                              'Shipping Discount'))
            prod_order_line and prod_order_line.write(
                {'amz_shipping_discount_ept': shipping_discount})
            self.create(order_line_vals)

        """Gift Wrapper Line"""
        gift_wrapper_product = product_details.get('gift_wrapper_charge', False)
        gift_wrapper_description = product_details.get('gift_wrapper_description', False)
        if gift_wrapper_product or gift_wrapper_description:
            git_wrapper_charge = self.get_gift_wrapper_price(order_line,instance.seller_id)
            tax_amount = self.get_gift_wrapper_tax_amount(order_line, git_wrapper_charge)
            tax_id = False
            qty_price_dict.update({'order_qty': 1, 'amount_per_unit': git_wrapper_charge})
            order_line_vals = self.create_sale_order_line_vals_amazon(order_line, qty_price_dict,
                                                                      tax_id, False,
                                                                      gift_wrapper_product or False,
                                                                      amazon_order, instance, (
                                                                              gift_wrapper_description and
                                                                              gift_wrapper_description) or (
                                                                              gift_wrapper_product and
                                                                              gift_wrapper_product.name or
                                                                              'Gift Wrapper Fee'))
            order_line_vals.update({'line_tax_amount': tax_amount})
            prod_order_line and prod_order_line.write(
                {'amz_gift_wrapper_charge': git_wrapper_charge, 'amz_gift_wrapper_tax': tax_amount})
            self.create(order_line_vals)

        """Promotion Discount """
        promotion_discount_product = product_details.get('promotion_discount', False)
        promotion_discount_description = product_details.get('promotion_discount_description',
                                                             False)
        if promotion_discount_product or promotion_discount_description:
            promotion_discount = float(
                order_line.get('PromotionDiscount', {}).get('Amount', {}).get('value', 0.0))
            if promotion_discount > 0.0:
                promotion_discount = promotion_discount * -1
            qty_price_dict.update({'order_qty': 1, 'amount_per_unit': promotion_discount})
            order_line_vals = self.create_sale_order_line_vals_amazon(order_line, qty_price_dict,
                                                                      tax_id, False,
                                                                      promotion_discount_product or False,
                                                                      amazon_order, instance, (
                                                                              promotion_discount_description and
                                                                              promotion_discount_description) or (
                                                                              promotion_discount_product and
                                                                              promotion_discount_product.name or
                                                                              'Promotion Discount'))
            prod_order_line and prod_order_line.write(
                {'amz_promotion_discount': promotion_discount})
            self.create(order_line_vals)

        return True

    """
        This Method Search  Or Create Product into ERP ,If In shipment,gift wrapper,
        promotion product,Cod product Configured in the instance then we will take set product in 
        the sale order line or we will set only description in the sale order line
        we have not create this type of product from  the code
    """

    @api.multi
    def search_or_create_or_update_product(self, order_line, instance, fulfillment_by):
        amazon_product_obj = self.env['amazon.product.ept']
        asin_number = order_line.get('ASIN', {}).get('value', False)
        seller_sku = order_line.get('SellerSKU', {}).get('value', False)
        domain = [('instance_id', '=', instance.id)]

        shipment_charge_product, gift_wrapper_product, promotion_discount_product, cod_charge_product_id = False, False, False, False
        shipment_discount_product, shipping_discount_description = False, False
        shipping_charge_description, gift_wrapper_description, promotion_discount_description, cod_charge_description = False, False, False, False
        # asin_number and domain.append(('product_asin','=',asin_number))
        seller_sku and domain.append(('seller_sku', '=', seller_sku))

        """Search Product Which we will deliver to the customer"""
        odoo_product = amazon_product_obj.search_product(seller_sku)
        amazon_product = amazon_product_obj.search_amazon_product(instance.id, seller_sku,
                                                                  fulfillment_by)
        if not amazon_product:
            product_vals = self.create_product_vals(order_line, instance, odoo_product,
                                                    fulfillment_by)
            amazon_product = amazon_product_obj.create(product_vals)

        if not amazon_product.product_asin:
            amazon_product.write({'product_asin': asin_number})

        """Create Or Search Shipment Charge Product"""
        if float(order_line.get('ShippingPrice', {}).get('Amount', {}).get('value', 0.0)) > 0.0:

            """Changes by Dhruvi
                Fetching value of shipment_charge_product according to seller wise"""
            if instance.seller_id.shipment_charge_product_id:
                shipment_charge_product = instance.seller_id.shipment_charge_product_id
            else:
                shipping_charge_description = "Shipping and Handling"

        """Create Or Search Shipment Discount Product"""
        if float(order_line.get('ShippingDiscount', {}).get('Amount', {}).get('value', 0.0)) > 0.0:

            """Changes by Dhruvi
                Getting value of ship_discount_product_id according to seller wise"""
            if instance.seller_id.ship_discount_product_id:
                shipment_discount_product = instance.seller_id.ship_discount_product_id
            else:
                shipping_discount_description = "Shipping Discount"

        """Create Or Search GiftWrapper Product"""
        if float(order_line.get('GiftWrapPrice', {}).get('Amount', {}).get('value', 0.0)) > 0.0:

            """Changes by Dhruvi
                Getting value of gift_wrapper_product_id according to seller wise"""
            if instance.seller_id.gift_wrapper_product_id:
                gift_wrapper_product = instance.seller_id.gift_wrapper_product_id
            else:
                gift_wrapper_description = 'Gift Wrapping'

        """Create Or Search Promotion Discount Product"""
        if float(order_line.get('PromotionDiscount', {}).get('Amount', {}).get('value', 0.0)) > 0.0:

            """Changes by Dhruvi
                Getting value of promotion_discount_product according to seller wise."""
            if instance.seller_id.promotion_discount_product_id:
                promotion_discount_product = instance.seller_id.promotion_discount_product_id
            else:
                promotion_discount_description = 'Promotion Discount'

        return {
            'sale_product': amazon_product,
            'shipment_charge': shipment_charge_product,
            'gift_wrapper_charge': gift_wrapper_product,
            'promotion_discount': promotion_discount_product,
            'cod_charge': cod_charge_product_id,
            'shipping_charge_description': shipping_charge_description,
            'gift_wrapper_description': gift_wrapper_description,
            'promotion_discount_description': promotion_discount_description,
            'cod_charge_description': cod_charge_description,
            'shipment_discount_product': shipment_discount_product,
            'shipping_discount_description': shipping_discount_description,
        }

    def create_sale_order_line_vals_amazon(self, order_line, qty_price_dict, tax_id,
                                           amazon_product=False, odoo_product=False,
                                           amazon_order=False, instance=False, title=False):

        """If In amazon Response we got 0.0 amazon in tax then search from the product
        if we got tax in product then we set default tax based on instance configuration"""
        sale_order_line = self.env['sale.order.line']
        # new_record = self.env['sale.order.line'].new({'order_id': amazon_order.id,
        #                                               'company_id': amazon_order.company_id.id,
        #                                               'product_id': amazon_product and
        # amazon_product.product_id.id or odoo_product and odoo_product.id or False,
        #                                               'product_uom': amazon_product and
        # amazon_product.product_tmpl_id.uom_id or odoo_product and odoo_product.product_tmpl_id.uom_id,
        #                                               'name': title
        #                                               })
        # new_record.product_id_change()
        # order_vals = new_record._convert_to_write(
        #     {name: new_record[name] for name in new_record._cache})
        #
        # order_qty = qty_price_dict.get('order_qty')
        # order_vals.update({
        #     'product_uom_qty': order_qty,
        #     'amazon_order_qty': order_line.get('QuantityOrdered', {}).get('value', 0.0),
        #     'price_unit': qty_price_dict.get('amount_per_unit'),
        #     'customer_lead': amazon_product and amazon_product.sale_delay or False,
        #     'invoice_status': False,
        #     'state': 'draft',
        #     'amazon_order_item_id': order_line.get('OrderItemId', {}).get('value'),
        #     'discount': 0.0,
        #     'amazon_product_id': amazon_product and amazon_product.id or False,
        #     'product_uom': new_record.product_uom.id,
        #     'producturl': "%s%s" % (
        #     instance.producturl_prefix or '', order_line.getvalue("ASIN", "value"))
        # })

        vals = ({
            'order_id': amazon_order.id,
            'product_id': amazon_product and amazon_product.product_id.id or
                          odoo_product and odoo_product.id or False,
            'company_id': amazon_order.company_id.id,
            'description': title,
            'order_qty': qty_price_dict.get('order_qty'),
            'price_unit': qty_price_dict.get('amount_per_unit'),
            'discount': 0.0,
            'product_uom': amazon_product and amazon_product.product_tmpl_id.uom_id or
                           odoo_product and odoo_product.product_tmpl_id.uom_id
        })
        order_vals = sale_order_line.create_sale_order_line_ept(vals)

        order_vals.update({
            'amazon_order_qty': order_line.get('QuantityOrdered', {}).get('value', 0.0),
            'customer_lead': amazon_product and amazon_product.sale_delay or False,
            'invoice_status': False,
            'amazon_order_item_id': order_line.get('OrderItemId', {}).get('value'),
            'amazon_product_id': amazon_product and amazon_product.id or False,
            'producturl': "%s%s" % (
            instance.producturl_prefix or '', order_line.get("ASIN", "value"))
        })
        return order_vals


    @api.multi
    def calculate_order_qty_and_price_based_on_asin_qty(self, amazon_product, item_price,
                                                        order_qty):
        if amazon_product and (not amazon_product.allow_package_qty):
            if order_qty > 0:
                item_price = float(item_price) / float(order_qty)
            return {'order_qty': order_qty, 'amount_per_unit': item_price}
        if amazon_product and order_qty > 0.0:
            asin_qty = amazon_product.asin_qty * order_qty
            amount_per_unit = item_price / asin_qty
            order_qty = asin_qty
        elif order_qty and order_qty > 0.0:
            amount_per_unit = item_price / order_qty
        else:
            amount_per_unit = 0.0
        return {'order_qty': order_qty, 'amount_per_unit': amount_per_unit}

    @api.multi
    def create_product_vals(self, order_line, instance, odoo_product, fulfillment_by):
        sku = order_line.get('SellerSKU', {}).get('value', False) or (
                odoo_product and odoo_product[0].default_code) or False
        vals = {
            'instance_id': instance.id,
            'product_asin': order_line.get('ASIN', {}).get('value', False),
            'seller_sku': sku,
            'type': odoo_product and odoo_product[0].type or 'product',
            'product_id': odoo_product and odoo_product[0].id or False,
            'purchase_ok': True,
            'sale_ok': True,
            'exported_to_amazon': True,
            'fulfillment_by': fulfillment_by,
        }
        if not odoo_product:
            vals.update({'name': order_line.get('Title', {}).get('value'), 'default_code': sku})

        return vals
