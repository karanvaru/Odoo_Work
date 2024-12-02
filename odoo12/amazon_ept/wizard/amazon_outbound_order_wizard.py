import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class amazon_outbound_order_wizard(models.TransientModel):
    _name = "amazon.outbound.order.wizard"
    _description = 'amazon.outbound.order.wizard'

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

    instance_id = fields.Many2one("amazon.instance.ept", "Instance")
    fba_warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")

    sale_order_ids = fields.Many2many("sale.order", "convert_sale_order_bound_rel", "wizard_id",
                                      "sale_id",
                                      "Sales Orders")
    fulfillment_action = fields.Selection([('Ship', 'Ship'), ('Hold', 'Hold')],
                                          string="Fulfillment Action",
                                          default="Hold", help=help_fulfillment_action)
    displayable_date_time = fields.Date("Displayable Order Date", required=False,
                                        help="Display Date in package")
    fulfillment_policy = fields.Selection(
        [('FillOrKill', 'FillOrKill'), ('FillAll', 'FillAll'),
         ('FillAllAvailable', 'FillAllAvailable')],
        string="Fulfillment Policy", default="FillOrKill", required=True,
        help=help_fulfillment_policy)
    shipment_service_level_category = fields.Selection(
        [('Expedited', 'Expedited'), ('NextDay', 'NextDay'), ('SecondDay', 'SecondDay'),
         ('Standard', 'Standard'),
         ('Priority', 'Priority'), ('ScheduledDelivery', 'ScheduledDelivery')], "Shipment Category",
        default='Standard')
    delivery_start_time = fields.Datetime("Delivery Start Time",
                                          help="Delivery Estimated Start Time")
    delivery_end_time = fields.Datetime("Delivery End Time", help="Delivery Estimated End Time")
    query_start_date_time = fields.Datetime("Query Start Date Time",
                                            help="If you not specified start time then system "
                                                 "will take -36 hours")
    notify_by_email = fields.Boolean("Notify By Email", default=False,
                                     help="If true then system will notify by email to followers")
    is_displayable_date_time_required = fields.Boolean("Displayable Date Requied ?", default=True)
    note = fields.Text("note", help="To set note in outbound order")

    @api.onchange("instance_id", "is_displayable_date_time_required")
    def on_change_sale_orders(self):
        sale_order_obj = self.env['sale.order']
        warehouse_id = self.instance_id and self.instance_id.fba_warehouse_id and \
                       self.instance_id.fba_warehouse_id.id or False
        if not self.is_displayable_date_time_required:
            self.displayable_date_time = False
        self.fba_warehouse_id = warehouse_id
        res = {}
        domain = {}
        sales_orders = sale_order_obj.search(
            [('state', '=', 'draft'), ('warehouse_id', '=', warehouse_id),
             ('amz_instance_id', '=', False)])
        domain.update({'sale_order_ids': [('id', 'in', sales_orders.ids)]})
        res.update({'domain': domain})
        return res

    @api.multi
    def create_order(self):
        instance = self.instance_id
        fulfillment_action = self.fulfillment_action
        displayable_date_time = self.displayable_date_time or False
        fulfillment_policy = self.fulfillment_policy
        shipment_service_level_category = self.shipment_service_level_category
        amazon_sale_order_ids = []
        amazon_product_obj = self.env['amazon.product.ept']
        for amazon_order in self.sale_order_ids:
            if not amazon_order.order_line:
                continue

            if not amazon_order.amz_fulfillment_instance_id:
                amazon_order.write({'amz_instance_id': instance.id,
                                    'amz_fulfillment_instance_id': instance.id,
                                    'amz_fulfillment_action': fulfillment_action,
                                    'warehouse_id': instance.fba_warehouse_id.id,
                                    'pricelist_id': instance.pricelist_id.id,
                                    'amz_displayable_date_time': displayable_date_time or
                                                                 amazon_order.date_order,
                                    'amz_fulfillment_policy': fulfillment_policy,
                                    'amz_shipment_service_level_category': shipment_service_level_category,
                                    'amz_is_outbound_order': True,
                                    'notify_by_email': self.notify_by_email,
                                    'amazon_reference': amazon_order.name,
                                    'note': self.note or amazon_order.name,
                                    })
                for line in amazon_order.order_line:
                    if line.product_id.type == 'service':
                        continue
                    if line.product_id:
                        amz_product = amazon_product_obj.search(
                            [('product_id', '=', line.product_id.id),
                             ('instance_id', '=', instance.id),
                             ('fulfillment_by', '=', 'AFN')], limit=1)
                        line.write(
                            {'amazon_product_id': amz_product.id})
            amazon_sale_order_ids.append(amazon_order.id)
        return True

    """ Updated code by twinkal on 13 december, done changes to solve issue json not process 
         seriallizable data and  to pass prepared dict to create fulfillement """

    @api.multi
    def create_fulfillment(self):
        active_ids = self._context.get('active_ids')
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        draft_orders = self.env['sale.order'].search(
            [('id', 'in', active_ids), ('amz_is_outbound_order', '=', True),
             ('state', '=', 'draft'),
             ('exported_in_amazon', '=', False)])
        amazon_instance_obj = self.env['amazon.instance.ept']
        if not draft_orders:
            return True
        for order in draft_orders:
            if not order.amz_shipment_service_level_category:
                raise Warning(
                    "Required field Shipment Category is not set for order %s" % (order.name))
            if not order.note:
                raise Warning("Required field Displayable Order Comment is not set for order %s" % (
                    order.name))
            if not order.amz_fulfillment_action:
                raise Warning("Required field Order Fulfullment Action is not set for order %s" % (
                    order.name))
            if not order.amz_displayable_date_time:
                raise Warning("Required field  Order Fulfullment Action is not set for order %s" % (
                    order.name))
            if not order.amz_fulfillment_policy:
                raise Warning(
                    "Required field  Fulfullment Policy is not set for order %s" % (order.name))

        instances = amazon_instance_obj.search([('fba_warehouse_id', '!=', False)])
        filtered_orders = draft_orders.filtered(lambda x: x.amz_instance_id in instances)
        for order in filtered_orders:
            data = order.get_data()
            kwargs = {
                'merchant_id': order.amz_instance_id.merchant_id and str(order.amz_instance_id.merchant_id) or False,
                'auth_token': order.amz_instance_id.auth_token and str(order.amz_instance_id.auth_token) or False,
                'app_name': 'amazon_ept',
                'account_token': account.account_token,
                'emipro_api': 'auto_create_outbound_order',
                'dbuuid': dbuuid,
                'amazon_marketplace_code': order.amz_instance_id.country_id.amazon_marketplace_code or
                                           order.amz_instance_id.country_id.code,
                'data': data, }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                if order.amz_fulfillment_action == 'Ship':
                    order.write({'exported_in_amazon': True})
                self._cr.commit()

        return True

    """ Updated code by twinkal on 13 december, done changes to solve issue json not process 
         seriallizable data and  to pass prepared dict to update fulfillement """

    @api.multi
    def update_fulfillment(self):
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        active_ids = self._context.get('active_ids')
        amazon_instance_obj = self.env['amazon.instance.ept']
        progress_orders = self.env['sale.order'].search(
            [('id', 'in', active_ids), ('amz_is_outbound_order', '=', True),
             ('state', '=', 'draft'),
             ('exported_in_amazon', '=', True)])
        if not progress_orders:
            return True
        instances = amazon_instance_obj.search([('fba_warehouse_id', '!=', False)])
        filtered_orders = progress_orders.filtered(lambda x: x.amz_instance_id in instances)
        for order in filtered_orders:
            data = order.get_data()
            kwargs = {
                'merchant_id': order.amz_instance_id.merchant_id and str(
                    order.amz_instance_id.merchant_id) or False,
                'auth_token': order.amz_instance_id.auth_token and str(
                    order.amz_instance_id.auth_token) or False,
                'app_name': 'amazon_ept',
                'account_token': account.account_token,
                'emipro_api': 'update_fulfillment',
                'dbuuid': dbuuid,
                'amazon_marketplace_code': order.amz_instance_id.country_id.amazon_marketplace_code or
                                           order.amz_instance_id.country_id.code,
                'data': data, }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                self._cr.commit()

        return True

    """ Updated code by twinkal on 13 december, done changes to pass order name"""

    @api.multi
    def cancel_fulfillment(self):
        active_ids = self._context.get('active_ids')
        amazon_instance_obj = self.env['amazon.instance.ept']
        progress_orders = self.env['sale.order'].search(
            [('id', 'in', active_ids), ('amz_is_outbound_order', '=', True),
             ('state', '=', 'cancel'),
             ('exported_in_amazon', '=', True)])

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        if not progress_orders:
            return True

        instances = amazon_instance_obj.search([('fba_warehouse_id', '!=', False)])
        filtered_orders = progress_orders.filtered(lambda x: x.amz_instance_id in instances)
        for order in filtered_orders:
            kwargs = {
                'merchant_id': order.amz_instance_id.merchant_id and str(order.amz_instance_id.merchant_id) or False,
                'auth_token': order.amz_instance_id.auth_token and str(order.amz_instance_id.auth_token) or False,
                'app_name': 'amazon_ept',
                'account_token': account.account_token,
                'emipro_api': 'action_cancel',
                'dbuuid': dbuuid,
                'amazon_marketplace_code': order.amz_instance_id.country_id.amazon_marketplace_code or
                                           order.amz_instance_id.country_id.code,
                'order_name': order.name, }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                self._cr.commit()
        return True

    @api.multi
    def get_fulfillment_by_instance(self):
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        amazon_instance_obj = self.env['amazon.instance.ept']
        instance_id = self._context.get('active_id')
        instance = amazon_instance_obj.search(
            [('id', '=', instance_id), ('fba_warehouse_id', '!=', False)])
        orders = self.env['sale.order'].search(
            [('state', 'in', ['progress', 'manual']),
             ('amz_fulfullment_order_status', 'not in', ['COMPLETE', 'CANCELLED']),
             ('amz_instance_id', '=', instance_id), ('exported_in_amazon', '=', True)])

        for order in orders:
            kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token': instance.auth_token and str(instance.auth_token) or False,
                      'app_name': 'amazon_ept',
                      'account_token': account.account_token,
                      'emipro_api': 'get_fulfillment_order',
                      'dbuuid': dbuuid,
                      'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                                 instance.country_id.code,
                      'order_name': order.name, }
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
            if response.get('result'):
                result = response.get('result')
                self.env['stock.picking'].create_shipment(order, result)
            else:
                raise Warning(response.get('reason'))

        return True

    """ Updated code by twinkal on 13 december, done changes to pass order name"""

    @api.multi
    def get_fulfillment_order(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        active_ids = self._context.get('active_ids')
        orders = self.env['sale.order'].search(
            [('state', 'in', ['progress', 'manual']),
             ('amz_fulfullment_order_status', 'not in', ['COMPLETE', 'CANCELLED']),
             ('id', 'in', active_ids), ('exported_in_amazon', '=', True)])

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        instances = amazon_instance_obj.search([('fba_warehouse_id', '!=', False)])
        filtered_orders = orders.filtered(lambda x: x.amz_instance_id in instances)
        for order in filtered_orders:
            kwargs = {
                'merchant_id': order.amz_instance_id.merchant_id and str(order.amz_instance_id.merchant_id) or False,
                'auth_token': order.amz_instance_id.auth_token and str(order.amz_instance_id.auth_token) or False,
                'app_name': 'amazon_ept',
                'account_token': account.account_token,
                'emipro_api': 'get_fulfillment_order',
                'dbuuid': dbuuid,
                'amazon_marketplace_code': order.amz_instance_id.country_id.amazon_marketplace_code or
                                           order.amz_instance_id.country_id.code,
                'order_name': order.name, }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
            if response.get('result'):
                result = response.get('result')
                self.env['stock.picking'].create_shipment(order, result)
            else:
                raise Warning(response.get('reason'))
        return True

    @api.multi
    def list_fulfillment_orders(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        instance_id = self._context.get('active_id')

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        instance = amazon_instance_obj.search(
            [('id', '=', instance_id), ('fba_warehouse_id', '!=', False)])
        sale_order_obj = self.env['sale.order']
        import_time = False
        if self.query_start_date_time:
            import_time = time.strptime(self.query_start_date_time, "%Y-%m-%d %H:%M:%S")
            import_time = time.strftime("%Y-%m-%dT%H:%M:%S", import_time)
            import_time = time.strftime("%Y-%m-%dT%H:%M:%S",
                                        time.gmtime(time.mktime(
                                            time.strptime(import_time, "%Y-%m-%dT%H:%M:%S"))))
            import_time = str(import_time) + 'Z'
        list_wrapper = []
        kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token': instance.auth_token and str(instance.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'list_fulfillment_orders',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                             instance.country_id.code,
                  'import_time': import_time, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('result'):
            list_wrapper = response.get('result')
        else:
            raise Warning(response.get('reason'))

        for wrapper in list_wrapper:
            for member in wrapper.get('FulfillmentOrders', {}):
                order_name = member.get('SellerFulfillmentOrderId', {}).get('value', False)
                status = member.get('FulfillmentOrderStatus', {}).get('value', False)
                order = sale_order_obj.search({'name': order_name})
                order and order.write({'amz_fulfullment_order_status': status})
        return True

    @api.multi
    def wizard_view(self, created_id):
        view = self.env.ref('amazon_ept.amazon_outbound_order_wizard')
        return {
            'name': _('Amazon Outbound Orders'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amazon.outbound.order.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': created_id and created_id.id or False,
            'context': self._context,
        }
