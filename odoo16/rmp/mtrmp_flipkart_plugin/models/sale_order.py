# -*- coding: utf-8 -*-
import logging
import pytz
from dateutil import parser
from odoo import models, fields, api

utc = pytz.utc

_logger = logging.getLogger(__name__)


class SaleOrderExtend(models.Model):
    _inherit = 'sale.order'

    def search_existing_flipkart_order(self, order_data, shop_id):
        sale_order = self.search([("sub_order_no", "=", order_data.get('orderId')),
                                  ("sales_shop_id", "=", shop_id.id)])
        return sale_order

    def create_flipkart_order_from_api(self, shop_id, order_data):
        log_lines = []
        res_partner_obj = self.env['res.partner']
        partner = shop_id.shop_customer_id
        partner_invoice_id = partner
        partner_shipping_id = partner
        if order_data.get('billingAddress'):
            partner_response = order_data.get('billingAddress') and order_data.get('billingAddress').get(
                'email') or order_data.get('deliveryAddress') and order_data.get('deliveryAddress').get(
                'email')
            partner = res_partner_obj.search_partner_by_email(partner_response)
            partner_invoice_response = order_data.get('billingAddress') or order_data.get('deliveryAddress')
            partner_invoice_id = self.search_or_create_bol_partner_ept(partner_invoice_response, partner, 'invoice')
            partner_shipping_id = self.search_or_create_bol_partner_ept(order_data.get(
                'deliveryAddress'), partner or partner_invoice_id or False, 'delivery')
        vals = self.prepare_vals_for_flipkart_order(shop_id, order_data, partner or partner_invoice_id,
                                                    partner_invoice_id, partner_shipping_id)
        order = self.create(vals)
        logs, skip_order = self.create_flipkart_order_lines(shop_id, order, order_data)
        if logs:
            log_lines = log_lines + logs
        if skip_order:
            order.unlink()
            return False
        return True

    def prepare_vals_for_flipkart_order(self, shop_id, order_data, partner_id, partner_invoice_id,
                                        partner_shipping_id):
        vals = {}
        date_order = order_data.get('orderDate')
        date_order = parser.parse(date_order).astimezone(utc).strftime('%Y-%m-%d %H:%M:%S')
        vals.update({'partner_id': partner_id.id,
                     'partner_invoice_id': partner_invoice_id.id,
                     'partner_shipping_id': partner_shipping_id.id,
                     'sub_order_no': order_data.get('orderId'),
                     'sales_shop_id': shop_id.id,
                     'client_order_ref': order_data.get('orderId'),
                     "company_id": shop_id.company_id.id if shop_id.company_id else False,
                     "warehouse_id": shop_id.default_warehouse_id.id,
                     "pricelist_id": shop_id.pricelist_id.id,
                     "state": "draft",
                     "team_id": shop_id.crm_team_id.id,
                     "date_order": date_order,
                     })
        new_record = self.new(vals)
        order_vals = self._convert_to_write({name: new_record[name] for name in new_record._cache})
        return order_vals

    def search_shop_product(self, default_code, shop_id):
        shop_product = False
        if not shop_product and default_code:
            shop_product = self.env['sale.shop.product'].search([('default_code', '=', default_code),
                                                                 ('shop_id', '=', shop_id.id)])
        if not shop_product:
            return False
        return shop_product

    def prepare_vals_for_sale_order_line(self, product, product_name, price, quantity, order):
        uom_id = product and product.uom_id and product.uom_id.id or False
        line_vals = {
            "product_id": product and product.ids[0] or False,
            "order_id": order.id,
            "company_id": self.company_id.id,
            "product_uom": uom_id,
            "name": product_name,
            "price_unit": price,
            "product_uom_qty": quantity
        }
        return line_vals

    def create_flipkart_order_lines(self, shop_id, order, order_line):
        log_lines = []
        skip_order = False
        product_sku = order_line.get('sku')
        flipkart_order_id = order.sub_order_no
        shop_product = self.search_shop_product(product_sku, shop_id)
        price_component = order_line.get('priceComponents')
        if not shop_product:
            shop_log_id = self.env['shop.fail.log'].create({'operation': 'import_sales_order',
                                                            'shop_id': shop_id.id})
            message = "Odoo product is not found with SKU {0}".format(product_sku)
            vals = {'operation': 'import_sales_order', 'message': message, 'shop_log_id': shop_log_id.id,
                    'display_name': flipkart_order_id, 'is_mismatch': True}
            log_lines.append([0, 0, vals])
            shop_log_id.log_lines = log_lines
            skip_order = True

        if not skip_order:
            product = shop_product.product_id
            sale_order_line = self.create_flipkart_sale_order_line(product, float(order_line.get('quantity')),
                                                                   product.name or order_line.get("title"),
                                                                   float(price_component['sellingPrice']),
                                                                   order_line, order, is_discount=False)
            sale_order_line.write({'flipkart_order_item_id': order_line.get('orderItemId')})
        if price_component['shippingCharge'] or price_component['flipkartDiscount']:
            self.create_flipkart_shipping_discount_lines(order_line, price_component, shop_id, order)
        return log_lines, skip_order

    def create_flipkart_sale_order_line(self, product, quantity, product_name, price,
                                        order_response, order, is_discount=False):
        sale_order_line_obj = self.env["sale.order.line"]
        shop_id = self.sales_shop_id
        order_line_vals = self.prepare_vals_for_sale_order_line(product, product_name, price, quantity, order)
        if is_discount:
            order_line_vals["name"] = "Discount for " + str(product_name)
        order_line = sale_order_line_obj.create(order_line_vals)
        order_line.with_context(round=False)._compute_amount()
        return order_line

    def create_flipkart_shipping_discount_lines(self, order_response, price_component, shop_id, order):
        order_number = self.sub_order_no
        shipping_price = float(price_component['shippingCharge'])
        discount_amount = float(price_component['flipkartDiscount'])
        discount_product_id = shop_id.default_discount_product_id
        shipping_product_id = shop_id.default_delivery_product_id
        if shipping_product_id and shipping_price > 0.0:
            order_line = self.create_flipkart_sale_order_line(shipping_product_id, 1,
                                                              shipping_product_id.name or order_response.get("title"),
                                                              shipping_price,
                                                              order_response, order, is_discount=False)
            _logger.info("Creating shipping line for Odoo order(%s) and Flipkart order is (%s)", self.name,
                         order_number)
        if discount_product_id and discount_amount > 0.0:
            _logger.info("Creating discount line for Odoo order(%s) and Flipkart order is (%s)", self.name,
                         order_number)
            self.create_flipkart_sale_order_line(discount_product_id, 1,
                                                 discount_product_id.name, float(discount_amount) * -1,
                                                 order_response, order, is_discount=True)
