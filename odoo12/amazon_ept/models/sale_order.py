import pytz
import requests
import ast
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from dateutil import parser
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap
from ..endpoint import DEFAULT_ENDPOINT
import time
import logging
_logger = logging.getLogger(__name__)
utc = pytz.utc


class sale_order(models.Model):
    _inherit = "sale.order"

    # take care about this during merge file added to solve instance issue
    amz_is_outbound_order = fields.Boolean("Out Bound Order", default=False)

    # Added by twinkal to merge amazon FBA
    full_fill_ment_order_help = """ 
        RECEIVED:The fulfillment order was received by Amazon Marketplace Web Service (Amazon MWS) 
                 and validated. Validation includes determining that the destination address is 
                 valid and that Amazon's records indicate that the seller has enough sellable 
                 (undamaged) inventory to fulfill the order. The seller can cancel a fulfillment 
                 order that has a status of RECEIVED
        INVALID:The fulfillment order was received by Amazon Marketplace Web Service (Amazon MWS) 
                but could not be validated. The reasons for this include an invalid destination 
                address or Amazon's records indicating that the seller does not have enough sellable 
                inventory to fulfill the order. When this happens, the fulfillment order is invalid 
                and no items in the order will ship
        PLANNING:The fulfillment order has been sent to the Amazon Fulfillment Network to begin 
                 shipment planning, but no unit in any shipment has been picked from inventory yet. 
                 The seller can cancel a fulfillment order that has a status of PLANNING
        PROCESSING:The process of picking units from inventory has begun on at least one shipment 
                   in the fulfillment order. The seller cannot cancel a fulfillment order that 
                   has a status of PROCESSING
        CANCELLED:The fulfillment order has been cancelled by the seller.
        COMPLETE:All item quantities in the fulfillment order have been fulfilled.
        COMPLETE_PARTIALLED:Some item quantities in the fulfillment order were fulfilled; the rest 
                            were either cancelled or unfulfillable.
        UNFULFILLABLE: item quantities in the fulfillment order could be fulfilled because t
        he Amazon fulfillment center workers found no inventory 
        for those items or found no inventory that was in sellable (undamaged) condition.
    """

    help_fulfillment_action = """ 
        Ship - The fulfillment order ships now
        
        Hold - An order hold is put on the fulfillment order.3
        
        Default: Ship in Create Fulfillment
        Default: Hold in Update Fulfillment    
    """

    help_fulfillment_policy = """ 
    
        FillOrKill - If an item in a fulfillment order is determined to be unfulfillable before any 
                    shipment in the order moves to the Pending status (the process of picking units 
                    from inventory has begun), then the entire order is considered unfulfillable. 
                    However, if an item in a fulfillment order is determined to be unfulfillable 
                    after a shipment in the order moves to the Pending status, Amazon cancels as 
                    much of the fulfillment order as possible
                    
        FillAll - All fulfillable items in the fulfillment order are shipped. 
                The fulfillment order remains in a processing state until all items are either 
                shipped by Amazon or cancelled by the seller
                
        FillAllAvailable - All fulfillable items in the fulfillment order are shipped. 
            All unfulfillable items in the order are cancelled by Amazon.
            
        Default: FillOrKill
    """

    amz_fulfillment_by = fields.Selection(
        [('MFN', 'Manufacturer Fulfillment Network'), ('AFN', 'Amazon Fulfillment Network')],
        string="Fulfillment By")
    amz_fulfillment_action = fields.Selection([('Ship', 'Ship'), ('Hold', 'Hold')],
                                              string="Fulfillment Action", default="Hold",
                                              help=help_fulfillment_action)
    amz_displayable_date_time = fields.Date("Displayable Order Date Time", required=False,
                                            help="Display Date in package")
    amz_shipment_service_level_category = fields.Selection(
        selection_add=[('Priority', 'Priority'),
                       ('ScheduledDelivery', 'ScheduledDelivery')],
        help="ScheduledDelivery used only for japan")
    amz_fulfillment_policy = fields.Selection([('FillOrKill', 'FillOrKill'), ('FillAll', 'FillAll'),
                                               ('FillAllAvailable', 'FillAllAvailable')],
                                              string="Fulfillment Policy", default="FillOrKill",
                                              required=False, help=help_fulfillment_policy)
    amz_is_outbound_order = fields.Boolean("Out Bound Order", default=False)
    amz_delivery_start_time = fields.Datetime("Delivery Start Time",
                                              help="Delivery Estimated Start Time")
    amz_delivery_end_time = fields.Datetime("Delivery End Time", help="Delivery Estimated End Time")
    exported_in_amazon = fields.Boolean("Exported In Amazon", default=False)
    notify_by_email = fields.Boolean("Notify By Email", default=False,
                                     help="If true then system will notify by email to followers")
    amz_fulfullment_order_status = fields.Selection(
        [('RECEIVED', 'RECEIVED'), ('INVALID', 'INVALID'), ('PLANNING', 'PLANNING'),
         ('PROCESSING', 'PROCESSING'), ('CANCELLED', 'CANCELLED'), ('COMPLETE', 'COMPLETE'),
         ('COMPLETE_PARTIALLED', 'COMPLETE_PARTIALLED'), ('UNFULFILLABLE', 'UNFULFILLABLE')],
        string="Fulfillment Order Status", help=full_fill_ment_order_help)

    amz_shipment_report_id = fields.Many2one('shipping.report.request.history', "Shipment Report")

    @api.one
    @api.constrains('amz_fulfillment_action')
    def check_fulfillment_action(self):
        for record in self:
            if record.sudo().exported_in_amazon and record.sudo().amz_fulfillment_action == 'Hold':
                raise Warning(
                    "You can change action Ship to Hold Which are already exported in amazon")

    @api.multi
    def _check_is_fba_warhouse(self):
        for record in self:
            if record.warehouse_id.is_fba_warehouse:
                record.order_has_fba_warehouse = True
            else:
                record.order_has_fba_warehouse = False

    order_has_fba_warehouse = fields.Boolean("Order Has FBA Warehouse",
                                             compute="_check_is_fba_warhouse", store=False)

    # This Function will create wizard for creating outbound shiipment (For 1 record only)
    @api.multi
    def create_outbound_shipment(self):
        amazon_outbound_order_wizard_obj = self.env['amazon.outbound.order.wizard']
        created_id = amazon_outbound_order_wizard_obj.with_context(
            {'active_model': self._name, 'active_ids': self.ids,
             'active_id': self.id or False}).create({'sale_order_ids': [(6, 0, [self.id])]})
        return amazon_outbound_order_wizard_obj.wizard_view(created_id)

    @api.multi
    def action_cancel(self):
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        for order in self:
            instance = order.amz_instance_id
            if order.amz_is_outbound_order:
                if order.amz_fulfullment_order_status in ['PROCESSING', 'COMPLETE',
                                                          'COMPLETE_PARTIALLED']:
                    raise Warning(
                        "You cannot cancel a fulfillment order with a status of Processing, "
                        "Complete, or CompletePartialled")

                proxy_data = instance.seller_id.get_proxy_server()

                kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                          'auth_token': instance.auth_token and str(instance.auth_token) or False,
                          'app_name': 'amazon_ept',
                          'account_token': account.account_token,
                          'emipro_api': 'action_cancel',
                          'dbuuid': dbuuid,
                          'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                                     instance.country_id.code,
                          'proxies': proxy_data,
                          'order_name': order.name, }

                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):
                    raise Warning(response.get('reason'))

                # order.sale_order_id.action_cancel()
            res = super(sale_order, self).action_cancel()
            return res

    @api.multi
    def action_button_confirm(self):
        for order in self:
            if order.amz_is_outbound_order:
                if order.amz_fulfillment_action != 'Ship':
                    raise Warning(
                        "Set Fulfillment Action To Ship Otherwise you are not allow to "
                        "confirm this order")
        #             order.action_button_confirm()
        super(sale_order, self).action_button_confirm()
        return True

    """This Function Cancel Orders into ERP System"""

    @api.multi
    def cancel_draft_sales_order(self, seller, list_of_wrapper):
        instance_obj = self.env['amazon.instance.ept']
        for wrapper_obj in list_of_wrapper:
            orders = []
            if not isinstance(wrapper_obj.get('Orders', {}).get('Order', []), list):
                orders.append(wrapper_obj.get('Orders', {}).get('Order', {}))
            else:
                orders = wrapper_obj.get('Orders', {}).get('Order', [])
            transaction_log_lines = []
            skip_order = False
            marketplace_instance_dict = {}
            for order in orders:
                order_status = order.get('OrderStatus', {}).get('value', '')
                if order_status != 'Canceled':
                    continue

                amazon_order_ref = order.get('AmazonOrderId', {}).get('value', False)
                if not amazon_order_ref:
                    continue

                marketplace_id = order.get('MarketplaceId', {}).get('value', False)
                instance = marketplace_instance_dict.get(marketplace_id)
                if not instance:
                    instance = instance_obj.search(
                        [('marketplace_id.market_place_id', '=', marketplace_id),
                         ('seller_id', '=', seller.id)])
                    marketplace_instance_dict.update({marketplace_id: instance})

                existing_order = self.search([('amazon_reference', '=', amazon_order_ref),
                                              ('amz_instance_id', '=', instance.id),
                                              ('state', '!=', 'cancel')])
                if existing_order:
                    if existing_order.state != 'draft' and existing_order.state != 'cancel':
                        ### Create log to notify to user that order has been processed in odoo but in amazon it's cancel
                        log_message = 'Sale order %s not in draft state, only draft order can be ' \
                                      'cancelled.' % (existing_order.name)
                        skip_order = True
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'sale.order'),
                            'res_id': existing_order.id or 0,
                            'log_type': 'not_found',
                            'action_type': 'skip_line',
                            'not_found_value': existing_order.name,
                            'user_id': self.env.uid,
                            'skip_record': skip_order,
                            'amazon_order_reference': amazon_order_ref,
                            'message': log_message,
                        }
                        transaction_log_lines.append((0, 0, log_line_vals))
                    else:
                        #                         existing_order.action_cancel()
                        super(sale_order, existing_order).action_cancel()
            if skip_order and transaction_log_lines:
                job_log_vals = {
                    'transaction_log_ids': transaction_log_lines,
                    'skip_process': skip_order,
                    'application': 'sales',
                    'operation_type': 'import',
                    'message': "Cancelled orders process has not been completed successfully, "
                               "due to cancelled amazon orders processed in odoo.",
                }
                self.env['amazon.process.log.book'].create(job_log_vals)
        return True

    """Check Status of draft order in Amazon and if it is cancel, then cancel that order in Odoo"""

    @api.multi
    def check_cancel_order_in_amazon(self, seller, marketplaceids=[], instance_ids=[]):
        """Create Object for the integrate with amazon"""
        proxy_data = seller.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        auto_process = self._context.get('auto_process', False)
        domain = [('state', '=', 'draft')]
        if instance_ids:
            domain.append(('amz_instance_id', 'in', instance_ids))

        min_draft_order = self.search(domain, limit=1, order='date_order')
        max_draft_order = self.search(domain, limit=1, order='date_order desc')

        if not min_draft_order or not max_draft_order:
            if auto_process:
                return []
            else:
                raise Warning("No draft order found in odoo")

        min_date = datetime.strptime(str(min_draft_order.date_order), "%Y-%m-%d %H:%M:%S")
        max_date = datetime.strptime(str(max_draft_order.date_order), "%Y-%m-%d %H:%M:%S")
        date_ranges = {}
        date_from = min_date
        while date_from < max_date or date_from < datetime.now():
            date_to = date_from + timedelta(days=30)
            if date_to > max_date:
                date_to = max_date
            if date_to > datetime.now():
                date_to = datetime.now()
            date_ranges.update({date_from: date_to})
            date_from = date_from + timedelta(days=31)

        list_of_wrapper = []
        for from_date, to_date in list(date_ranges.items()):
            min_date_str = from_date.strftime("%Y-%m-%dT%H:%M:%S")
            created_after = min_date_str + 'Z'

            max_date_str = to_date.strftime("%Y-%m-%dT%H:%M:%S")
            created_before = max_date_str + 'Z'

            if not marketplaceids:
                instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])
                marketplaceids = tuple([x.market_place_id for x in instances])

            if not marketplaceids:
                if auto_process:
                    return []
                else:
                    raise Warning(
                        "There is no any instance is configured of seller %s" % (seller.name))

            kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                      'auth_token': seller.auth_token and str(seller.auth_token) or False,
                      'app_name': 'amazon_ept',
                      'account_token': account.account_token,
                      'emipro_api': 'check_cancel_order_in_amazon',
                      'dbuuid': dbuuid,
                      'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                                 seller.country_id.code,
                      'proxies': proxy_data,
                      'marketplaceids': marketplaceids,
                      'created_after': created_after,
                      'created_before': created_before, }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)

            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                list_of_wrapper = response.get('result')

            for result in list_of_wrapper:
                self.cancel_draft_sales_order(seller, [result])
                self._cr.commit()

            return list_of_wrapper

    """Import FBA Pending Sales Order From Amazon"""

    @api.multi
    def import_fba_pending_sales_order(self, seller, marketplaceids=[]):
        """Create Object for the integrate with amazon"""
        proxy_data = seller.get_proxy_server()

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        """If Last FBA Sync Time is define then system will take those orders which are created 
        after last import time Otherwise System will take last 30 days orders
        """
        if not marketplaceids:
            instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])
            marketplaceids = tuple([x.market_place_id for x in instances])
        if not marketplaceids:
            raise Warning("There is no any instance is configured of seller %s" % (seller.name))

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'import_fba_pending_sales_order',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'marketplaceids': marketplaceids, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)

        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            result = response.get('result')

        amazon_order_list = []
        #         list_of_wrapper.append(result)
        amazon_order_list = amazon_order_list + self.create_pending_sales_order(seller, [result])
        self._cr.commit()
        next_token = result.get('NextToken', {}).get('value')
        """We have create list of Dictwrapper now we create orders into system"""

        kwargs.update({'next_token': next_token,
                       'emipro_api': 'order_by_next_token', })

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            order_by_next_token = response.get('result')

        for result in order_by_next_token:
            amazon_order_list = amazon_order_list + self.create_pending_sales_order(seller,
                                                                                    [result])
            self._cr.commit()

        return amazon_order_list

    """This Function Create Orders with Draft state into ERP System"""

    @api.multi
    def create_pending_sales_order(self, seller, list_of_wrapper):
        sale_order_line_obj = self.env['sale.order.line']
        instance_obj = self.env['amazon.instance.ept']
        amazon_order_list = []
        amazon_product_obj = self.env['amazon.product.ept']
        marketplace_instance_dict = {}

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        for wrapper_obj in list_of_wrapper:
            orders = []
            if not isinstance(wrapper_obj.get('Orders', {}).get('Order', []), list):
                orders.append(wrapper_obj.get('Orders', {}).get('Order', {}))
            else:
                orders = wrapper_obj.get('Orders', {}).get('Order', [])

            for order in orders:
                amazon_order_ref = order.get('AmazonOrderId', {}).get('value', False)
                if not amazon_order_ref:
                    continue

                marketplace_id = order.get('MarketplaceId', {}).get('value', False)
                instance = marketplace_instance_dict.get(marketplace_id)
                if not instance:
                    instance = instance_obj.search(
                        [('marketplace_id.market_place_id', '=', marketplace_id),
                         ('seller_id', '=', seller.id)])
                    marketplace_instance_dict.update({marketplace_id: instance})
                if not instance:
                    continue
                existing_order = self.search([('amazon_reference', '=', amazon_order_ref),
                                              ('amz_instance_id', '=', instance.id)])
                if existing_order:
                    continue

                """Changes by Dhruvi 
                    default_fba_partner_id fetched according to seller wise"""
                partner_dict = {
                    'invoice_address': instance.seller_id.def_fba_partner_id and
                                       instance.seller_id.def_fba_partner_id.id,
                    'delivery_address': instance.seller_id.def_fba_partner_id and
                                        instance.seller_id.def_fba_partner_id.id,
                    'pricelist_id': instance.pricelist_id and instance.pricelist_id.id}

                kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                          'auth_token': seller.auth_token and str(seller.auth_token) or False,
                          'app_name': 'amazon_ept',
                          'account_token': account.account_token,
                          'emipro_api': 'create_Sale_order',
                          'dbuuid': dbuuid,
                          'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                                     seller.country_id.code,
                          'amazon_order_ref': amazon_order_ref, }

                list_of_orderlines_wrapper = []
                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):
                    raise Warning(response.get('reason'))
                else:
                    list_of_orderlines_wrapper = response.get('result')

                amazon_order = False
                skip_order = False
                message = ''
                log_message = ''
                log_action_type = 'skip_line'
                for order_line_wrapper_obj in list_of_orderlines_wrapper:
                    order_lines = []
                    skip_order = False
                    if not isinstance(
                            order_line_wrapper_obj.get('OrderItems', {}).get('OrderItem',
                                                                             []), list):
                        order_lines.append(
                            order_line_wrapper_obj.get('OrderItems', {}).get('OrderItem',
                                                                             {}))
                    else:
                        order_lines = order_line_wrapper_obj.get('OrderItems', {}).get(
                            'OrderItem', [])

                    message = ''
                    log_message = ''
                    res_id = False
                    model_name = 'amazon.product.ept'
                    transaction_log_lines = []
                    for order_line in order_lines:
                        seller_sku = order_line.get('SellerSKU', {}).get('value', False)
                        domain = [('instance_id', '=', instance.id)]
                        seller_sku and domain.append(('seller_sku', '=', seller_sku))
                        amazon_product = amazon_product_obj.search_amazon_product(instance.id,
                                                                                  seller_sku, 'AFN')

                        if not amazon_product:
                            erp_product = amazon_product_obj.search_product(seller_sku)
                            """
                                If odoo product founds and amazon product not found then no need to 
                                check anything and create new amazon product and create log for that
                                , if odoo product not found then go to check configuration which 
                                action has to be taken for that.
                                
                                There are following situations managed by code. 
                                In any situation log that event and action.
                                
                                1). Amazon product and odoo product not found
                                    => Check seller configuration if allow to create new product 
                                    then create product.
                                    => Enter log details with action.
                                2). Amazon product not found but odoo product is there.
                                    => Created amazon product with log and action.
                            """
                            product_id = False
                            if erp_product:
                                product_id = erp_product.id
                                log_action_type = 'create'
                                message = 'Order is imported with creating new amazon product.'
                                log_message = 'Odoo Product is already exists. System have ' \
                                              'created new Amazon Product %s for %s instance' % (
                                                  seller_sku, instance.name)
                                # log_message = 'Product %s created in amazon->Products->Products for %s instance. Product already exist in Odoo and Amazon.'%(seller_sku, instance.name )
                            elif not seller.create_new_product:
                                skip_order = True
                                message = 'Order is not imported due to product not found issue.'
                                log_action_type = 'skip_line'
                                log_message = 'Product %s not found for %s instance' % (
                                    seller_sku, instance.name)
                            else:
                                log_action_type = 'create'
                                message = 'Order is imported with creating new odoo product.'
                                log_message = 'System have created new Odoo Product %s for %s instance' % (
                                    seller_sku, instance.name)
                                # log_message = 'Product %s created in odoo for %s instance'%
                                # (seller_sku, instance.name )

                            if not skip_order:
                                sku = seller_sku or (
                                        erp_product and erp_product[0].default_code) or False
                                prod_vals = {
                                    'instance_id': instance.id,
                                    'product_asin': order_line.get('ASIN', {}).get('value', False),
                                    'seller_sku': sku,
                                    'type': erp_product and erp_product[0].type or 'product',
                                    'product_id': product_id,
                                    'purchase_ok': True,
                                    'sale_ok': True,
                                    'exported_to_amazon': True,
                                    'fulfillment_by': "AFN",
                                }
                                if not erp_product:
                                    prod_vals.update(
                                        {'name': order_line.get('Title', {}).get('value'),
                                         'default_code': sku})

                                amazon_product = amazon_product_obj.create(prod_vals)
                                if not erp_product:
                                    res_id = amazon_product and \
                                             amazon_product.product_id.id or False
                                    model_name = 'product.product'
                                else:
                                    res_id = amazon_product and amazon_product.id or False

                            log_line_vals = {
                                'model_id': self.env['amazon.transaction.log'].get_model_id(
                                    model_name),
                                'res_id': res_id or 0,
                                'log_type': 'not_found',
                                'action_type': log_action_type,
                                'not_found_value': seller_sku,
                                'user_id': self.env.uid,
                                'skip_record': skip_order,
                                'amazon_order_reference': amazon_order_ref,
                                'message': log_message,
                            }
                            transaction_log_lines.append((0, 0, log_line_vals))

                    if not skip_order:
                        if not amazon_order:
                            order_vals = self.create_sales_order_vals(partner_dict, order, instance)
                            amazon_order = self.create(order_vals)
                            amazon_order_list.append(amazon_order)

                        for order_line in order_lines:
                            sale_order_line_obj.create_sale_order_line(order_line, instance,
                                                                       amazon_order, False)

                    if skip_order or log_action_type == 'create':
                        job_log_vals = {
                            'transaction_log_ids': transaction_log_lines,
                            'skip_process': skip_order,
                            'application': 'sales',
                            'operation_type': 'import',
                            'message': message,
                            'instance_id': instance.id
                        }
                        self.env['amazon.process.log.book'].create(job_log_vals)
        return amazon_order_list

    @api.multi
    def _prepare_invoice(self):
        """We need to Inherit this method to set Amazon instance id in Invoice"""
        res = super(sale_order, self)._prepare_invoice()
        amazon_order = self.env['sale.order'].search(
            [('id', '=', self.id), ('amazon_reference', '!=', False)])
        amazon_order and res.update({
            'amazon_instance_id': amazon_order.amz_instance_id and
                                  amazon_order.amz_instance_id.id or False})
        res.update({'seller_id': self.seller_id.id})
        return res

    @api.multi
    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):
        res = super(sale_order, self).onchange_partner_shipping_id()
        fiscal_position = False
        if self.warehouse_id:
            warehouse = self.warehouse_id
            origin_country_id = warehouse.partner_id and \
                                warehouse.partner_id.country_id and \
                                warehouse.partner_id.country_id.id or False
            origin_country_id = origin_country_id or (
                    warehouse.company_id.partner_id.country_id and
                    warehouse.company_id.partner_id.country_id.id or False)
            fiscal_position = self.env['account.fiscal.position'].with_context(
                {'origin_country_ept': origin_country_id}).get_fiscal_position(self.partner_id.id,
                                                                               self.partner_shipping_id.id)
            self.fiscal_position_id = fiscal_position
        return res

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        warehouse = self.warehouse_id
        if warehouse and self.partner_id:
            origin_country_id = warehouse.partner_id and warehouse.partner_id.country_id and \
                                warehouse.partner_id.country_id.id or False
            origin_country_id = origin_country_id or (
                    warehouse.company_id.partner_id.country_id and
                    warehouse.company_id.partner_id.country_id.id or False)
            fiscal_position_id = self.env['account.fiscal.position'].with_context(
                {'origin_country_ept': origin_country_id}).get_fiscal_position(self.partner_id.id,
                                                                               self.partner_shipping_id.id)
            self.fiscal_position_id = fiscal_position_id

    @api.multi
    def get_header(self, instnace):
        return """<?xml version="1.0"?>
                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                <Header>
                    <DocumentVersion>1.01</DocumentVersion>
                    <MerchantIdentifier>%s</MerchantIdentifier>
                </Header>
                <MessageType>OrderAcknowledgement</MessageType>
             """ % (instnace.merchant_id)

    @api.multi
    def get_message(self, lines, instance, order):
        message_id = 1
        message_str = ''
        message_order_line = ''
        message = """ 
                <Message>
                <MessageID>%s</MessageID>
                <OrderAcknowledgement>
                     <AmazonOrderID>%s</AmazonOrderID>
                     <StatusCode>Failure</StatusCode>  
            """ % (message_id, order.amazon_reference)
        for line in lines:
            message_order_line = """ 
                    <Item> 
                    <AmazonOrderItemCode>%s</AmazonOrderItemCode>
                    <CancelReason>%s</CancelReason>         
                    </Item> 
                """ % (line.sale_line_id.amazon_order_item_id, line.message)
            message = "%s %s" % (message, message_order_line)
            line.sale_line_id.write({'amz_return_reason': line.message})
        message = "%s </OrderAcknowledgement></Message>" % (message)

        message_str = "%s %s" % (message, message_str)
        header = self.get_header(instance)
        message_str = "%s %s </AmazonEnvelope>" % (header, message_str)
        return message_str

    @api.multi
    def send_cancel_request_to_amazon(self, lines, instance, order):
        data = self.get_message(lines, instance, order)
        proxy_data = instance.seller_id.get_proxy_server()

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token': instance.auth_token and str(instance.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'send_cancel_request_to_amazon',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                             instance.country_id.code,
                  'proxies': proxy_data,
                  'marketplaceids': [instance.market_place_id],
                  'instance_id': instance.id,
                  'data': data, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            results = response.get('result')

        if results.get('FeedSubmissionInfo', {}).get('FeedSubmissionId', {}).get('value', False):
            last_feed_submission_id = results.get('FeedSubmissionInfo', {}).get('FeedSubmissionId',
                                                                                {}).get('value',
                                                                                        False)
            vals = {'message': data, 'feed_result_id': last_feed_submission_id,
                    'feed_submit_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'instance_id': instance.id, 'user_id': self._uid,
                    'seller_id': instance.seller_id.id}
            self.env['feed.submission.history'].create(vals)

        return True

    @api.multi
    def cancel_in_amazon(self):
        view = self.env.ref('amazon_ept.view_amazon_cancel_order_wizard')
        context = dict(self._context)
        context.update({'order_id': self.id})
        return {
            'name': _('Cancel Order In Amazon'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amazon.cancel.order.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }

    @api.one
    def _get_amazon_staus(self):
        for order in self:
            if order.picking_ids:
                order.updated_in_amazon = True
            else:
                order.updated_in_amazon = False
            for picking in order.picking_ids:
                if picking.state == 'cancel':
                    continue
                if picking.location_dest_id.usage != 'customer':
                    continue
                if not picking.updated_in_amazon:
                    order.updated_in_amazon = False
                    break

    def _search_order_ids_amazon(self, operator, value):
        # inner join amazon_sale_order_ept on sale_order_id=sale_order.id
        query = """
                    select sale_order.id from stock_picking               
                    inner join sale_order on sale_order.procurement_group_id=stock_picking.group_id
                    inner join stock_location on stock_location.id=stock_picking.location_dest_id and stock_location.usage='customer'                
                    where stock_picking.updated_in_amazon=False and stock_picking.state='done'    
                  """
        self._cr.execute(query)
        results = self._cr.fetchall()
        order_ids = []
        for result_tuple in results:
            order_ids.append(result_tuple[0])
        return [('id', 'in', order_ids)]

    amazon_reference = fields.Char(size=350, string='Amazon Order Ref')

    # commented by dhaval 26-2-2019
    # no more field required
    # amz_send_order_acknowledgment=fields.Boolean("Acknowledgment required ?")

    amz_allow_adjustment = fields.Boolean("Allow Adjustment ?")
    amz_instance_id = fields.Many2one("amazon.instance.ept", "Instance")
    updated_in_amazon = fields.Boolean("Updated In Amazon", compute='_get_amazon_staus',
                                       search='_search_order_ids_amazon', store=False)

    amz_shipment_service_level_category = fields.Selection(
        [('Expedited', 'Expedited'), ('NextDay', 'NextDay'), ('SecondDay', 'SecondDay'),
         ('Standard', 'Standard'), ('FreeEconomy', 'FreeEconomy')],
        "Shipment Service Level Category", default='Standard')

    is_amazon_canceled = fields.Boolean("Canceled In amazon ?", default=False)
    amz_fulfillment_instance_id = fields.Many2one('amazon.instance.ept',
                                                  string="Fulfillment Instance")

    # added by Dhruvi
    seller_id = fields.Many2one("amazon.seller.ept", "Seller")

    # added by dhaval 6-3-2019
    # set order is business or not
    is_business_order = fields.Boolean('Business Order', default=False)

    """Import Sales Order From Amazon"""

    @api.multi
    def import_sales_order(self, seller, marketplaceids=[], updated_before='', updated_after=''):
        """Create Object for the integrate with amazon"""
        proxy_data = seller.get_proxy_server()
        log_book_obj = self.env['amazon.process.log.book']
        orderstatus = ('Unshipped', 'PartiallyShipped')

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        transaction_log_obj = self.env['amazon.transaction.log']
        model_id = transaction_log_obj.get_model_id('sale.order')
        log_rec = False

        """If Last Sync Time is definds then system will take those orders which are 
        created after last import time Otherwise System will take last 30 days orders
        """
        if not updated_after:
            if seller.order_last_sync_on:
                earlier_str = seller.order_last_sync_on - timedelta(
                    int(seller.last_import_fbm_order_days) or 0)
                earlier_str = earlier_str.strftime("%Y-%m-%dT%H:%M:%S")
                updated_after = earlier_str
            else:
                today = datetime.now()
                earlier = today - timedelta(days=30)
                earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
                updated_after = earlier_str

        """
        Add 'LastUpdatedBefore' in request of FBM orders
        It will not be search order on current time so deducted with 2 minutes
        @author: Deval Jagad (30/12/2019)
        """
        if not updated_before:
            updated_before = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")

        if not marketplaceids:
            instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])
            marketplaceids = tuple(map(lambda x: x.market_place_id, instances))
        if not marketplaceids:
            raise Warning("There is no any instance is configured of seller %s" % (seller.name))

        """Call List Order Method Of Amazon Api for the Read Orders and 
        API give response in DictWrapper"""
        if seller.import_shipped_fbm_orders:
            orderstatus = orderstatus + ('Shipped',)

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'import_sales_order',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'marketplaceids': marketplaceids,
                  'updated_after': updated_after,
                  'updated_before': updated_before,
                  'orderstatus': orderstatus, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                log_vals = {
                    'application': 'sales',
                    'operation_type': 'import',
                }
                log_rec = log_book_obj.create(log_vals)
            else:
                raise Warning(response.get('reason'))

            transaction_vals = {'model_id': model_id,
                                'log_type': 'error',
                                'action_type': 'terminate_process_with_log',
                                'message': response.get('reason'),
                                'job_id': log_rec.id, }
            transaction_log_obj.create(transaction_vals)
        else:

            result = response.get('result')
            """
            Update Last Sync FBM order before processing order
            @author: Deval Jagad (30/12/2019)
            """
            self.create_sales_order(seller, [result])
            self._cr.commit()
            next_token = result.get('NextToken', {}).get('value')

            kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                      'auth_token': seller.auth_token and str(seller.auth_token) or False,
                      'app_name': 'amazon_ept',
                      'account_token': account.account_token,
                      'emipro_api': 'order_by_next_token',
                      'dbuuid': dbuuid,
                      'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                                 seller.country_id.code,
                      'proxies': proxy_data,
                      'next_token': next_token,
                      }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                order_by_next_token = response.get('result')
                for result in order_by_next_token:
                    self.create_sales_order(seller, [result])
                    self._cr.commit()
                    """We have create list of Dictwrapper now we create orders into system"""

        return True

    """This Function Create Orders into ERP System"""

    @api.multi
    def create_sales_order(self, seller, list_of_wrapper):
        sale_line_obj = self.env['sale.order.line']
        instance_obj = self.env['amazon.instance.ept']
        auto_work_flow_obj = self.env['sale.workflow.process.ept']
        stock_move_line_obj = self.env['stock.move.line']
        amazon_product_obj = self.env['amazon.product.ept']
        stock_immediate_transfer_obj = self.env['stock.immediate.transfer']
        shipped_orders = []
        marketplace_instance_dict = {}
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        for wrapper_obj in list_of_wrapper:
            orders = []
            if not isinstance(wrapper_obj.get('Orders', {}).get('Order', []), list):
                orders.append(wrapper_obj.get('Orders', {}).get('Order', {}))
            else:
                orders = wrapper_obj.get('Orders', {}).get('Order', [])
            for order in orders:
                amazon_order_ref = order.get('AmazonOrderId', {}).get('value', False)
                if not amazon_order_ref:
                    continue
                marketplace_id = order.get('MarketplaceId', {}).get('value', False)
                instance = marketplace_instance_dict.get(marketplace_id)
                if not instance:
                    instance = instance_obj.search(
                        [('marketplace_id.market_place_id', '=', marketplace_id),
                         ('seller_id', '=', seller.id)])
                    marketplace_instance_dict.update({marketplace_id: instance})
                if not instance:
                    continue
                existing_order = self.search([('amazon_reference', '=', amazon_order_ref),
                                              ('amz_instance_id', '=', instance.id)])
                if existing_order:
                    continue
                instance = instance[0]
                fulfillment_channel = order.get('FulfillmentChannel', {}).get('value', False)
                if fulfillment_channel and fulfillment_channel == 'AFN' and not hasattr(instance,
                                                                                        'fba_warehouse_id'):
                    continue
                order_status = order.get('OrderStatus', {}).get('value', False)
                if order_status == 'Shipped':
                    shipped_orders.append(amazon_order_ref)
                partner_dict = self.create_or_update_partner_amazon(order, instance)

                kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                          'auth_token': seller.auth_token and str(seller.auth_token) or False,
                          'app_name': 'amazon_ept',
                          'account_token': account.account_token,
                          'emipro_api': 'create_Sale_order',
                          'dbuuid': dbuuid,
                          'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                                     seller.country_id.code,
                          'amazon_order_ref': amazon_order_ref, }

                list_of_orderlines_wrapper = []
                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):
                    raise Warning(response.get('reason'))
                else:
                    list_of_orderlines_wrapper = response.get('result')

                amazon_order = False
                skip_order = False
                message = ''
                log_message = ''
                log_action_type = 'skip_line'
                for order_line_wrapper_obj in list_of_orderlines_wrapper:
                    order_lines = []
                    skip_order = False
                    if not isinstance(
                            order_line_wrapper_obj.get('OrderItems', {}).get('OrderItem',
                                                                             []), list):
                        order_lines.append(
                            order_line_wrapper_obj.get('OrderItems', {}).get('OrderItem',
                                                                             {}))
                    else:
                        order_lines = order_line_wrapper_obj.get('OrderItems', {}).get(
                            'OrderItem', [])

                    message = ''
                    log_message = ''
                    res_id = False
                    model_name = 'amazon.product.ept'
                    transaction_log_lines = []
                    for order_line in order_lines:
                        seller_sku = order_line.get('SellerSKU', {}).get('value', False)
                        domain = [('amz_instance_id', '=', instance.id)]
                        seller_sku and domain.append(('seller_sku', '=', seller_sku))
                        amazon_product = amazon_product_obj.search_amazon_product(instance.id,
                                                                                  seller_sku, 'MFN')

                        if not amazon_product:
                            erp_product = amazon_product_obj.search_product(seller_sku)
                            """
                                If odoo product founds and amazon product not found then no need to 
                                check anything and create new amazon product and create log for that, 
                                if odoo product not found then go to check configuration which 
                                action has to be taken for that.
                                
                                There are following situations managed by code. 
                                In any situation log that event and action.
                                
                                1). Amazon product and odoo product not found
                                    => Check seller configuration if allow to create new product 
                                        then create product.
                                    => Enter log details with action.
                                2). Amazon product not found but odoo product is there.
                                    => Created amazon product with log and action.
                            """
                            product_id = False
                            if erp_product:
                                product_id = erp_product.id
                                log_action_type = 'create'
                                message = 'Order is imported with creating new amazon product.'
                                log_message = 'Odoo Product is already exists. System have created ' \
                                              'new Amazon Product %s for %s instance' % (seller_sku, instance.name)
                                # log_message = 'Product %s created in amazon->Products->Products
                                # for %s instance. Product already exist in Odoo and Amazon.'
                                # %(seller_sku, instance.name )
                            elif not seller.create_new_product:
                                skip_order = True
                                message = 'Order is not imported due to product not found issue.'
                                log_action_type = 'skip_line'
                                log_message = 'Product %s not found for %s instance' % (
                                    seller_sku, instance.name)
                            else:
                                log_action_type = 'create'
                                message = 'Order is imported with creating new odoo product.'
                                log_message = 'System have created new Odoo Product %s for %s instance' % (
                                    seller_sku, instance.name)
                                # log_message = 'Product %s created in odoo for %s instance'%(seller_sku, instance.name )

                            if not skip_order:
                                sku = seller_sku or (
                                        erp_product and erp_product[0].default_code) or False
                                prod_vals = {
                                    'instance_id': instance.id,
                                    'product_asin': order_line.get('ASIN', {}).get('value', False),
                                    'seller_sku': sku,
                                    'type': erp_product and erp_product[0].type or 'product',
                                    'product_id': product_id,
                                    'purchase_ok': True,
                                    'sale_ok': True,
                                    'exported_to_amazon': True,
                                    'fulfillment_by': fulfillment_channel,
                                }
                                if not erp_product:
                                    prod_vals.update(
                                        {'name': order_line.get('Title', {}).get('value'),
                                         'default_code': sku})

                                amazon_product = amazon_product_obj.create(prod_vals)
                                if not erp_product:
                                    res_id = amazon_product and \
                                             amazon_product.product_id.id or False
                                    model_name = 'product.product'
                                else:
                                    res_id = amazon_product and amazon_product.id or False

                            log_line_vals = {
                                'model_id': self.env['amazon.transaction.log'].get_model_id(
                                    model_name),
                                'res_id': res_id or 0,
                                'log_type': 'not_found',
                                'action_type': log_action_type,
                                'not_found_value': seller_sku,
                                'user_id': self.env.uid,
                                'skip_record': skip_order,
                                'message': log_message,
                                'amazon_order_reference': amazon_order_ref,
                            }
                            transaction_log_lines.append((0, 0, log_line_vals))

                    if not skip_order:
                        if not amazon_order:
                            order_vals = self.create_sales_order_vals(partner_dict, order, instance)
                            amazon_order = self.create(order_vals)
                        for order_line in order_lines:
                            sale_line_obj.create_sale_order_line(order_line, instance, amazon_order)
                        if amazon_order:
                            """Changes by Dhruvi auto_workflow_id is fetched according to seller wise."""
                            auto_work_flow_obj.auto_workflow_process(
                                instance.seller_id.auto_workflow_id.id, [amazon_order.id])
                            if amazon_order.amazon_reference in shipped_orders:
                                if amazon_order.state == 'draft':
                                    amazon_order.action_confirm()
                                for picking in amazon_order.picking_ids:
                                    if picking.state in ['waiting', 'confirmed']:
                                        picking.action_assign()
                                    if picking.state == 'assigned':
                                        stock_immediate_transfer_obj.create(
                                            {'pick_ids': [(4, picking.id)]}).process()
                                    elif picking.state in ['confirmed', 'partially_available']:
                                        for move in picking.move_lines:
                                            if move.state in ['confirmed', 'partially_available']:
                                                remaining_qty = move.product_uom_qty - move.reserved_availability
                                                if remaining_qty > 0.0:
                                                    stock_move_line_obj.create(
                                                        {
                                                            'product_id': move.product_id.id,
                                                            'product_uom_id': move.product_id.uom_id.id,
                                                            'picking_id': picking.id,
                                                            'qty_done': float(remaining_qty) or 0,
                                                            'location_id': picking.location_id.id,
                                                            'location_dest_id': picking.location_dest_id.id,
                                                            'move_id': move.id,
                                                        })

                                        picking.with_context(
                                            {'auto_processed_orders_ept': True}).action_done()
                                    picking.write({'updated_in_amazon': True})

                    if skip_order or log_action_type == 'create':
                        job_log_vals = {
                            'transaction_log_ids': transaction_log_lines,
                            'skip_process': skip_order,
                            'application': 'sales',
                            'operation_type': 'import',
                            'message': message,
                            'instance_id': instance.id
                        }
                        self.env['amazon.process.log.book'].create(job_log_vals)
        return True

    @api.multi
    def create_sales_order_vals(self, partner_dict, order, instance):
        delivery_carrier_obj = self.env['delivery.carrier']
        sale_order_obj = self.env['sale.order']
        fpos = instance.fiscal_position_id and instance.fiscal_position_id.id or False
        shipping_category = order.get('ShipmentServiceLevelCategory', {}).get('value', False)
        date_order = False
        if order.get('PurchaseDate', {}).get('value', False):
            date_order = parser.parse(
                order.get('PurchaseDate', False).get('value', False)).astimezone(utc).strftime(
                '%Y-%m-%d %H:%M:%S')
        else:
            date_order = time.strftime('%Y-%m-%d %H:%M:%S')

        is_business_order = order.get('IsBusinessOrder', {}).get('value', False)
        if is_business_order:
            if is_business_order.lower() == 'true' or is_business_order.lower() == 't':
                is_business_order = True

            else:
                is_business_order = False

        vals = {'company_id': instance.company_id.id,
                'partner_id': partner_dict.get('invoice_address'),
                'partner_invoice_id': partner_dict.get('invoice_address'),
                'partner_shipping_id': partner_dict.get('delivery_address'),
                'warehouse_id': instance.warehouse_id.id, 'picking_policy': instance.picking_policy,
                'date_order': date_order,
                'pricelist_id': instance.pricelist_id.id,
                'payment_term_id': instance.seller_id.payment_term_id.id,
                'fiscal_position_id': fpos, 'invoice_policy': instance.invoice_policy or False,
                'team_id': instance.team_id and instance.team_id.id or False,
                'client_order_ref': order.get('AmazonOrderId', {}).get('value', False),
                'carrier_id': False, 'invoice_shipping_on_delivery': False
                }

        ordervals = sale_order_obj.create_sales_order_vals_ept(vals)
        ordervals.update(
            {
                'auto_workflow_process_id': instance.seller_id.auto_workflow_id.id or False,
                'amz_instance_id': instance and instance.id or False,
                'amz_fulfillment_by': 'MFN',
                'amazon_reference': order.get('AmazonOrderId', {}).get('value', False),
                'amz_shipment_service_level_category': shipping_category,
                'global_channel_id': instance.seller_id and instance.seller_id.global_channel_id and
                                     instance.seller_id.global_channel_id.id or False,
                'seller_id': instance.seller_id and instance.seller_id.id or False,
                'is_business_order': is_business_order or False
            })

        carrier = delivery_carrier_obj.search([
            ('shipping_service_level_category', '=', shipping_category)], limit=1)
        ordervals.update({'carrier_id': carrier.id})
        fulfillment_channel = order.get('FulfillmentChannel', {}).get('value', False)
        #Apply FBM or FBA Order prefix according to Fulfillment Channel
        if not instance.seller_id.is_default_odoo_sequence_in_sales_order:
            prefix = False
            if fulfillment_channel and instance.seller_id:
                prefix = instance.seller_id.fba_order_prefix if fulfillment_channel == 'AFN' else instance.seller_id.order_prefix
            if prefix:
                ordervals.update({'name': "%s%s" % (prefix + '_' or '', order.get('AmazonOrderId', {}).get('value'))})
            else:
                ordervals.update({'name': order.get('AmazonOrderId', {}).get('value')})
        if fulfillment_channel and fulfillment_channel == 'AFN':
            """Changes by Dhruvi fba_auto_workflow_id is fetched according to seller wise"""
            workflow = instance.seller_id.fba_auto_workflow_id or instance.seller_id.auto_workflow_id
            ordervals.update({
                'warehouse_id': instance.fba_warehouse_id and
                                instance.fba_warehouse_id.id or
                                instance.warehouse_id.id,
                'auto_workflow_process_id': workflow.id,
                'amz_fulfillment_by': 'AFN',
                'picking_policy': workflow.picking_policy,
                'invoice_policy': workflow.invoice_policy or False,
                'seller_id': instance.seller_id and instance.seller_id.id or False,
                'global_channel_id': instance.seller_id and
                                     instance.seller_id.global_channel_id and
                                     instance.seller_id.global_channel_id.id or False
            })
        return ordervals

    @api.multi
    def create_or_update_partner_amazon(self, order, instance):
        address_info = order.get('ShippingAddress')
        partner_obj = self.env['res.partner']
        return_partner = {}

        partner_id = instance.partner_id and instance.partner_id.id or False
        country_code = address_info.get('CountryCode', {}).get('value', instance.country_id.code)
        state = address_info.get('StateOrRegion', {}).get('value', False)
        state = state and state.capitalize()

        street = address_info.get('AddressLine1', {}).get('value', False)
        street2 = address_info.get('AddressLine2', {}).get('value', False)
        email_id = order.get('BuyerEmail', {}).get('value', False)
        postalcode = address_info.get('PostalCode', {}).get('value', False)
        inv_cust_name = order.get('BuyerName', {}).get('value', False)
        deliv_cust_name = address_info.get('Name', {}).get('value', False)

        phone = address_info.get('Phone', {}).get('value', False)
        city = address_info.get('City', {}).get('value', False)
        if street and street == order.get('BuyerName', {}).get(
                'value') or street == address_info.get('Name', {}).get('value'):
            street = False

        domain = []
        street and domain.append(('street'))
        street2 and domain.append(('street2'))
        email_id and domain.append(('email'))
        phone and domain.append(('phone'))
        city and domain.append(('city'))
        postalcode and domain.append(('zip'))
        state and domain.append(('state_id'))
        country_code and domain.append(('country_id'))
        deliv_cust_name and domain.append(('name'))

        vals = {
            'state_code': state or False,
            'state_name': state or False,
            'country_code': country_code,
            'country_name': country_code,
            'name': deliv_cust_name,
            'parent_id': partner_id,
            'street': street,
            'street2': street2,
            'city': city,
            'phone': phone,
            'email': email_id,
            'zip': postalcode,
            'lang': instance.lang_id and instance.lang_id.code,
            'company_id': instance.company_id.id,
            'type': False,
            'is_company': False
        }

        partnervals = self._prepare_amazon_partner_vals(vals)
        partnervals.update({'customer': not bool(partner_id)})

        if instance.amazon_property_account_payable_id:
            partnervals.update({'property_account_payable_id': instance.amazon_property_account_payable_id.id})

        if instance.amazon_property_account_receivable_id:
            partnervals.update({'property_account_receivable_id': instance.amazon_property_account_receivable_id.id})

        if instance.customer_is_company and not partner_id:
            partnervals.update({'is_company': True})

        add_name_same = False
        if deliv_cust_name.lower() == inv_cust_name.lower():
            add_name_same = True

        exist_partner = partner_obj._find_partner(partnervals, domain)
        if exist_partner:
            exist_partner = exist_partner[0]

            if instance.amazon_property_account_payable_id:
                exist_partner.update({'property_account_payable_id': instance.amazon_property_account_payable_id.id})

            if instance.amazon_property_account_receivable_id:
                exist_partner.update(
                    {'property_account_receivable_id': instance.amazon_property_account_receivable_id.id})

            return_partner.update({'invoice_address': exist_partner.id,
                                   'property_product_pricelist': exist_partner.property_product_pricelist.id,
                                   'delivery_address': exist_partner.id, 'type': 'delivery'})
        else:
            partnervals.update({'type': 'delivery', 'name': deliv_cust_name})
            if 'message_follower_ids' in partnervals:
                del partnervals['message_follower_ids']
            exist_partner = partner_obj.create(partnervals)
            exist_partner and return_partner.update({'invoice_address': exist_partner.id,
                                                     'property_product_pricelist': exist_partner.property_product_pricelist.id,
                                                     'delivery_address': exist_partner.id})

        if not add_name_same:

            partnervals.update({'name': inv_cust_name})

            exist_invoice_partner = partner_obj._find_partner(partnervals, domain)
            if exist_invoice_partner:
                exist_invoice_partner = exist_invoice_partner[0]

                property_account_vals = {}
                if instance.amazon_property_account_payable_id:
                    property_account_vals.update(
                        {'property_account_payable_id': instance.amazon_property_account_payable_id.id or False})

                if instance.amazon_property_account_receivable_id:
                    property_account_vals.update(
                        {'property_account_receivable_id': instance.amazon_property_account_receivable_id.id or False})

                property_account_vals.update({'type': 'invoice'})
                exist_invoice_partner.write(property_account_vals)
                return_partner.update({'invoice_address': exist_invoice_partner.id})
            else:
                partnervals.update({'type': 'invoice', 'name': inv_cust_name})
                if 'message_follower_ids' in partnervals:
                    del partnervals['message_follower_ids']
                exist_invoice_partner = partner_obj.create(partnervals)
                exist_invoice_partner and return_partner.update(
                    {'invoice_address': exist_invoice_partner.id})
            if not instance.customer_is_company and not partner_id:
                exist_invoice_partner.write({'is_company': True})
            exist_partner.write({'is_company': False, 'parent_id': exist_invoice_partner.id})
        return return_partner

    @api.multi
    def get_qty_for_phantom_type_products(self, order, picking, order_ref, carrier_name,
                                          shipping_level_category, message_id,
                                          fulfillment_date_concat):
        message_information = ''
        move_obj = self.env['stock.move']
        update_move_ids = []
        picking_ids = order.picking_ids.ids
        moves = move_obj.search(
            [('picking_id', 'in', picking_ids), ('picking_type_id.code', '!=', 'incoming'),
             ('state', 'not in', ['draft', 'cancel']), ('updated_in_amazon', '=', False)])
        phantom_product_dict = {}
        for move in moves:
            if move.sale_line_id.product_id.id != move.product_id.id:
                if move.sale_line_id in phantom_product_dict and move.product_id.id not in phantom_product_dict.get(
                        move.sale_line_id):
                    phantom_product_dict.get(move.sale_line_id).append(move.product_id.id)
                else:
                    phantom_product_dict.update({move.sale_line_id: [move.product_id.id]})
        for sale_line_id, product_ids in phantom_product_dict.items():
            parcel = {}
            moves = move_obj.search(
                [('picking_id', 'in', picking_ids), ('state', 'in', ['draft', 'cancel']),
                 ('product_id', 'in', product_ids)])
            if not moves:
                moves = move_obj.search([('picking_id', 'in', picking_ids), ('state', '=', 'done'),
                                         ('product_id', 'in', product_ids),
                                         ('updated_in_amazon', '=', False)])
                tracking_no = picking.carrier_tracking_ref
                for move in moves:
                    if not tracking_no:
                        for move_line in move.move_line_ids:
                            tracking_no = move_line.result_package_id and \
                                          move_line.result_package_id.tracking_no or False
                update_move_ids += moves.ids
                amazon_order_line = sale_line_id  # get_amazon_sale_line(moves[0])
                amazon_order_item_id = sale_line_id.amazon_order_item_id

                product_qty = sale_line_id.product_qty
                if amazon_order_line and amazon_order_line.amazon_product_id and \
                        amazon_order_line.amazon_product_id.allow_package_qty:
                    asin_qty = amazon_order_line.amazon_product_id.asin_qty
                    if asin_qty != 0:
                        product_qty = product_qty / asin_qty
                product_qty = int(product_qty)
                parcel.update({
                    'tracking_no': tracking_no or '',
                    'qty': product_qty,
                    'amazon_order_item_id': amazon_order_item_id,
                    'order_ref': order_ref,
                    'carrier_name': carrier_name,
                    'shipping_level_category': shipping_level_category
                })
                message_information += self.create_parcel_for_multi_tracking_number(parcel,
                                                                                    message_id,
                                                                                    fulfillment_date_concat)
                message_id = message_id + 1
        return message_information, message_id, update_move_ids

    @api.multi
    def create_parcel_for_multi_tracking_number(self, parcel, message_id, fulfillment_date_concat):
        message_information = ''
        carrier_information = ''
        if parcel.get('carrier_code'):
            carrier_information = '''<CarrierCode>%s</CarrierCode>''' % (parcel.get('carrier_code'))
        else:
            carrier_information = '''<CarrierName>%s</CarrierName>''' % (parcel.get('carrier_name'))
        item_string = '''<Item>
                                <AmazonOrderItemCode>%s</AmazonOrderItemCode>
                                <Quantity>%s</Quantity>
                          </Item>''' % (parcel.get('amazon_order_item_id'), parcel.get('qty', 0))
        message_information += """<Message>
                                        <MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <OrderFulfillment>
                                            <AmazonOrderID>%s</AmazonOrderID>
                                            <FulfillmentDate>%s</FulfillmentDate>
                                            <FulfillmentData>
                                                %s
                                                <ShippingMethod>%s</ShippingMethod>
                                                <ShipperTrackingNumber>%s</ShipperTrackingNumber>
                                            </FulfillmentData>
                                            %s
                                        </OrderFulfillment>
                                    </Message>""" % (
            str(message_id), parcel.get('order_ref'), fulfillment_date_concat,
            carrier_information, parcel.get('shipping_level_category'),
            parcel.get('tracking_no'), item_string)
        return message_information

    @api.multi
    def create_parcel_for_single_tracking_number(self, parcel, message_id, fulfillment_date_concat):
        message_information = ''
        carrier_information = ''
        if parcel.get('carrier_code'):
            carrier_information = '''<CarrierCode>%s</CarrierCode>''' % (parcel.get('carrier_code'))
        else:
            carrier_information = '''<CarrierName>%s</CarrierName>''' % (parcel.get('carrier_name'))
        message_information += """<Message>
                                        <MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <OrderFulfillment>
                                            <AmazonOrderID>%s</AmazonOrderID>
                                            <FulfillmentDate>%s</FulfillmentDate>
                                            <FulfillmentData>
                                                %s
                                                <ShippingMethod>%s</ShippingMethod>
                                                <ShipperTrackingNumber>%s</ShipperTrackingNumber>
                                            </FulfillmentData>
                                        </OrderFulfillment>
                                    </Message>""" % (
            str(message_id), parcel.get('order_ref'), fulfillment_date_concat,
            carrier_information, parcel.get('shipping_level_category'),
            parcel.get('tracking_no'))
        return message_information

    @api.multi
    def create_data(self, message_information, merchant_id):
        data = """<?xml version="1.0" encoding="utf-8"?>
                        <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                            <Header>
                                <DocumentVersion>1.01</DocumentVersion>
                                    <MerchantIdentifier>%s</MerchantIdentifier>
                            </Header>
                        <MessageType>OrderFulfillment</MessageType>""" % (
            merchant_id) + message_information + """
                        </AmazonEnvelope>"""

        return data

    @api.model
    def check_already_status_updated_in_amazon(self, seller, marketplaceids):
        """Create Object for the integrate with amazon"""
        proxy_data = seller.get_proxy_server()

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])
        warehouse_ids = list(set(map(lambda x: x.warehouse_id.id, instances)))
        
        sales_orders = self.search([('warehouse_id', 'in', warehouse_ids),
                                    ('amazon_reference', '!=', False),
                                    ('amz_instance_id', 'in', instances.ids),
                                    ('updated_in_amazon', '=', False),
                                    ('amz_fulfillment_by', '=', 'MFN'),
                                    ], order='date_order')
        if not sales_orders:
            return []

        if not marketplaceids:
            marketplaceids= tuple(map(lambda x: x.market_place_id,sales_orders.mapped('amz_instance_id')))
        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'check_already_status_updated_in_amazon',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'marketplaceids': marketplaceids, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            list_of_wrapper = response.get('result')
        list_of_amazon_order_ref = []
        if list_of_wrapper:
            for wrapper_obj in list_of_wrapper:
                orders = []
                if not isinstance(wrapper_obj.get('Orders', {}).get('Order', []), list):
                    orders.append(wrapper_obj.get('Orders', {}).get('Order', {}))
                else:
                    orders = wrapper_obj.get('Orders', {}).get('Order', [])
                for order in orders:
                    amazon_order_ref = order.get('AmazonOrderId', {}).get('value', False)
                    list_of_amazon_order_ref.append(amazon_order_ref)
        unshipped_sales_orders = []
        for order in sales_orders:
            if order.amazon_reference not in list_of_amazon_order_ref:
                order.picking_ids.write({'updated_in_amazon': True})
        _logger.info(list_of_amazon_order_ref)
        _logger.info(instances)
        unshipped_sales_orders=self.search([('amazon_reference','in',list_of_amazon_order_ref),
                                            ('amz_instance_id', 'in', instances.ids),
                                            ('amz_fulfillment_by', '=', 'MFN'),])
        return unshipped_sales_orders

    """Update Order Status into Amazon
            Consider Cases....!!!!
            1.Partial shipment
            2.Same Carrier With More then one tracking no
            3.Same Carrier and Same Product with more then one tracking no    
    """

    @api.multi
    def amz_update_order_status(self, seller, marketplaceids=[]):
        proxy_data = seller.get_proxy_server()
        carrier_name, order_ref = False, False
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        log_book_obj = self.env['amazon.process.log.book']
        transaction_log_obj = self.env['amazon.transaction.log']
        model_id = transaction_log_obj.get_model_id('sale.order')
        log_rec = False

        """Check If Order already shipped in the amazon then we will skip that all orders and 
            set update_into_amazon=True 
        """
        amazon_orders = self.check_already_status_updated_in_amazon(seller, marketplaceids)
        if not amazon_orders:
            return []
        marketplaceids= tuple(map(lambda x: x.market_place_id,amazon_orders.mapped('amz_instance_id')))
        parcel = {}
        shipment_pickings = []
        message_information = ""
        message_id = 1
        updated_picking_wize_move_lines = {}

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        for amazon_order in amazon_orders:
            for picking in amazon_order.picking_ids:
                """Here We Take only done picking and  updated in amazon false"""
                if (picking.updated_in_amazon and amazon_order.picking_ids.filtered(lambda l:l.backorder_id.id==picking.id)) or picking.state != 'done' or picking.location_dest_id.usage != 'customer':
                    continue
                if picking.date_done:
                    fulfillment_date = time.strptime(str(picking.date_done), "%Y-%m-%d %H:%M:%S")
                    fulfillment_date = time.strftime("%Y-%m-%dT%H:%M:%S", fulfillment_date)
                else:
                    fulfillment_date = time.strftime('%Y-%m-%dT%H:%M:%S')
                fulfillment_date_concat = str(fulfillment_date) + '-00:00'
                shipment_pickings.append(picking.id)
                order_ref = amazon_order.amazon_reference
                carrier_name = picking.carrier_id and \
                               picking.carrier_id.amz_delivery_carrier_code and \
                               picking.carrier_id.amz_delivery_carrier_code.name or \
                               picking.carrier_id.name

                shipping_level_category = amazon_order.amz_shipment_service_level_category
                if picking.carrier_tracking_ref:
                    manage_multi_tracking_number_in_delivery_order = False
                else:
                    manage_multi_tracking_number_in_delivery_order = True
                if not shipping_level_category:
                    continue
                if not manage_multi_tracking_number_in_delivery_order:
                    tracking_no = picking.carrier_tracking_ref
                    parcel.update({
                        'tracking_no': tracking_no or '',
                        'order_ref': order_ref,
                        'carrier_name': carrier_name or '',
                        'shipping_level_category': shipping_level_category
                    })
                    message_information += self.create_parcel_for_single_tracking_number(parcel,
                                                                                         message_id,
                                                                                         fulfillment_date_concat)
                    message_id = message_id + 1
                    updated_picking_wize_move_lines.update({picking.id: picking.move_lines.ids})
                else:
                    """Create message for bom type products"""
                    phantom_msg_info, message_id, update_move_ids = self.get_qty_for_phantom_type_products(
                        amazon_order, picking, order_ref, carrier_name, shipping_level_category,
                        message_id, fulfillment_date_concat)
                    if phantom_msg_info:
                        message_information += phantom_msg_info
                    update_move_ids and updated_picking_wize_move_lines.update(
                        {picking.id: update_move_ids})
                    """Create Message for each move"""
                    for move in picking.move_lines:
                        if move in update_move_ids or move.sale_line_id.product_id.id != move.product_id.id:
                            continue
                        if picking.id in updated_picking_wize_move_lines:
                            updated_picking_wize_move_lines.get(picking.id).append(move.id)
                        else:
                            updated_picking_wize_move_lines.update({picking.id: move.ids})
                        amazon_order_line = move.sale_line_id  # get_amazon_sale_line(moves[0])
                        amazon_order_item_id = move.sale_line_id.amazon_order_item_id
                        """Create Package for the each parcel"""
                        tracking_no_with_qty = {}
                        product_qty = 0.0
                        for move_line in move.move_line_ids:
                            if move_line.qty_done < 0.0:
                                continue
                            tracking_no = move_line.result_package_id and move_line.result_package_id.tracking_no or 'UNKNOWN'
                            quantity = tracking_no_with_qty.get(tracking_no, 0.0)
                            quantity = quantity + move_line.qty_done
                            tracking_no_with_qty.update({tracking_no: quantity})
                        for tracking_no, product_qty in tracking_no_with_qty.items():
                            if tracking_no == 'UNKNOWN':
                                tracking_no = ''
                            if amazon_order_line and amazon_order_line.amazon_product_id and amazon_order_line.amazon_product_id.allow_package_qty:
                                asin_qty = amazon_order_line.amazon_product_id.asin_qty
                                if asin_qty != 0:
                                    product_qty = product_qty / asin_qty
                            product_qty = int(product_qty)
                            parcel.update({
                                'tracking_no': tracking_no or '',
                                'qty': product_qty,
                                'amazon_order_item_id': amazon_order_item_id,
                                'order_ref': order_ref,
                                'carrier_name': carrier_name,
                                'shipping_level_category': shipping_level_category
                            })
                            message_information += self.create_parcel_for_multi_tracking_number(
                                parcel, message_id, fulfillment_date_concat)
                            message_id = message_id + 1
        if not message_information:
            return True
        data = self.create_data(message_information, str(seller.merchant_id))

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'amz_update_order_status',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'data': data,
                  'marketplaceids': marketplaceids}

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            if not log_rec:
                log_vals = {
                    'application': 'sales',
                    'instance_id': self.amz_instance_id.id,
                    'operation_type': 'export',
                }
                log_rec = log_book_obj.create(log_vals)

            transaction_vals = {'model_id': model_id,
                                'log_type': 'error',
                                'action_type': 'skip_line',
                                'message': response.get('reason'),
                                'job_id': log_rec.id, }
            transaction_log_obj.create(transaction_vals)
        else:
            results = response.get('result',{})
            if results.get('FeedSubmissionInfo', {}).get('FeedSubmissionId', {}).get('value',
                                                                                     False):
                last_feed_submission_id = results.get('FeedSubmissionInfo', {}).get(
                    'FeedSubmissionId',
                    {}).get('value',
                            False)

                feed_vals = {'message': data.encode('utf-8'), 'feed_result_id': last_feed_submission_id,
                             'feed_submit_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                             'instance_id': False, 'seller_id': seller.id, 'user_id': self.env.user.id}
                self.env['feed.submission.history'].create(feed_vals)

                kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                          'auth_token': seller.auth_token and str(seller.auth_token) or False,
                          'app_name': 'amazon_ept',
                          'account_token': account.account_token,
                          'emipro_api': 'get_feed_submission_result',
                          'dbuuid': dbuuid,
                          'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                                     seller.country_id.code,
                          'proxies': proxy_data,
                          'last_feed_submission_id': last_feed_submission_id}

                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                submission_results = {}
                if response.get('reason'):
                    if not log_rec:
                        log_vals = {
                            'application': 'sales',
                            'instance_id': self.amz_instance_id.id,
                            'operation_type': 'export',
                        }
                        log_rec = log_book_obj.create(log_vals)

                    transaction_vals = {'model_id': model_id,
                                        'log_type': 'error',
                                        'message': response.get('reason'),
                                        'job_id': log_rec.id, }
                    transaction_log_obj.create(transaction_vals)
                else:
                    submission_results = response.get('result',{})
                    error = submission_results._response_dict.get('Message', {}).get('ProcessingReport',
                                                                                     {}).get(
                        'ProcessingSummary', {}).get('MessagesWithError', {}).get('value', '1')
                    if error == '0':
                        pickings = picking_obj.search([('id', 'in', shipment_pickings)])
                        for picking in pickings:
                            move_ids = updated_picking_wize_move_lines.get(picking.id)
                            move_obj.browse(move_ids).write({'updated_in_amazon': True})
                            moves = move_obj.search(
                                [('picking_id', '=', picking.id), ('updated_in_amazon', '=', False)])
                            if not moves:
                                picking.write({'updated_in_amazon': True})
                    else:
                        self.check_already_status_updated_in_amazon(seller, marketplaceids)
        return True

    """Added by twinkal to prepared requested dict for created outbound order and
       update fulfilment order @date : 20 december 2019"""

    def get_data(self):
        currency_code = self.amz_instance_id.company_id.currency_id.name

        data = {}
        data.update({
            'SellerFulfillmentOrderId': self.name,
            'DisplayableOrderId': self.amazon_reference,
            'ShippingSpeedCategory': self.amz_shipment_service_level_category,
        })
        if self.amz_delivery_start_time and self.amz_delivery_end_time:
            start_date = time.strptime(self.amz_delivery_start_time, "%Y-%m-%d %H:%M:%S")
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S", start_date)
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(start_date, "%Y-%m-%dT%H:%M:%S"))))
            start_date = str(start_date) + 'Z'

            end_date = time.strptime(self.amz_delivery_end_time, "%Y-%m-%d %H:%M:%S")
            end_date = time.strftime("%Y-%m-%dT%H:%M:%S", end_date)
            end_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(end_date, "%Y-%m-%dT%H:%M:%S"))))
            end_date = str(start_date) + 'Z'

            data.update({
                'DeliveryWindow.StartDateTime': start_date,
                'DeliveryWindow.EndDateTime': end_date,
            })

        displayable_date = self.amz_displayable_date_time or self.date_order
        if not isinstance(displayable_date, bool):
            displayable_date = str(displayable_date)
            displayable_date = '%s 00:00:00'%(displayable_date)

        data.update({
            'DestinationAddress.Name': str(self.partner_shipping_id.name),
            'DestinationAddress.Line1': str(self.partner_shipping_id.street or ''),
            'DestinationAddress.Line2': str(self.partner_shipping_id.street2 or ''),
            'DestinationAddress.CountryCode': str(self.partner_shipping_id.country_id.code or ''),
            'DestinationAddress.City': str(self.partner_shipping_id.city or ''),
            'DestinationAddress.StateOrProvinceCode': str(self.partner_shipping_id.state_id and
                                                          self.partner_shipping_id.state_id.code or ''),
            'DestinationAddress.PostalCode': str(self.partner_shipping_id.zip or ''),
        })

        data.update({'DisplayableOrderComment': str(self.note) or str(self.name)})
        data.update({
            'DisplayableOrderDateTime': displayable_date,
            'FulfillmentAction': str(self.amz_fulfillment_action),

        })
        count = 1
        for line in self.order_line:
            if line.product_id and line.product_id.type == 'service':
                continue

            key = "Items.member.%s.Quantity" % (count)
            data.update({key: str(int(line.product_uom_qty))})
            key = "Items.member.%s.SellerSKU" % (count)
            data.update({key: str(line.amazon_product_id.seller_sku)})
            key = "Items.member.%s.SellerFulfillmentOrderItemId" % (count)
            data.update({key: str(line.amazon_product_id.seller_sku)})
            count = count + 1
        if self.notify_by_email:
            count = 1
            for follower in self.message_follower_ids:
                if follower.partner_id.email:
                    key = "NotificationEmailList.member.%s" % (count)
                    data.update({'key': str(follower.partner_id.email)})
                    count = count + 1
        return data

    @api.multi
    def mark_sent_amazon(self):
        return True

    @api.multi
    def mark_not_sent_amazon(self):
        return True

    @api.multi
    def _prepare_amazon_partner_vals(self, vals):
        """
            This function prepare dictionary for the res.partner.
            @note: You need to prepare partner values and pass as dictionary in this function.
            @requires: name
            @param vals: {'name': 'emipro', 'street': 'address', 'street2': 'address', 'email': 'test@test.com'...}
            @return: values of partner as dictionary
        """
        context = dict(self._context)
        state_code = vals.get('state_code') or vals.get('state_name')
        country_code = vals.get('country_code', '')
        country_name = vals.get('country_name', '')
        country_obj = self.env['res.country'].search(['|', ('code', '=', country_code), ('name', '=', country_name)],
                                                     limit=1)
        state_obj = self.create_order_update_state(state_code, vals.get('zip', ''), country_obj)
        partner_vals = {
            'name': vals.get('name'),
            'parent_id': vals.get('parent_id', False),
            'street': vals.get('street', ''),
            'street2': vals.get('street2', ''),
            'city': vals.get('city', ''),
            'state_id': state_obj and state_obj.id or False,
            'country_id': country_obj and country_obj.id or False,
            'phone': vals.get('phone', ''),
            'email': vals.get('email'),
            'zip': vals.get('zip', ''),
            'lang': vals.get('lang', False),
            'company_id': vals.get('company_id', False),
            'type': vals.get('type', False),
            'is_company': vals.get('is_company', False),
        }
        if context.get('return_with_state_and_country_obj', False):
            return partner_vals, country_obj, state_obj
        return partner_vals

    def create_order_update_state(self, state_name_or_code, zip_code, country):
        state = self.env['res.country.state'].search(
            ['|', ('name', '=', state_name_or_code), ('code', '=', state_name_or_code),
             ('country_id', '=', country.id)], limit=1)

        if not state:
            try:
                url = 'https://api.zippopotam.us/' + country.code + '/' + zip_code.split('-')[0]
                response = requests.get(url)
                response = ast.literal_eval(response.content.decode('utf-8'))
            except:
                return state
            if response:
                state_obj = self.env['res.country.state']
                country_obj = self.env['res.country']
                if not country:
                    country = country_obj.search([('name', '=', response.get('country')), (
                        'code', '=', response.get('country abbreviation'))])
                if not country:
                    country = country_obj.create({'name': response.get('country'),
                                                  'code': response.get('country abbreviation')})
                state = state_obj.search(
                    ['|', ('name', '=', response.get('places')[0].get('state')), ('code', '=', response.get('places')[0].get('state abbreviation')),
                     ('country_id', '=', country.id)], limit=1)
                if not state:
                    state = state_obj.create({
                        'name': response.get('places')[0].get('state'),
                        'code': response.get('places')[0].get('state abbreviation'),
                        'country_id': country.id
                    })
                return state
        else:
            return state