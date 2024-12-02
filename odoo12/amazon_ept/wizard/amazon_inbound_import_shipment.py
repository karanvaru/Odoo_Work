from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class amazon_inbound_import_shipment_wizard(models.TransientModel):
    _name = "amazon.inbound.import.shipment.ept"
    _description = 'amazon.inbound.import.shipment.ept'

    shipment_id = fields.Char('Shipment Id', required=True)
    instance_id = fields.Many2one('amazon.instance.ept', string='Instance', required=True)
    from_warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True)
    sync_product = fields.Boolean('Sync Product', default=True,
                                  help="Set to True to if you want before import shipment automatically sync the amazon product.")
    """
    This model is use to get inforamation based on given shipment_id and instance of inbound shipment. 
    
    Update by twinkal  27 june
    updated passed argrument in create_amazon_inbound_shipment from result to 
    amazon_shipments
    """

    @api.multi
    def get_inbound_import_shipment(self):
        shipment_id = self.shipment_id
        shipment_ids = self.shipment_id.split(',')
        for shipment_id in shipment_ids:
            instance = self.instance_id
            proxy_data = self.instance_id.seller_id.get_proxy_server()

            account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
            dbuuid = self.env['ir.config_parameter'].sudo(
            ).get_param('database.uuid')
            amazon_shipments = []

            kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token': instance.auth_token and str(instance.auth_token) or False,
                      'app_name': 'amazon_ept',
                      'account_token': account.account_token,
                      'emipro_api': 'check_status',
                      'dbuuid': dbuuid,
                      'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                                 instance.country_id.code,
                      'proxies': proxy_data,
                      'shipment_ids': [shipment_id], }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                amazon_shipments = response.get('amazon_shipments')

            inbound_shipment = self.create_amazon_inbound_shipment(amazon_shipments)
            self.get_list_inbound_shipment_items(shipment_id, instance, inbound_shipment)
            inbound_shipment.create_shipment_picking()

    @api.multi
    def create_amazon_inbound_shipment(self, results):
        inbound_shipment = False
        for result in results:
            amazon_inbound_shipment_obj = self.env['amazon.inbound.shipment.ept']
            ShipmentName = result.get('ShipmentName', {}).get('value', False)
            ShipmentId = result.get('ShipmentId', {}).get('value', False)
            fulfillment_center_id = result.get('DestinationFulfillmentCenterId', {}).get('value', False)
            # partner_name=results.get('ShipmentData',{}).get('member',{}).get('ShipFromAddress',{})
            # partner=amazon_inbound_shipment_obj.create_or_update_address(partner_name)
            inbound_shipment = amazon_inbound_shipment_obj.create(
                {'name': ShipmentName, 'fulfill_center_id': fulfillment_center_id, 'shipment_id': ShipmentId,
                 'from_warehouse_id': self.from_warehouse_id.id, 'is_manually_created': True,
                 'instance_id_ept': self.instance_id.id})
        return inbound_shipment

    @api.multi
    def get_list_inbound_shipment_items(self, shipment_id, instance, inbound_shipment):

        proxy_data = instance.seller_id.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        items = []

        kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token': instance.auth_token and str(instance.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'check_amazon_shipment_status',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                             instance.country_id.code,
                  'proxies': proxy_data,
                  'amazon_shipment_id': shipment_id, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            items = response.get('items')

        return self.create_amazon_inbound_shipment_line(items, inbound_shipment)

    @api.multi
    def create_amazon_inbound_shipment_line(self, items, inbound_shipment):
        amazon_inbound_shipment_plan_line_obj = self.env['inbound.shipment.plan.line']
        amazon_product_obj = self.env['amazon.product.ept']
        for item in items:
            seller_sku = item.get('SellerSKU', {}).get('value', '')
            fn_sku = item.get('FulfillmentNetworkSKU', {}).get('value')
            received_qty = float(item.get('QuantityShipped', {}).get('value', 0.0))
            amazon_product = amazon_product_obj.search_amazon_product(self.instance_id.id, seller_sku, 'AFN')
            if not amazon_product:
                amazon_product = amazon_product_obj.search(
                    [('product_asin', '=', fn_sku), ('instance_id', '=', self.instance_id.id)], limit=1)
            if not amazon_product:
                raise Warning("Amazon Product is not found in ERP || Seller SKU %s || Instance %s" % (
                seller_sku, self.instance_id.name))
            amazon_inbound_shipment_plan_line_obj.create(
                {'amazon_product_id': amazon_product.id, 'seller_sku': seller_sku, 'quantity': received_qty,
                 'fn_sku': fn_sku, 'odoo_shipment_id': inbound_shipment.id})
        return True

    @api.multi
    def prepare_amazon_product_vals(self, sku, odoo_product):
        vals = {
            'instance_id': self.instance_id.id,
            'seller_sku': sku,
            'type': odoo_product and odoo_product[0].type or 'product',
            'product_id': odoo_product and odoo_product[0].id or False,
            'purchase_ok': True,
            'sale_ok': True,
            'exported_to_amazon': True,
            'fulfillment_by': 'AFN',
        }
        return vals
