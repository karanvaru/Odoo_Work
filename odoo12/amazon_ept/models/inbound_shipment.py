import base64
import zipfile
import os
import logging
import time
from collections import defaultdict
from odoo import models, fields, api, _
import dateutil.parser
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap
from stdnum.nl import postcode
from ..endpoint import DEFAULT_ENDPOINT
# from samples.test_perf import response

_logger = logging.getLogger(__name__)

shipment_status_help = """
WORKING - The shipment was created by the seller, but has not yet shipped.
SHIPPED - The shipment was picked up by the carrier.
IN_TRANSIT - The carrier has notified the Amazon fulfillment center that it is aware of the shipment.
DELIVERED - The shipment was delivered by the carrier to the Amazon fulfillment center.
CHECKED_IN - The shipment was checked-in at the receiving dock of the Amazon fulfillment center.
RECEIVING - The shipment has arrived at the Amazon fulfillment center, but not all items have been marked as received.
CLOSED - The shipment has arrived at the Amazon fulfillment center and all items have been marked as received.
CANCELLED - The shipment was cancelled by the seller after the shipment was sent to the Amazon fulfillment center.
DELETED - The shipment was cancelled by the seller before the shipment was sent to the Amazon fulfillment center.
ERROR - There was an error with the shipment and it was not processed by Amazon."""

transport_status = [('draft', 'Draft'), ('WORKING', 'WORKING'),
                    ('ERROR_ON_ESTIMATING', 'ERROR_ON_ESTIMATING'),
                    ('ESTIMATING', 'ESTIMATING'),
                    ('ESTIMATED', 'ESTIMATED'),
                    ('ERROR_ON_CONFIRMING', 'ERROR_ON_CONFIRMING'),
                    ('CONFIRMING', 'CONFIRMING'),
                    ('CONFIRMED', 'CONFIRMED'),
                    ('VOIDING', 'VOIDING'),
                    ('VOIDED', 'VOIDED'),
                    ('ERROR_IN_VOIDING', 'ERROR_IN_VOIDING')]
transport_status_list = ['WORKING', 'ERROR_ON_ESTIMATING', 'ESTIMATING', 'ESTIMATED',
                         'ERROR_ON_CONFIRMING', 'CONFIRMING', 'CONFIRMED', 'VOIDING', 'VOIDED',
                         'ERROR_IN_VOIDING']


class inbound_shipment_ept(models.Model):
    _name = "amazon.inbound.shipment.ept"
    _description = "Inbound Shipment"
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.one
    @api.depends('partnered_ltl_ids.weight_unit', 'partnered_ltl_ids.weight_value')
    def _get_shipment_weight(self):
        if self.is_partnered:
            if self.partnered_ltl_ids and self.transport_type == 'partnered_ltl_data':
                weight_unit_kg = weight_unit_pound = 0
                weight_kg = weight_pound = 0.0
                for parcel in self.partnered_ltl_ids:
                    if parcel.weight_unit == 'kilograms':
                        weight_unit_kg += 1
                        weight_kg += parcel.weight_value
                    elif parcel.weight_unit == 'pounds':
                        weight_unit_pound += 1
                        weight_pound += parcel.weight_value
                weight_unit = max(weight_unit_kg, weight_unit_pound)
                if weight_unit == weight_unit_kg:
                    # Convert Weight Pounds to Kilograms
                    weight_kg += (weight_pound * 0.453592)
                    self.amazon_shipment_weight = weight_kg
                    self.amazon_shipment_weight_unit = 'kilograms'
                else:
                    # Convert Weight Kilograms to Pounds
                    weight_pound += (weight_kg * 2.20462)
                    self.amazon_shipment_weight = weight_pound
                    self.amazon_shipment_weight_unit = 'pounds'

    @api.one
    @api.depends('is_partnered', 'shipping_type')
    def _get_transport_type(self):
        if self.shipping_type == 'sp' and self.is_partnered:
            self.transport_type = 'partnered_small_parcel_data'
        elif self.shipping_type == 'ltl' and self.is_partnered:
            self.transport_type = 'partnered_ltl_data'
        elif self.shipping_type == 'sp':
            self.transport_type = 'non_partnered_small_parcel_data'
        elif self.shipping_type == 'ltl':
            self.transport_type = 'non_partnered_ltl_data'

    @api.one
    @api.depends('picking_ids.state', 'picking_ids.updated_in_amazon')
    def _get_amazon_staus(self):
        if self.picking_ids:
            self.updated_in_amazon = True
        else:
            self.updated_in_amazon = False
        for picking in self.picking_ids:
            if picking.state == 'cancel':
                continue
            if picking.picking_type_id.code != 'outgoing':
                continue
            if not picking.updated_in_amazon:
                self.updated_in_amazon = False
                break

    @api.one
    def get_error_logs(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('amazon.inbound.shipment.ept')
        logs = amazon_transaction_log_obj.search(
            [('model_id', '=', model_id), ('res_id', '=', self.id)])
        self.log_ids = logs.ids
        if self.picking_ids:
            self.is_picking = True
        else:
            self.is_picking = False

    @api.multi
    def get_instance(self, shipment):
        if shipment.instance_id_ept:
            return shipment.instance_id_ept
        else:        
            return shipment.shipment_plan_id.instance_id

    @api.multi
    def get_carton_content_result(self):
        amazon_log_book_obj = self.env['amazon.process.log.book']
        amazon_transaction_obj = self.env['amazon.transaction.log']
        if not self.feed_id:
            return True

        instance = self.get_instance(self)
        #         instance=self.shipment_plan_id.instance_id

        proxy_data = instance.seller_id.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        
        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'get_feed_submission_result',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxies':proxy_data,
                  'feed_submission_id': self.feed_id.feed_result_id,}
        try:
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                result = response.get('result')
                summary=result.get('AmazonEnvelope',{}).get('Message',{}).get('ProcessingReport',{}).get('ProcessingSummary',{})
                error=summary.get('MessagesWithError',{}).get('value')
                if error!='0':
                    job_log_vals = {
                        'skip_process': True,
                        'message': "Inbound Shipment Partner Carrier Carton Update Error",
                        'application': 'update_inbound_shipment',
                        'operation_type': 'export',
                        'instance_id': instance.id
                    }
                    job = amazon_log_book_obj.create(job_log_vals)
                    summary = result.get('AmazonEnvelope', {}).get('Message', {}).get(
                        'ProcessingReport', {}).get('ProcessingSummary', {})
                    description = "MessagesProcessed %s" % (
                    summary.get('MessagesProcessed', {}).get('value'))
                    description = "%s || MessagesSuccessful %s" % (
                    description, summary.get('MessagesSuccessful', {}).get('value'))
                    description = "%s || MessagesWithError %s" % (
                    description, summary.get('MessagesWithError', {}).get('value'))
                    description = "%s || MessagesWithWarning %s" % (
                    description, summary.get('MessagesWithWarning', {}).get('value'))
                    summary = result.get('AmazonEnvelope', {}).get('Message', {}).get(
                        'ProcessingReport', {}).get('Result', {})
                    if not isinstance(summary, list):
                        summary = [summary]
                    for line in summary:
                        description = "%s %s" % (description, line.get('ResultDescription'))
                    if not amazon_transaction_obj.search(
                            [('message', '=', description), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': self.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': self.name,
                            'message': description,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    self.write({'is_update_inbound_carton_contents': False})
                else:
                    self.write({'is_carton_content_updated': True})
        except Exception as e:
            raise Warning(str(e))
        return True

    @api.onchange('partnered_ltl_ids')
    def on_change_partnered_ltl(self):
        self.total_box = len(self.partnered_ltl_ids.ids)

    feed_id = fields.Many2one("feed.submission.history", string="Submit Feed Id")
    log_ids = fields.One2many('amazon.transaction.log', compute="get_error_logs")
    is_picking = fields.Boolean("Is Picking", compute="get_error_logs")
    is_carton_content_updated = fields.Boolean("Carton Content Updated ?", default=False,
                                               copy=False)
    name = fields.Char(size=120, string='Name', readonly=True, required=False, index=True)
    shipment_id = fields.Char(size=120, string='Shipment ID', index=True)
    shipment_plan_id = fields.Many2one('inbound.shipment.plan.ept', string='Shipment Plan')
    address_id = fields.Many2one('res.partner', string='Ship To Address')
    fulfill_center_id = fields.Char(size=120, string='Fulfillment Center', readonly=True,
                                    help="DestinationFulfillmentCenterId provided by Amazon "
                                         "when we send shipment Plan to Amazon")
    label_prep_type = fields.Char(size=120, string='LabelPrepType', readonly=True,
                                  help="LabelPrepType provided by Amazon when we send shipment Plan "
                                       "to Amazon")
    odoo_shipment_line_ids = fields.One2many('inbound.shipment.plan.line', 'odoo_shipment_id',
                                             string='Shipment Items')
    picking_ids = fields.One2many('stock.picking', 'odoo_shipment_id', string="Pickings",
                                  readonly=True)
    are_cases_required = fields.Boolean("AreCasesRequired", default=False,
                                        help="Indicates whether or not an Inbound shipment contains "
                                             "case-packed boxes. A shipment must either contain all "
                                             "case-packed boxes or all individually packed boxes")
    created_date = fields.Date('Create on', default=time.strftime('%Y-%m-%d'))
    updated_in_amazon = fields.Boolean("Updated In Amazon", compute=_get_amazon_staus, store=True)
    pro_number = fields.Char('Pro Number', size=10,
                             help="The PRO number assigned to your shipment by the carrier. "
                                  "A string of numbers, seven to 10 characters in length.")
    state = fields.Selection([('draft', 'Draft'), ('WORKING', 'WORKING'), ('SHIPPED', 'SHIPPED'),
                              ('IN_TRANSIT', 'IN_TRANSIT'), ('DELIVERED', 'DELIVERED'),
                              ('CHECKED_IN', 'CHECKED_IN'), ('RECEIVING', 'RECEIVING'),
                              ('CLOSED', 'CLOSED'), ('CANCELLED', 'CANCELLED'),
                              ('DELETED', 'DELETED'), ('ERROR', 'ERROR'),
                              ],
                             string='Shipment Status', default='WORKING', help=shipment_status_help)

    transport_type = fields.Selection([('partnered_small_parcel_data', 'PartneredSmallParcelData'),
                                       ('non_partnered_small_parcel_data',
                                        'NonPartneredSmallParcelData'),
                                       ('partnered_ltl_data', 'PartneredLtlData'),
                                       ('non_partnered_ltl_data', 'NonPartneredLtlData')
                                       ], compute="_get_transport_type", store=True,
                                      string='Transport Type')
    transport_state = fields.Selection(transport_status, default='draft', copy=False,
                                       string='Transport States')
    transport_content_exported = fields.Boolean('Transport Content Exported?', default=False,
                                                copy=False)
    is_partnered = fields.Boolean('Is Partnered', default=False, copy=False)
    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    shipping_type = fields.Selection([('sp', 'SP (Small Parcel)'),
                                      ('ltl', 'LTL (Less Than Truckload/FullTruckload (LTL/FTL))')
                                      ], string="Shipping Type", default="sp")
    is_billof_lading_available = fields.Boolean(string='IsBillOfLadingAvailable', default=False,
                                                help="Indicates whether the bill of lading for the "
                                                     "shipment is available.")
    partnered_small_parcel_ids = fields.One2many('stock.quant.package',
                                                 'partnered_small_parcel_shipment_id',
                                                 string='Partnered Small Parcel')
    partnered_ltl_ids = fields.One2many('stock.quant.package', 'partnered_ltl_shipment_id',
                                        string='Partnered LTL')

    currency_id = fields.Many2one('res.currency', string='Currency')
    estimate_amount = fields.Float('Estimate Amount',
                                   help='The amount that the Amazon-partnered carrier will charge '
                                        'to ship the inbound shipment.')
    confirm_deadline_date = fields.Datetime(string='Confirm Deadline Date',
                                            help="The date by which this estimate must be confirmed. "
                                                 "After this date the estimate is no longer valid "
                                                 "and cannot be confirmed. In ISO 8601 format.")
    void_deadline_date = fields.Datetime(string='Void Deadline Date',
                                         help="The date after which a confirmed transportation "
                                              "request can no longer be voided. "
                                              "This date is 24 hours after you confirm a Small "
                                              "Parcel shipment transportation request or one hour "
                                              "after you confirm a Less Than Truckload/Full Truckload (LTL/FTL) "
                                              "shipment transportation request. After the void "
                                              "deadline passes your account will be charged for "
                                              "the shipping cost. In ISO 8601 format.")

    partnered_ltl_id = fields.Many2one('res.partner', string='Contact',
                                       help="Contact information for the person in your organization "
                                            "who is responsible for the shipment. "
                                            "Used by the carrier if they have questions "
                                            "about the shipment.")
    box_count = fields.Integer('Number of box')
    seller_freight_class = fields.Selection(
        [('50', '50'), ('55', '55'), ('60', '60'), ('65', '65'), ('70', '70'), ('77.5', '77.5'),
         ('85', '85'), ('92.5', '92.5'), ('100', '100'), ('110', '110'), ('125', '125'),
         ('150', '150'),
         ('175', '175'), ('200', '200'), ('250', '250'), ('300', '300'), ('400', '400'),
         ('500', '500')],
        string='Seller Freight Class')
    freight_ready_date = fields.Date('Freight Ready Date')
    preview_pickup_date = fields.Datetime(string='PreviewPickupDate',
                                          help="The estimated date that the shipment will be picked "
                                               "up by the carrier. In ISO 8601 format.")
    preview_delivery_date = fields.Datetime(string='PreviewDeliveryDate',
                                            help="The estimated date that the shipment will be "
                                                 "delivered to an Amazon fulfillment center.")
    preview_freight_class = fields.Selection(
        [('50', '50'), ('55', '55'), ('60', '60'), ('65', '65'), ('70', '70'), ('77.5', '77.5'),
         ('85', '85'), ('92.5', '92.5'), ('100', '100'), ('110', '110'), ('125', '125'),
         ('150', '150'),
         ('175', '175'), ('200', '200'), ('250', '250'), ('300', '300'), ('400', '400'),
         ('500', '500')],
        string='PreviewFreightClass',
        help="The freight class of the shipment as estimated by Amazon if you did not include a "
             "freight class when you called the PutTransportContent operation.")

    amazon_reference_id = fields.Char(string='Amazon Reference Id', size=50,
                                      help="A unique identifier created by Amazon that identifies "
                                           "this Amazon-partnered, Less Than Truckload/Full Truckload (LTL/FTL) shipment.")

    amazon_shipment_weight = fields.Float(compute='_get_shipment_weight',
                                          string="Shipment Weight", store=True, readonly=True)
    amazon_shipment_weight_unit = fields.Selection(
        [('pounds', 'Pounds'), ('kilograms', 'Kilograms'), ],
        string='Weight Unit',
        compute="_get_shipment_weight",
        store=True, readonly=True)
    is_update_inbound_carton_contents = fields.Boolean("Is Update Inbound Carton Contents ?",
                                                       default=False, copy=False)
    closed_date = fields.Date("Closed Date", readonly=True, copy=False)
    is_finally_closed = fields.Boolean("IS Finally Closed ?", default=False)
    suggest_seller_declared_value = fields.Float("Suggest Seller Declared Value", digits=(16, 2))
    seller_declared_value = fields.Float("Seller Declared Value", digits=(16, 2))
    declared_value_currency_id = fields.Many2one('res.currency', string="Declare Value Currency")
    intended_boxcontents_source = fields.Selection(
        [('NONE', 'NONE'), ('FEED', 'FEED'), ('2D_BARCODE', '2D_BARCODE')], default='FEED',
        help="If your instance is USA then you must set box contect, other wise amazon will collect per piece fee",
        string="Intended BoxContents Source")

    # added by twinkal to merge module amazon import inbound shipment
    
    
    from_warehouse_id=fields.Many2one("stock.warehouse",string="Warehouse")
    is_manually_created=fields.Boolean("Is Manually Created",default=False,copy=False)
    instance_id_ept=fields.Many2one("amazon.instance.ept",string="Instance")    
    
    


    @api.multi
    def update_seller_declared_value(self):
        currency_obj = self.env['res.currency']
        self.ensure_one()
        total_value = 0.0
        for picking in self.picking_ids:
            if picking.is_fba_wh_picking:
                continue
            for move in picking.move_lines:
                if move.reserved_availability > 0.0:
                    #                     for quant in move.reserved_quant_ids:
                    #                         if quant.qty>0.0:
                    total_value = total_value + move.reserved_availability
                else:
                    seller = move.product_id.seller_ids and move.product_id.seller_ids[0]
                    price = seller and seller.name.price or 0.0
                    total_value = total_value + (price * move.product_qty)
        instance = self.get_instance(self)
        if instance.pricelist_id.currency_id.name in ['USD']:
            currency = currency_obj.search([('name', '=', 'USD')], limit=1)
        elif instance.company_id.currency_id.name in ['GBP']:
            currency = currency_obj.search([('name', '=', 'GBP')], limit=1)
        else:
            currency = currency_obj.search([('name', '=', 'USD')], limit=1)
        total_value = instance.company_id.currency_id.with_context(
            {'date': time.strftime("%Y-%m-%d %H:%M:%S")}).compute(total_value, currency)
        self.suggest_seller_declared_value = total_value
        if self.seller_declared_value <= 0.0:
            self.seller_declared_value = total_value
        self.declared_value_currency_id = currency.id
        return True

    @api.multi
    def unlink(self):
        for shipment in self:
            if shipment.shipment_plan_id and shipment.shipment_plan_id.state == 'plan_approved':
                raise Warning(_('You cannot delete Inbound Shipment.'))
            
            if shipment.instance_id_ept and shipment.state not in ['CANCELLED','DELETED']:
                raise Warning('You cannot delete Inbound Shipment.')

        return super(inbound_shipment_ept, self).unlink()

    @api.multi
    def get_header(self, instnace):
        return """<?xml version="1.0"?>
            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
            <Header>
                <DocumentVersion>1.01</DocumentVersion>
                <MerchantIdentifier>%s</MerchantIdentifier>
            </Header>
            <MessageType>CartonContentsRequest</MessageType>
            <Message>
         """ % (instnace.merchant_id)

    @api.multi
    def create_carton_contents_requests(self):
        inbound_shipment_line_obj = self.env['inbound.shipment.plan.line']
        amazon_product_obj = self.env['amazon.product.ept']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        amazon_transaction_obj = self.env['amazon.transaction.log']
        feed_submit_obj = self.env['feed.submission.history']
        message = 1
        data = ''
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        for shipment in self:
            instance = self.get_instance(shipment)
            job_log_vals = {
                'skip_process': True,
                'message': 'Amazon Inbound Shipment Submit carton content information (Partner Carrier))',
                'application': 'update_inbound_shipment',
                'operation_type': 'export',
                'instance_id': instance.id
            }
            job = amazon_log_book_obj.create(job_log_vals)

            if not shipment.partnered_small_parcel_ids and not shipment.partnered_ltl_ids:
                message = 'Carton Content Information did not updated in amazon because system not found Carton Content for update || Inbound shipment ref %s' % (
                shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                continue

            box_no_product_dict = {}
            if shipment.partnered_small_parcel_ids:
                parcels = shipment.partnered_small_parcel_ids
            else:
                parcels = shipment.partnered_ltl_ids
            for content in parcels:
                box_no = content.box_no
                if box_no not in box_no_product_dict:
                    box_no_product_dict.update({box_no: {}})
                for carton_line in content.carton_info_ids:
                    line = inbound_shipment_line_obj.search(
                        [('amazon_product_id', '=', carton_line.amazon_product_id.id),
                         ('odoo_shipment_id', '=', shipment.id)], limit=1)
                    seller_sku = line and line.seller_sku
                    quantity_in_case=line.quantity_in_case
                    if not line:
                        amazon_product = amazon_product_obj.search(
                            [('id', '=', carton_line.amazon_product_id.id),
                             ('instance_id', '=', instance.id)], limit=1)
                        seller_sku = amazon_product and amazon_product.seller_sku or False
                    if not seller_sku:
                        continue
                    qty = box_no_product_dict.get(box_no, {}).get(seller_sku, 0.0)
                    qty += carton_line.quantity
                    box_no_product_dict.get(box_no, {}).update({seller_sku:[str(int(qty)), str(int(quantity_in_case))]})
            total_box_list = set(box_no_product_dict.keys())
            flag = False
            for box, qty_dict in box_no_product_dict.items():
                if len(qty_dict.keys()) > 200:
                    message = 'System did not update carton in amazon because amazon not allow to update more then 200 item in one box || Box no %s || Inbound shipment ref %s' % (
                    box, shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    flag = True
            if flag:
                continue

            data = '<MessageID>%s</MessageID><CartonContentsRequest>' % (message)
            message = message + 1
            data = "%s <ShipmentId>%s</ShipmentId><NumCartons>%s</NumCartons>" % (
            data, shipment.shipment_id, len(total_box_list))
            for box, qty_dict in box_no_product_dict.items():
                box_info = '<Carton><CartonId>%s</CartonId>' % (box)
                item_dict = ''
                for sku, qty in qty_dict.items():
                    item_dict = "%s <Item><SKU>%s</SKU><QuantityShipped>%s</QuantityShipped><QuantityInCase>%s</QuantityInCase></Item>" % (
                    item_dict, sku, qty[0],qty[1])
                box_info = "%s %s </Carton>" % (box_info, item_dict)
                data = "%s %s" % (data, box_info)
            data = "%s </CartonContentsRequest>" % (data)
        header = self.get_header(shipment.shipment_plan_id.instance_id)
        if data:
            data = "%s %s </Message></AmazonEnvelope>" % (header, data)
            proxy_data = instance.seller_id.get_proxy_server()
            marketplaceids = [instance.market_place_id]
            instance_id = instance.id
            kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token':instance.auth_token and str(instance.auth_token) or False,
                      'app_name':'amazon_ept',
                      'account_token':account.account_token,
                      'emipro_api':'create_carton_contents_requests',
                      'dbuuid':dbuuid,
                      'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                    instance.country_id.code,
                      'proxies':proxy_data,
                      'marketplaceids': marketplaceids,
                      'instance_id': instance_id,
                      'data': data,}
        
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                results = response.get('result')
                if results.get('FeedSubmissionInfo', {}).get('FeedSubmissionId', {}).get('value',
                                                                                         False):
                    last_feed_submission_id = results.get('FeedSubmissionInfo', {}).get(
                        'FeedSubmissionId', {}).get('value', False)

                    vals = {'message': data, 'feed_result_id': last_feed_submission_id,
                            'feed_submit_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                            'instance_id': instance.id, 'user_id': self._uid, 
                            'seller_id': instance.seller_id.id}
                    feed = feed_submit_obj.create(vals)

                    self.write({'is_update_inbound_carton_contents': True, 'feed_id': feed.id})
        return True

    @api.multi
    def cancel_shipment_in_amazon_via_shipment_lines(self):
        shipment=self
        ship_plan = shipment.shipment_plan_id
        instance = self.get_instance(shipment)
        address = ship_plan.ship_from_address_id
        name, add1, add2, city, postcode = address.name, address.street or '', address.street2 or '', address.city or '', address.zip or ''
        country = address.country_id and address.country_id.code or ''
        state = address.state_id and address.state_id.code or ''
        shipment_status = 'CANCELLED'
        if not shipment.shipment_id or not shipment.fulfill_center_id:
            raise Warning('You must have to first create Inbound Shipment Plan.')

        if self.is_manually_created:
            raise Warning("You can not cancel Inbound shipment from ERP which has created from Amazon")        

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        proxy_data = instance.seller_id.get_proxy_server()

        for x in range(0, len(shipment.odoo_shipment_line_ids), 20):
            ship_lines = shipment.odoo_shipment_line_ids[x:x + 20]
            sku_qty_dict = {}
            for line in ship_lines:
                sku_qty_dict.update({line.seller_sku: [str(int(line.quantity)), str(int(0))]})
            kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token':instance.auth_token and str(instance.auth_token) or False,
                      'app_name':'amazon_ept',
                      'account_token':account.account_token,
                      'emipro_api':'update_shipment_in_amazon',
                      'dbuuid':dbuuid,
                      'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                    instance.country_id.code,
                      'proxies':proxy_data,
                      'shipment_name': shipment.name,
                      'shipment_id':shipment.shipment_id,
                      'fulfill_center_id': shipment.fulfill_center_id,
                      'address_name': name,
                      'add1': add1,
                      'add2' : add2,
                      'city': city,
                      'state' : state,
                      'postcode': postcode,
                      'country': country,
                      'labelpreppreference': shipment.label_prep_type,
                      'shipment_status': shipment_status,
                      'inbound_box_content_status': shipment.intended_boxcontents_source,
                      'sku_qty_dict': sku_qty_dict,
                      'is_are_cases_required':shipment.shipment_plan_id.is_are_cases_required
                      }
            
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            break
        shipment.write({'state': 'CANCELLED'})
        flag = True
        for shipment_record in shipment.shipment_plan_id.odoo_shipment_ids:
            if shipment_record.state != 'CANCELLED':
                flag = False
                break
        flag and shipment.shipment_plan_id.write({'state': 'cancel'})
        return True

    @api.multi
    def cancel_shipment_in_amazon(self):
        plan_line_obj = self.env['inbound.shipment.plan.line']
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')        
        for shipment in self:
            stock_picking_obj = self.env['stock.picking']
            pickings = stock_picking_obj.search([
                ('odoo_shipment_id', '=', shipment.id),
                ('is_fba_wh_picking', '=', False),
                ('state', '=', 'done')
            ])
            if pickings:
                raise Warning(
                    "You can not cancel shipment because stock picking have already transfered from ERP")
            pickings = stock_picking_obj.search([
                ('state', 'not in', ['done', 'cancel']),
                ('odoo_shipment_id', '=', shipment.id),
                ('is_fba_wh_picking', '=', False),
            ])
            if not pickings:
                self.cancel_shipment_in_amazon_via_shipment_lines(shipment)
                continue
            for picking in pickings:
                odoo_shipment = picking.odoo_shipment_id
                ship_plan = picking.ship_plan_id
                instance = self.get_instance(odoo_shipment)
                address = picking.partner_id or ship_plan.ship_from_address_id
                name, add1, add2, city, postcode = address.name, address.street or '', address.street2 or '', address.city or '', address.zip or ''
                country = address.country_id and address.country_id.code or ''
                state = address.state_id and address.state_id.code or ''
                shipment_status = 'CANCELLED'
                amazon_product_obj = self.env['amazon.product.ept']
                if not odoo_shipment.shipment_id or not odoo_shipment.fulfill_center_id:
                    raise Warning('You must have to first create Inbound Shipment Plan.')
                proxy_data = instance.seller_id.get_proxy_server()
                for x in range(0, len(picking.move_lines), 20):
                    move_lines = picking.move_lines[x:x + 20]
                    sku_qty_dict = {}
                    for move in move_lines:
                        amazon_product = amazon_product_obj.search(
                            [('product_id', '=', move.product_id.id),
                             ('instance_id', '=', instance.id), ('fulfillment_by', '=', 'AFN')])
                        if not amazon_product:
                            raise Warning(
                                "Amazon Product is not available for this %s product code" % (
                                move.product_id.default_code))
                        line = plan_line_obj.search([('odoo_shipment_id', '=', odoo_shipment.id), (
                        'amazon_product_id', 'in', amazon_product.ids)])
                        sku_qty_dict.update({str(
                            line and line.seller_sku or amazon_product[0].seller_sku): str(
                            int(move.reserved_availability))})
                    kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                              'auth_token':instance.auth_token and str(instance.auth_token) or False,
                              'app_name':'amazon_ept',
                              'account_token':account.account_token,
                              'emipro_api':'update_shipment_in_amazon',
                              'dbuuid':dbuuid,
                              'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                            instance.country_id.code,
                              'proxies':proxy_data,
                              'shipment_name': shipment.name,
                              'shipment_id':shipment.shipment_id,
                              'fulfill_center_id': shipment.fulfill_center_id,
                              'address_name': name,
                              'add1': add1,
                              'add2' : add2,
                              'city': city,
                              'state' : state,
                              'postcode': postcode,
                              'country': country,
                              'labelpreppreference': shipment.label_prep_type,
                              'shipment_status': shipment_status,
                              'inbound_box_content_status': shipment.intended_boxcontents_source,
                              'sku_qty_dict': sku_qty_dict,
                              }
                    
                    response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                    if response.get('reason'):
                        raise Warning(response.get('reason'))
                    break
                picking.write({'inbound_ship_updated': True, 'shipment_status': 'CANCELLED'})

            shipment.picking_ids.action_cancel()
            shipment.write({'state': 'CANCELLED'})
            flag = True
            for shipment_record in shipment.shipment_plan_id.odoo_shipment_ids:
                if shipment_record.state != 'CANCELLED':
                    flag = False
                    break
            flag and shipment.shipment_plan_id.write({'state': 'cancel'})
        return True

    @api.model
    def auto_export_ltl_parcel_tracking(self, args={}):
        picking_obj = self.env['stock.picking']
        seller_id = args.get('seller_id', False)
        if seller_id:
            shipments = self.search(['|',('instance_id_ept.seller_id','=',seller_id),
                                     ('shipment_plan_id.instance_id.seller_id','=',seller_id),
                                     ('shipping_type','=','ltl'),
                                     ('is_partnered','=',False),
                                     ('updated_in_amazon','=',False),
                                     ('pro_number','!=',False),                                     
                                     ('state','in',['WORKING']),('transport_content_exported','=',False)
                                     ])
            args.update({'auto_called': True})
            for shipment in shipments:
                pickings = picking_obj.search([('is_fba_wh_picking', '=', False),
                                               ('odoo_shipment_id', '=', shipment.id),
                                               ('state', '=', 'done'),
                                               ('updated_in_amazon', '=', False)
                                               ])
                if pickings:
                    shipment.with_context(args).export_non_partnered_ltl_parcel_tracking()
            shipments = self.search([
                                     '|',('instance_id_ept.seller_id','=',seller_id),
                                     ('shipment_plan_id.instance_id.seller_id','=',seller_id),
                                     ('shipping_type','=','ltl'),
                                     ('is_partnered','=',True),
                                     ('updated_in_amazon','=',False),
                                     ('state','in',['WORKING']),('transport_content_exported','=',False)
                                     ])
            args.update({'auto_called': True})
            for shipment in shipments:
                pickings = picking_obj.search([('is_fba_wh_picking', '=', False),
                                               ('odoo_shipment_id', '=', shipment.id),
                                               ('state', '=', 'done'),
                                               ('updated_in_amazon', '=', False)
                                               ])
                if pickings:
                    shipment.with_context(args).export_partnered_ltl_parcel()
        return True

    @api.model
    def auto_export_small_parcel_tracking(self, args={}):
        picking_obj = self.env['stock.picking']
        seller_id = args.get('seller_id', False)
        if seller_id:
            shipments = self.search(['|',('instance_id_ept.seller_id','=',seller_id),
                                     ('shipment_plan_id.instance_id.seller_id','=',seller_id),
                                     ('shipping_type','=','sp'),
                                     ('is_partnered','=',False),
                                     ('updated_in_amazon','=',False),
                                     ('state','in',['WORKING']),('transport_content_exported','=',False)
                                     ])
            args.update({'auto_called': True})
            for shipment in shipments:
                pickings = picking_obj.search([('is_fba_wh_picking', '=', False),
                                               ('odoo_shipment_id', '=', shipment.id),
                                               ('state', '=', 'done'),
                                               ('updated_in_amazon', '=', False)
                                               ])
                if pickings:
                    shipment.with_context(args).export_non_partnered_small_parcel_tracking()

            shipments = self.search(['|',('instance_id_ept.seller_id','=',seller_id),
                                     ('shipment_plan_id.instance_id.seller_id','=',seller_id),
                                     ('shipping_type','=','sp'),
                                     ('is_partnered','=',True),
                                     ('updated_in_amazon','=',False),
                                     ('state','in',['WORKING']),('transport_content_exported','=',False)
                                     ])
            args.update({'auto_called': True})
            for shipment in shipments:
                pickings = picking_obj.search([('is_fba_wh_picking', '=', False),
                                               ('odoo_shipment_id', '=', shipment.id),
                                               ('state', '=', 'done'),
                                               ('updated_in_amazon', '=', False)
                                               ])
                if pickings:
                    shipment.with_context(args).export_partnered_small_parcel()
        return True

    @api.multi
    def update_shipment_in_amazon(self, picking, sku_qty_dict, instance, fba_shipment, job,
                                  auto_called):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        address = picking.partner_id or fba_shipment.shipment_plan_id.ship_from_address_id
        name, add1, add2, city, postcode = address.name, address.street or '', address.street2 or '', address.city or '', address.zip or ''
        country = address.country_id and address.country_id.code or ''
        state = address.state_id and address.state_id.code or ''
        shipment_status = 'SHIPPED'
        
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        proxy_data = instance.seller_id.get_proxy_server()

        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'update_shipment_in_amazon',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxies':proxy_data,
                  'shipment_name': fba_shipment.name,
                  'shipment_id':fba_shipment.shipment_id,
                  'fulfill_center_id': fba_shipment.fulfill_center_id,
                  'address_name': name,
                  'add1': add1,
                  'add2' : add2,
                  'city': city,
                  'state' : state,
                  'postcode': postcode,
                  'country': country,
                  'labelpreppreference': fba_shipment.label_prep_type,
                  'shipment_status': shipment_status,
                  'inbound_box_content_status': fba_shipment.intended_boxcontents_source,
                  'sku_qty_dict': sku_qty_dict,
                  }
        
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            error_value = response.get('reason')
            if job:
                message = '%s %s' % (error_value, fba_shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': fba_shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': fba_shipment.name,
                        'message': error_value,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
            else:
                if not auto_called:
                    raise Warning(error_value)
            fba_shipment.write(
                {'state': 'ERROR', 'updated_in_amazon': False, 'transport_content_exported': False})
            picking.write({'updated_in_amazon': False})
        return True

    @api.multi
    def update_shipment_ept(self, fba_shipment, pickings, back_orders, auto_called, instance,
                            job=False):
        plan_line_obj = self.env['inbound.shipment.plan.line']
        amazon_product_obj = self.env['amazon.product.ept']
        sku_qty_dict = {}
        sku_list = []
        instance = self.get_instance(fba_shipment)
        for picking in pickings:
            for x in range(0, len(picking.move_lines), 1):
                move_lines = picking.move_lines[x:x + 1]
                sku_qty_dict = {}
                for move in move_lines:
                    if move.state == 'done':
                        amazon_product = amazon_product_obj.search(
                            [('product_id', '=', move.product_id.id),
                             ('instance_id', '=', instance.id), ('fulfillment_by', '=', 'AFN')])
                        if not amazon_product:
                            raise Warning(
                                "Amazon Product is not available for this %s product code" % (
                                move.product_id.default_code))
                        line = plan_line_obj.search(
                            [('odoo_shipment_id', '=', picking.odoo_shipment_id.id),
                             ('amazon_product_id', 'in', amazon_product.ids)])
                        qty = sku_qty_dict.get(
                            str(line and line.seller_sku or amazon_product[0].seller_sku), 0.0)
                        qty = move.product_qty + float(qty)
                        sku_qty_dict.update({str(
                            line and line.seller_sku or amazon_product[0].seller_sku): str(
                            int(qty))})
                self.update_shipment_in_amazon(picking, sku_qty_dict, instance, fba_shipment,
                                               job, auto_called)
                sku_list = sku_list + sku_qty_dict.keys()
        for picking in back_orders:
            for x in range(0, len(picking.move_lines), 20):
                move_lines = picking.move_lines[x:x + 20]
                sku_qty_dict = {}
                for move in move_lines:
                    amazon_product = amazon_product_obj.search(
                        [('product_id', '=', move.product_id.id), ('instance_id', '=', instance.id),
                         ('fulfillment_by', '=', 'AFN')])
                    if not amazon_product:
                        raise Warning("Amazon Product is not available for this %s product code" % (
                        move.product_id.default_code))
                    line = plan_line_obj.search(
                        [('odoo_shipment_id', '=', picking.odoo_shipment_id.id),
                         ('amazon_product_id', 'in', amazon_product.ids)])
                    if str(line and line.seller_sku or amazon_product[0].seller_sku) in sku_list:
                        continue
                    if str(line and line.seller_sku or amazon_product[
                        0].seller_sku) not in sku_qty_dict:
                        sku_qty_dict.update({str(
                            line and line.seller_sku or amazon_product[0].seller_sku): str(
                            int(0.0))})
                self.update_shipment_in_amazon(picking, sku_qty_dict, instance, fba_shipment,
                                               job, auto_called)
        pickings.write({'shipment_status': 'SHIPPED'})
        return True

    @api.multi
    def export_non_partnered_small_parcel_tracking(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        ctx = self._context.copy() or {}
        auto_called = ctx.get('auto_called', False)
        stock_picking_obj = self.env['stock.picking']
        for shipment in self:
            instance = self.get_instance(shipment)
            job_log_vals = {
                'skip_process': True,
                'message': 'Amazon Inbound Shipment Update Parcel (Non partnered(SP))',
                'application': 'update_inbound_shipment',
                'operation_type': 'export',
                'instance_id': instance.id
            }
            job = amazon_log_book_obj.create(job_log_vals)
            pickings = stock_picking_obj.search([
                ('state', '=', 'done'),
                ('odoo_shipment_id', '=', shipment.id),
                ('is_fba_wh_picking', '=', False),
                ('updated_in_amazon', '=', False),
            ])
            if not pickings:
                message = 'Inbound Shipment %s is not update in amazon because of system is not found any transfered picking' % (
                shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
            if not instance.update_partially_inbound_shipment:
                back_orders = stock_picking_obj.search([
                    ('state', 'not in', ['done', 'cancel']),
                    ('odoo_shipment_id', '=', shipment.id),
                    ('is_fba_wh_picking', '=', False),
                    ('updated_in_amazon', '=', False),
                ])
                if back_orders:
                    message = 'Inbound Shipment %s is not update in amazon because backorder not processed in the system' % (
                    shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
        for fba_shipment in self:
            pickings = stock_picking_obj.search([
                ('state', '=', 'done'),
                ('odoo_shipment_id', '=', fba_shipment.id),
                ('is_fba_wh_picking', '=', False)
            ])
            if not pickings:
                continue
            if not instance.update_partially_inbound_shipment:
                back_orders = stock_picking_obj.search([
                    ('state', 'not in', ['done', 'cancel']),
                    ('odoo_shipment_id', '=', fba_shipment.id),
                    ('is_fba_wh_picking', '=', False),
                    ('updated_in_amazon', '=', False),
                ])
                if back_orders:
                    continue
            in_shipment_rec = pickings[0].odoo_shipment_id
            data = {'ShipmentId': in_shipment_rec.shipment_id,
                    'IsPartnered': 'true' if in_shipment_rec.is_partnered else 'false',
                    'ShipmentType': 'SP' if in_shipment_rec.shipping_type == 'sp' else 'LTL'}
            if pickings[0].carrier_id:
                carrier_name = pickings[0].carrier_id and \
                               pickings[0].carrier_id.amz_delivery_carrier_code and \
                               pickings[0].carrier_id.amz_delivery_carrier_code.name or 'OTHER'
            else:
                carrier_name = 'OTHER'
            data.update(
                {'TransportDetails.NonPartneredSmallParcelData.CarrierName': str(carrier_name)})
            traking_dict = {}
            count_box = 0
            tacking_no_list = []
            instance = self.get_instance(fba_shipment)
            if instance.update_partially_inbound_shipment:
                back_orders = stock_picking_obj.search([
                    ('state', 'not in', ['done', 'cancel']),
                    ('odoo_shipment_id', '=', fba_shipment.id),
                    ('is_fba_wh_picking', '=', False),
                    ('updated_in_amazon', '=', False),
                ])
                back_orders and back_orders.action_cancel()
            else:
                back_orders = []

            for picking in pickings:
                in_shipment_rec = picking.odoo_shipment_id
                instance = self.get_instance(in_shipment_rec)
                """done for v11 op means pack op--> move_line"""
                for op in picking.move_line_ids:
                    tracking_no = op.result_package_id and op.result_package_id.tracking_no
                    if tracking_no and tracking_no not in tacking_no_list:
                        count_box += 1
                        traking_dict.update({
                            'TransportDetails.NonPartneredSmallParcelData.PackageList.member.' + str(
                                count_box) + '.TrackingId': str(tracking_no),
                        })
                        tacking_no_list.append(tracking_no)
                if not traking_dict:
                    message = 'Inbound Shipment %s is not update in amazon because Tracking ' \
                              'number not found in the system' % (
                    shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    continue
            while True:
                if count_box >= in_shipment_rec.box_count:
                    break
                else:
                    count_box += 1
                    traking_dict.update({
                        'TransportDetails.NonPartneredSmallParcelData.PackageList.member.' + str(
                            count_box) + '.TrackingId': str(' '),
                    })

            data.update(traking_dict)
            proxy_data = instance.seller_id.get_proxy_server()
            
            result = {}
            account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
            dbuuid = self.env['ir.config_parameter'].sudo(
            ).get_param('database.uuid')
                    
            kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token':instance.auth_token and str(instance.auth_token) or False,
                      'app_name':'amazon_ept',
                      'account_token':account.account_token,
                      'emipro_api':'export_non_partnered_small_parcel_tracking',
                      'dbuuid':dbuuid,
                      'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                    instance.country_id.code,
                      'proxies':proxy_data,
                      'data': data,}
            
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('result'):
                result = response.get('result')
                pickings.write({'updated_in_amazon': True})
                transport_status = result and result.get('TransportResult', {}).get(
                    'TransportStatus', {}).get('value', '')
                if transport_status in transport_status_list:
                    in_shipment_rec.write(
                        {'transport_state': transport_status, 'transport_content_exported': True,
                         'state': 'SHIPPED', 'updated_in_amazon': True})
            elif response.get('reason'):
                error_value = response.get('reason')
                message = '%s %s' % (error_value, shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                fba_shipment.write({'state': 'ERROR'})
            if fba_shipment.state != 'ERROR':
                self.update_shipment_ept(fba_shipment, pickings, back_orders, auto_called, instance,job)
        if not job.transaction_log_ids:
            job.unlink()
        return True

    @api.multi
    def export_partnered_small_parcel(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        for shipment in self:
            instance = self.get_instance(shipment)
            job_log_vals = {
                'skip_process': True,
                'message': 'Amazon Inbound Shipment Update Parcel (partnered(SP))',
                'application': 'update_inbound_shipment',
                'operation_type': 'export',
                'instance_id': instance.id
            }
            job = amazon_log_book_obj.create(job_log_vals)

            data = {'ShipmentId': shipment.shipment_id,
                    'IsPartnered': 'true' if shipment.is_partnered else 'false',
                    'ShipmentType': 'SP' if shipment.shipping_type == 'sp' else 'LTL'}
            if not shipment.partnered_small_parcel_ids:
                message = 'Inbound Shipment %s is not update in amazon because Parcel not found ' \
                          'for update in amazon' % (shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                continue
            count = 1
            flag = True
            for package in shipment.partnered_small_parcel_ids:
                if not package.ul_id:
                    message = 'Inbound Shipment %s is not update in amazon because dimension ' \
                              'package not found for update' % (shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    flag = False
                    break
                if package.ul_id.height <= 0.0 or package.ul_id.width <= 0.0 or package.ul_id.length <= 0.0:
                    message = 'Inbound Shipment %s is not update in amazon because Dimension ' \
                              'Length, Width and Height value must be greater than zero.' % (
                    shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    flag = False
                    break
                dimension_unit = package.ul_id.dimension_unit or 'centimeters'
                if shipment.carrier_id:
                    data.update({
                                    'TransportDetails.PartneredSmallParcelData.CarrierName': shipment.carrier_id and
                                                                                             shipment.carrier_id.amz_delivery_carrier_code and
                                                                                             shipment.carrier_id.amz_delivery_carrier_code.name or
                                                                                             shipment.carrier_id.name})
                data.update({
                                'TransportDetails.PartneredSmallParcelData.PackageList.member.%d.Dimensions.Unit' % (
                                count): dimension_unit})
                data.update({
                                'TransportDetails.PartneredSmallParcelData.PackageList.member.%d.Dimensions.Length' % (
                                count): str(package.ul_id.length)})
                data.update({
                                'TransportDetails.PartneredSmallParcelData.PackageList.member.%d.Dimensions.Width' % (
                                count): str(package.ul_id.width)})
                data.update({
                                'TransportDetails.PartneredSmallParcelData.PackageList.member.%d.Dimensions.Height' % (
                                count): str(package.ul_id.height)})
                data.update({
                                'TransportDetails.PartneredSmallParcelData.PackageList.member.%d.Weight.Unit' % (
                                count): package.weight_unit})
                data.update({
                                'TransportDetails.PartneredSmallParcelData.PackageList.member.%d.Weight.Value' % (
                                count): str(int(package.weight_value))})
                count += 1
            if flag:
                proxy_data = instance.seller_id.get_proxy_server()
                kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                          'auth_token':instance.auth_token and str(instance.auth_token) or False,
                          'app_name':'amazon_ept',
                          'account_token':account.account_token,
                          'emipro_api':'put_transport_content',
                          'dbuuid':dbuuid,
                          'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                        instance.country_id.code,
                          'proxy_data': proxy_data,
                          'data': data, }

                result = {}
                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):
                    error_value = response.get('reason')
                    message = '%s %s' % (error_value, shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    shipment.write({'state': 'ERROR'})                
                else:
                    result = response.get('result')
                transport_status = result and result.get('TransportResult', {}).get(
                    'TransportStatus', {}).get('value', '')
                if transport_status in transport_status_list:
                    shipment.write(
                        {'transport_state': transport_status, 'transport_content_exported': True,
                         'updated_in_amazon': True})
        if not job.transaction_log_ids:
            job.unlink()
        return True

    @api.multi
    def export_partnered_ltl_parcel(self):
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        for shipment in self:
            amazon_transaction_obj = self.env['amazon.transaction.log']
            amazon_log_book_obj = self.env['amazon.process.log.book']
            job_log_vals = {
                'skip_process': True,
                'message': 'Amazon Inbound Shipment Update Parcel (Non partnered(SP))',
                'application': 'update_inbound_shipment',
                'operation_type': 'export',
                'instance_id': shipment.shipment_plan_id.instance_id.id
            }
            job = amazon_log_book_obj.create(job_log_vals)

            name = shipment.partnered_ltl_id.name or ''
            phone = shipment.partnered_ltl_id.phone or ''
            email = shipment.partnered_ltl_id.email or ''
            fax = shipment.partnered_ltl_id.fax or ''
            if not name or not phone or not email or not fax:
                message = 'Invalid contact details found check name/phone/email/fax for contact %s' % (
                name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                continue
            if len(shipment.partnered_ltl_ids.ids) <= 0:
                message = 'Number of box must be greater than zero for shipment %s' % (
                shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                continue
            data = {'ShipmentId': shipment.shipment_id,
                    'IsPartnered': 'true' if shipment.is_partnered else 'false',
                    'ShipmentType': 'SP' if shipment.shipping_type == 'sp' else 'LTL',
                    'TransportDetails.PartneredLtlData.Contact.Name': name,
                    'TransportDetails.PartneredLtlData.Contact.Phone': str(phone),
                    'TransportDetails.PartneredLtlData.Contact.Email': email,
                    'TransportDetails.PartneredLtlData.Contact.Fax': str(fax),
                    'TransportDetails.PartneredLtlData.BoxCount': str(
                        len(shipment.partnered_ltl_ids.ids)),
                    'TransportDetails.PartneredLtlData.FreightReadyDate': shipment.freight_ready_date.strftime("%Y-%m-%d")
                    }
            instance = self.get_instance(shipment)
            if shipment.seller_freight_class:
                data.update({
                                'TransportDetails.PartneredLtlData.SellerFreightClass': shipment.seller_freight_class})
            count = 1
            # Not required parameter, so if given then we will set otherwise we skip it.
            flag = True
            for pallet in shipment.partnered_ltl_ids:
                if not pallet.ul_id:
                    message = 'Inbound Shipment %s is not update in amazon because of dimension ' \
                              'for package not found' % (shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    flag = False
                    break
                if pallet.ul_id.length <= 0.0 or pallet.ul_id.width <= 0.0 or pallet.ul_id.height <= 0.0:
                    message = 'Inbound Shipment %s is not update in amazon because of Dimension ' \
                              'Length, Width and Height value must be greater that zero' % (
                    shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    flag = False
                    break
                dimension_unit = pallet.ul_id.dimension_unit or 'centimeters'
                data.update({
                                'TransportDetails.PartneredLtlData.PalletList.member.%d.Dimensions.Unit' % (
                                count): dimension_unit})
                data.update({
                                'TransportDetails.PartneredLtlData.PalletList.member.%d.Dimensions.Length' % (
                                count): str(pallet.ul_id.length)})
                data.update({
                                'TransportDetails.PartneredLtlData.PalletList.member.%d.Dimensions.Width' % (
                                count): str(pallet.ul_id.width)})
                data.update({
                                'TransportDetails.PartneredLtlData.PalletList.member.%d.Dimensions.Height' % (
                                count): str(pallet.ul_id.height)})

                # Not required parameter, so if given then we will set otherwise we skip it.
                if pallet.weight_unit and pallet.weight_value:
                    data.update({
                                    'TransportDetails.PartneredLtlData.PalletList.member.%d.Weight.Unit' % (
                                    count): pallet.weight_unit})
                    data.update({
                                    'TransportDetails.PartneredLtlData.PalletList.member.%d.Weight.Value' % (
                                    count): str(pallet.weight_value)})
                data.update({'TransportDetails.PartneredLtlData.PalletList.member.%d.IsStacked' % (
                count): 'true' if pallet.is_stacked else 'false'})
                count += 1

            # Not required parameter, so if given then we will set otherwise we skip it.
            if shipment.amazon_shipment_weight_unit and shipment.amazon_shipment_weight:
                data.update({'TransportDetails.PartneredLtlData.TotalWeight.Unit': str(
                    shipment.amazon_shipment_weight_unit)})
                data.update({'TransportDetails.PartneredLtlData.TotalWeight.Value': str(
                    shipment.amazon_shipment_weight)})
#            if shipment.seller_declared_value and shipment.declared_value_currency_id:
#                data.update({
#                                'TransportDetails.PartneredLtlData.SellerDeclaredValue.CurrencyCode': str(
#                                    shipment.declared_value_currency_id.name)})
#                data.update({'TransportDetails.PartneredLtlData.SellerDeclaredValue.Value': str(round(shipment.seller_declared_value,2)
#                    )})

            if flag:
                proxy_data = instance.seller_id.get_proxy_server()
                kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                          'auth_token':instance.auth_token and str(instance.auth_token) or False,
                          'app_name':'amazon_ept',
                          'account_token':account.account_token,
                          'emipro_api':'put_transport_content',
                          'dbuuid':dbuuid,
                          'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                        instance.country_id.code,
                          'proxy_data': proxy_data,
                          'data': data, }
                
                result = {}
                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):
                    error_value = response.get('reason')
                    message = '%s %s' % (error_value, shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    shipment.write({'state': 'ERROR'})                
                else:
                    result = response.get('result')
                transport_status = result and result.get('TransportResult', {}).get(
                    'TransportStatus', {}).get('value', '')
                if transport_status in transport_status_list:
                    self.write(
                        {'transport_state': transport_status, 'transport_content_exported': True})
        if not job.transaction_log_ids:
            job.unlink()
        return True

    @api.multi
    def create_shipment_picking(self):
        self.ensure_one()
        if self.is_manually_created:
            self.create_procurements(self,self.instance_id_ept,False)
        else:            
            inbound_shipment_plan_obj=self.env['inbound.shipment.plan.ept']
            inbound_shipment_plan_obj.create_procurements(self)
        return True

    @api.model
    def create_procurements(self, odoo_shipments,instance,job=False):
        proc_group_obj = self.env['procurement.group']
        picking_obj = self.env['stock.picking']
        shipping_obj = self.env['shipping.report.request.history']
        location_route_obj = self.env['stock.location.route']
        amazon_log_obj=self.env['amazon.process.log.book']
        amazon_transaction_obj=self.env['amazon.transaction.log'] 
        group_wh_dict = {}
        for shipment in odoo_shipments:
            proc_group = proc_group_obj.create({'odoo_shipment_id':shipment.id,'name':shipment.name})

            fulfill_center = shipment.fulfill_center_id
#             ship_plan = shipment.shipment_plan_id
            fulfillment_center,warehouse = shipping_obj.get_warehouse(fulfill_center,instance)#ship_plan.instance_id
            if not warehouse:
                if not job:
                    job=amazon_log_obj.create({'application':'other',
                                               'operation_type':'export',
                                               'instance_id':instance.id,
                                               'skip_process':True
                                               })
                error_value='No any warehouse found related to fulfillment center %s. Please set fulfillment center %s in warehouse || shipment %s.'%(fulfill_center,fulfill_center,shipment.name)
                amazon_transaction_obj.create({'log_type':'not_found',
                                               'action_type':'terminate_process_with_log',
                                               'operation_type':'export',
                                               'message':error_value,
                                               'model_id':amazon_transaction_obj.get_model_id('amazon.inbound.shipment.ept'),
                                               'res_id':shipment.id,
                                               'job_id':job.id
                                               })                
                continue
            location_routes = location_route_obj.search([('supplied_wh_id','=',warehouse.id),('supplier_wh_id','=',shipment.from_warehouse_id.id)])
            if not location_routes:
                if not job:
                    job=amazon_log_obj.create({'application':'other',
                                               'operation_type':'export',
                                               'instance_id':shipment.shipment_plan_id.instance_id.id,
                                               'skip_process':True
                                               })
                error_value='Location routes are not found. Please configure routes in warehouse properly || warehouse %s & shipment %s.'%(warehouse.name,shipment.name)
                amazon_transaction_obj.create({'log_type':'not_found',
                                               'action_type':'terminate_process_with_log',
                                               'operation_type':'export',
                                               'message':error_value,
                                               'model_id':amazon_transaction_obj.get_model_id('amazon.inbound.shipment.ept'),
                                               'res_id':shipment.id,
                                               'job_id':job.id
                                               })                
                continue
            location_routes = location_routes[0]
            group_wh_dict.update({proc_group:warehouse})
            for line in shipment.odoo_shipment_line_ids:
                qty = line.quantity
                amazon_product = line.amazon_product_id
                datas={'route_ids':location_routes, 
                       'group_id':proc_group,                       
                       'company_id':instance.id, 
                       'warehouse_id': warehouse, 
                       'priority': '1'
                       }
                proc_group_obj.run(amazon_product.product_id,qty,amazon_product.uom_id,warehouse.lot_stock_id,amazon_product.name,shipment.name,datas)
                                    
        if group_wh_dict:
            for group,warehouse in group_wh_dict.items(): 
                picking = picking_obj.search([('group_id','=',group.id),('picking_type_id.warehouse_id','=',warehouse.id)])
                if picking:
                    picking.write({'is_fba_wh_picking':True})
        return True

    @api.multi
    def export_non_partnered_ltl_parcel_tracking(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        stock_picking_obj = self.env['stock.picking']
        ctx = self._context
        auto_called = ctx.get('auto_called', False)
        shipment_with_no_pro_number = []
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')        
        for shipment in self:
            instance = self.get_instance(shipment)
            job_log_vals = {
                'skip_process': True,
                'message': 'Amazon Inbound Shipment Update Parcel (Non partnered(LTL))',
                'application': 'update_inbound_shipment',
                'operation_type': 'export',
                'instance_id': instance.id
            }
            job = amazon_log_book_obj.create(job_log_vals)
            pickings = stock_picking_obj.search([
                ('state', '=', 'done'),
                ('odoo_shipment_id', '=', shipment.id),
                ('is_fba_wh_picking', '=', False),
                ('updated_in_amazon', '=', False),
            ])
            if not pickings:
                message = 'Inbound Shipment %s is not update in amazon because of system is ' \
                          'not found any transfered picking' % (shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)

            if not instance.update_partially_inbound_shipment:
                back_orders = stock_picking_obj.search([
                    ('state', 'not in', ['done', 'cancel']),
                    ('odoo_shipment_id', '=', shipment.id),
                    ('is_fba_wh_picking', '=', False),
                    ('updated_in_amazon', '=', False),
                ])
                if not back_orders:
                    message = 'Inbound Shipment %s is not update in amazon because backorder not ' \
                              'processed in the system' % (shipment.name)
                    if not amazon_transaction_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.inbound.shipment.ept'),
                            'res_id': shipment.id or 0,
                            'log_type': 'not_found',
                            'user_id': self.env.uid,
                            'skip_record': True,
                            'amazon_order_reference': shipment.name,
                            'message': message,
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
        for shipment in self:
            instance = self.get_instance(shipment)
            if not shipment.pro_number:
                shipment_with_no_pro_number.append(shipment.name)
                continue
            data = {'ShipmentId': shipment.shipment_id,
                    'IsPartnered': 'true' if shipment.is_partnered else 'false',
                    'ShipmentType': 'SP' if shipment.shipping_type == 'sp' else 'LTL'}

            pickings = stock_picking_obj.search([
                ('state', '=', 'done'),
                ('odoo_shipment_id', '=', shipment.id),
                ('is_fba_wh_picking', '=', False),
                ('updated_in_amazon', '=', False),
            ])
            if not pickings:
                continue
            if not instance.update_partially_inbound_shipment:
                back_orders = stock_picking_obj.search([
                    ('state', 'not in', ['done', 'cancel']),
                    ('odoo_shipment_id', '=', shipment.id),
                    ('is_fba_wh_picking', '=', False),
                    ('updated_in_amazon', '=', False),
                ])
                if back_orders:
                    continue

            if not shipment.carrier_id:
                fba_pickings = shipment.picking_ids.filtered('is_fba_wh_picking')
                if fba_pickings and fba_pickings[0].carrier_id:
                    carrier_name = fba_pickings[0].carrier_id.name
                else:
                    carrier_name = 'OTHER'
            else:
                carrier_name = shipment.carrier_id.name

            if instance.update_partially_inbound_shipment:
                back_orders = stock_picking_obj.search([
                    ('state', 'not in', ['done', 'cancel']),
                    ('odoo_shipment_id', '=', shipment.id),
                    ('is_fba_wh_picking', '=', False),
                    ('updated_in_amazon', '=', False),
                ])
                back_orders and back_orders.action_cancel()
            else:
                back_orders = []
            data.update({'TransportDetails.NonPartneredLtlData.CarrierName': str(carrier_name)})
            data.update(
                {'TransportDetails.NonPartneredLtlData.ProNumber': str(shipment.pro_number)})
            proxy_data = instance.seller_id.get_proxy_server()
            kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token':instance.auth_token and str(instance.auth_token) or False,
                      'app_name':'amazon_ept',
                      'account_token':account.account_token,
                      'emipro_api':'put_transport_content',
                      'dbuuid':dbuuid,
                      'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                    instance.country_id.code,
                      'proxy_data': proxy_data,
                      'data': data, }
            
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                error_value = response.get('reason')
                message = '%s %s' % (error_value, shipment.name)
                if not amazon_transaction_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'res_id': shipment.id or 0,
                        'log_type': 'not_found',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': shipment.name,
                        'message': message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                shipment.write({'state': 'ERROR'})
            if shipment.state != 'ERROR':
                if transport_status in transport_status_list:
                    shipment.write(
                        {'transport_state': transport_status, 'transport_content_exported': True,
                         'state': 'SHIPPED', 'updated_in_amazon': True})
                self.update_shipment_ept(shipment, pickings, back_orders, auto_called, instance,job)
        if not job.transaction_log_ids:
            job.unlink()
        return True

    "=========================================================================================================="
    # Comment By Dipesh Tanna#
    "=========================================================================================================="
    """
        In some seller account amazon default set partner as carrier.
        If Default carrier is partnered carrier & we send request for label 
        (ERP shipment type is non partnered) then amazon will give an error        
        That's why we have updated non partnered carrier
        Here We are passing tracking id space / ProNumber ######### because amazon not give any 
        api to direct update carrier
        due to amazon support we have done this type of fix code        
    """

    @api.multi
    def update_non_partered_carrier(self):
        ctx = self._context.copy() or {}
        auto_called = ctx.get('auto_called', False)
        instance = self.get_instance(self)
        
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        data = {'ShipmentId': self.shipment_id,
                'IsPartnered': 'true' if self.is_partnered else 'false',
                'ShipmentType': 'SP' if self.shipping_type == 'sp' else 'LTL'}
        if self.shipping_type == 'sp':
            data.update({
                'TransportDetails.NonPartneredSmallParcelData.CarrierName': 'OTHER',
                'TransportDetails.NonPartneredSmallParcelData.PackageList.member.' + str(
                    '1') + '.TrackingId': str(' '),
            })
        else:
            carrier_code = self.carrier_id and \
                           self.carrier_id.amz_delivery_carrier_code and \
                           self.carrier_id.amz_delivery_carrier_code.name or 'OTHER'
            data.update({
                'TransportDetails.NonPartneredLtlData.ProNumber': '##########',
                'TransportDetails.NonPartneredLtlData.CarrierName': carrier_code,
            })

        proxy_data = instance.seller_id.get_proxy_server()
        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'put_transport_content',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxy_data': proxy_data,
                  'data': data, }
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):        
            error_value = response.get('reason')
            if not auto_called:
                raise Warning(error_value)
            _logger.error(error_value)
        return True

    @api.multi
    def estimate_transport_request(self):
        instance = self.get_instance(self)
        proxy_data = instance.seller_id.get_proxy_server()

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'estimate_transport_request',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxy_data': proxy_data,
                  'shipment_id': self.shipment_id, }

        result = {}
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            error_value = response.get('reason')
            raise Warning(error_value)
        else:
            result = response.get('result')

        transport_status = result and result.get('TransportResult', {}).get(
            'TransportStatus', {}).get('value', '')
        if transport_status in transport_status_list:
            self.write({'transport_state': transport_status})
            self.get_transport_content()
        return True

    @api.model
    def check_already_shipment_updated_in_amazon(self, instance, shipment_id):
        """Create Object for the integrate with amazon"""
        proxy_data = instance.seller_id.get_proxy_server()
        
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                   'auth_token':instance.auth_token and str(instance.auth_token) or False,
                   'app_name':'amazon_ept',
                   'account_token':account.account_token,
                   'emipro_api':'get_transport_content',
                   'dbuuid':dbuuid,
                   'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                 instance.country_id.code,
                   'proxy_data': proxy_data,
                   'shipment_id': shipment_id, }

        result = {}
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            result = response.get('result')        

        transport_detail = result.get('TransportContent', {}).get('TransportDetails', {})
        packages = transport_detail.get('NonPartneredSmallParcelData', {}).get('PackageList',
                                                                               {}).get('member', [])
        package_list = []
        if not isinstance(packages, list):
            package_list.append(packages)
        else:
            package_list = packages
        tracking_number_list = []
        for package in package_list:
            tracking_number_list.append(package.get('TrackingId', {}).get('value', ''))
        return tracking_number_list

    @api.multi
    def get_transport_content(self):
        instance = self.get_instance(self)
        proxy_data = instance.seller_id.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                   'auth_token':instance.auth_token and str(instance.auth_token) or False,
                   'app_name':'amazon_ept',
                   'account_token':account.account_token,
                   'emipro_api':'get_transport_content',
                   'dbuuid':dbuuid,
                   'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                 instance.country_id.code,
                   'proxy_data': proxy_data,
                   'shipment_id': self.shipment_id, }

        result = {}
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            result = response.get('result')  

        transport_result = result.get('TransportContent', {}).get('TransportResult', {})
        transport_detail = result.get('TransportContent', {}).get('TransportDetails', {})
        transport_header = result.get('TransportContent', {}).get('TransportHeader', {})

        transport_status = transport_result.get('TransportStatus', {}).get('value', '')
        ship_type = transport_header.get('ShipmentType', {}).get('value', '')
        is_partnered = True if transport_header.get('IsPartnered', {}).get('value',
                                                                           '') == 'true' else False

        if is_partnered and ship_type == 'SP' and transport_status in ['ESTIMATED', 'CONFIRMING',
                                                                       'CONFIRMED']:
            small_parcel_data = transport_detail.get('PartneredSmallParcelData', {})
            self.set_estimate_amount(small_parcel_data)
            self.setup_partnered_small_parcel_data(small_parcel_data)
        elif is_partnered and ship_type == 'LTL' and transport_status in ['ESTIMATED', 'CONFIRMING',
                                                                          'CONFIRMED']:
            parcel_data = transport_detail.get('PartneredLtlData', {})
            self.set_estimate_amount(parcel_data)
            self.setup_partnered_ltl_data(parcel_data)
        if transport_status in transport_status_list:
            self.write({'transport_state': transport_status})
        return True

    @api.multi
    def reset_inbound_shipment(self):
        self.ensure_one()
        self.transport_content_exported = False
        self.transport_state = 'draft'
        return True

    @api.multi
    def confirm_transport_request(self):
        instance = self.get_instance(self)
        proxy_data = instance.seller_id.get_proxy_server()
        
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'confirm_transport_request',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxy_data': proxy_data,
                  'shipment_id': self.shipment_id, }
    
        result = {}
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            error_value = response.get('reason')
            raise Warning(error_value)
        else:
            result = response.get('result')            
            
        transport_status = result.get('TransportResult', {}).get('TransportStatus', {}).get('value',
                                                                                            '')
        if transport_status in transport_status_list:
            self.write({'transport_state': transport_status})
        self.get_transport_content()
        return True

    @api.multi
    def void_transport_request(self):
        instance = self.get_instance(self)
        proxy_data = instance.seller_id.get_proxy_server()
        result = {}
        if not self.void_deadline_date:
            self.get_transport_content()

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'void_transport_request',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxy_data': proxy_data,
                  'shipmet_id': self.shipment_id, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            error_value = response.get('reason')
            raise Warning(error_value)
        else:
            result = response.get('result') 
        
        transport_status = result and result.get('TransportResult', {}).get(
            'TransportStatus', {}).get('value', '')
        if transport_status in transport_status_list:
            self.write({'transport_state': transport_status})
            self.reset_inbound_shipment()
        return True

    @api.multi
    def set_estimate_amount(self, parcel_data):
        amount = parcel_data.get('PartneredEstimate', {}).get('Amount', {})
        currency = amount.get('CurrencyCode', {}).get('value', '')
        amount_value = amount.get('Value', {}).get('value', 0.0)
        deadline_date = parcel_data.get('PartneredEstimate', {}).get('VoidDeadline', {}).get(
            'value')
        confirm_deadline_date = parcel_data.get('PartneredEstimate', {}).get('ConfirmDeadline',
                                                                             {}).get('value')
        currency_id = self.env['res.currency'].search([('name', '=', currency)])
        deadline_date = deadline_date and dateutil.parser.parse(deadline_date)
        vals = {'currency_id': currency_id and currency_id[0].id or False,
                'estimate_amount': amount_value, 'void_deadline_date': deadline_date}
        if confirm_deadline_date:
            confirm_deadline_date = dateutil.parser.parse(confirm_deadline_date)
            vals.update({'confirm_deadline_date': confirm_deadline_date})
        self.write(vals)
        return True

    @api.multi
    def setup_partnered_small_parcel_data(self, parcel_data):
        package_obj = self.env['stock.quant.package']
        package_list = []
        packages = parcel_data.get('PackageList', {}).get('member', [])
        if not isinstance(packages, list):
            package_list.append(packages)
        else:
            package_list = packages
        for package in package_list:
            tracking_number = package.get('TrackingId', {}).get('value', '')
            if not tracking_number:
                continue

            # carrier_name = package.get('CarrierName',{}).get('value','')
            package_status = package.get('PackageStatus', {}).get('value', '')
            weight_unit = package.get('Weight', {}).get('Unit', {}).get('value', '')
            weight_value = package.get('Weight', {}).get('Value', {}).get('value', '')

            package_vals = {'package_status': package_status, 'tracking_id': tracking_number}
            domain = [('partnered_small_parcel_shipment_id', '=', self.ids and self.ids[0])]

            weight_unit and package_vals.update({'weight_unit': weight_unit}), domain.append(
                ('weight_unit', '=', weight_unit))
            weight_value and package_vals.update({'weight_value': weight_value}), domain.append(
                ('weight_value', '=', weight_value))

            package_exist = package_obj.search(
                [('partnered_small_parcel_shipment_id', '=', self.ids and self.ids[0]),
                 ('tracking_no', '=', tracking_number)])
            if not package_exist:
                domain.append(('tracking_no', '=', False))
                package_exist = package_obj.search(domain, order='id')
            if package_exist:
                package_exist = package_exist[0]
                package_exist.write(package_vals)
            else:
                package_vals.update(
                    {'partnered_small_parcel_shipment_id': self.ids and self.ids[0]})
                package_obj.create(package_vals)

        return True

    @api.multi
    def setup_partnered_ltl_data(self, parcel_data):
        self.ensure_one()
        box_count = parcel_data.get('BoxCount', {}).get('value')
        freight_class = int(parcel_data.get('SellerFreightClass', {}).get('value',0))
        freight_ready_date = parcel_data.get('FreightReadyDate', {}).get('value', False)
        prev_pickup_date = parcel_data.get('PreviewPickupDate', {}).get('value', False)
        prev_delivery_date = parcel_data.get('PreviewDeliveryDate', {}).get('value', False)
        prev_freight_class = str(int(float(parcel_data.get('PreviewFreightClass', {}).get('value',0))))
        amazon_ref_id = parcel_data.get('AmazonReferenceId', {}).get('value', False)
        is_bol_available = True if parcel_data.get('IsBillOfLadingAvailable', {}).get('value',
                                                                                      '') == 'true' else False
        currency_code = parcel_data.get('AmazonCalculatedValue', {}).get('CurrencyCode', {}).get(
            'value')
        vals = {}
        if currency_code:
            currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
            currency and vals.update({'declared_value_currency_id': currency.id})
        currency_value = float(parcel_data.get('AmazonCalculatedValue', {}).get('Value', {}).get('value',0.0))
        if currency_value > 0.0:
            vals.update({'seller_declared_value': currency_value})
        freight_class and vals.update({'seller_freight_class': freight_class})
        freight_ready_date and vals.update({'freight_ready_date': freight_ready_date})
        box_count and vals.update({'box_count': box_count})
        prev_pickup_date and vals.update({'preview_pickup_date': prev_pickup_date})
        prev_delivery_date and vals.update({'preview_delivery_date': prev_delivery_date})
        prev_freight_class and vals.update({'preview_freight_class': prev_freight_class})
        amazon_ref_id and vals.update({'amazon_reference_id': amazon_ref_id})
        is_bol_available and vals.update({'is_billof_lading_available': is_bol_available})
        self.write(vals)
        return True

    @api.multi
    def get_remaining_qty(self, instance, amazon_shipment_id, odoo_shipment_rec):
        amazon_product_obj = self.env['amazon.product.ept']
        stock_move_line_obj = self.env['stock.move.line']
        attachment_ids = []
        move_obj = self.env['stock.move']
        stock_picking_obj = self.env['stock.picking']
        inbound_shipment_plan_line_obj = self.env['inbound.shipment.plan.line']

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')        

        new_picking = False
        picking = stock_picking_obj.search([('state', '=', 'done'),
                                            ('odoo_shipment_id', '=',
                                             odoo_shipment_rec and odoo_shipment_rec[0].id),
                                            ('is_fba_wh_picking', '=', True)], order="id asc",
                                           limit=1)
        if not picking:
            picking = stock_picking_obj.search([('state', '=', 'cancel'),
                                                ('odoo_shipment_id', '=',
                                                 odoo_shipment_rec and odoo_shipment_rec[0].id),
                                                ('is_fba_wh_picking', '=', True)], limit=1)

        proxy_data = instance.seller_id.get_proxy_server()
        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'check_amazon_shipment_status',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxies':proxy_data,
                  'amazon_shipment_id': amazon_shipment_id,}
        
        
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            items = response.get('items')
            datas = response.get('datas')
            
        for data in datas:
            file_name = 'inbound_shipment_report_%s.xml' % (odoo_shipment_rec.ids[0])
            if data.get('next_tone'):
                file_name = 'inbound_shipment_report_%s_%s.xml' % (odoo_shipment_rec.ids[0], str(data.get('next_token')))
            
            file_name = 'inbound_shipment_report_%s.xml' % (odoo_shipment_rec.ids[0])
            time.sleep(2)
            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'datas': base64.b64encode((data.get('origin')).encode('utf-8')),
                'datas_fname': file_name,
                'res_model': 'mail.compose.message',
            })
            if not instance.allow_process_unshipped_products:
                odoo_shipment_rec.message_post(body=_("<b> Inbound Shipment Report Downloaded </b>"),
                                               attachment_ids=attachment.ids)
            attachment_ids.append(attachment.id)              

        if not instance.allow_process_unshipped_products:
            return True
        for item in items:
            sku = item.get('SellerSKU', {}).get('value', '')
            asin = item.get('FulfillmentNetworkSKU', {}).get('value')
            shipped_qty = item.get('QuantityShipped', {}).get('value')
            received_qty = float(item.get('QuantityReceived', {}).get('value', 0.0))
            if received_qty <= 0.0:
                continue
            amazon_product = amazon_product_obj.search_amazon_product(instance.id, sku, 'AFN')
            if not amazon_product:
                amazon_product = amazon_product_obj.search(
                    [('product_asin', '=', asin), ('instance_id', '=', instance.id),
                     ('fulfillment_by', '=', 'AFN')], limit=1)
            if not amazon_product:
                odoo_shipment_rec.message_post(body=_("""Product not found in ERP ||| 
                                            FulfillmentNetworkSKU : %s
                                            SellerSKU : %s  
                                            Shipped Qty : %s
                                            Received Qty : %s                          
                                         """ % (asin, sku, shipped_qty, received_qty)))
                continue

            inbound_shipment_plan_line_id = inbound_shipment_plan_line_obj.search(
                [('odoo_shipment_id', '=', odoo_shipment_rec and odoo_shipment_rec[0].id),
                 ('amazon_product_id', '=', amazon_product.id)], limit=1)
            if inbound_shipment_plan_line_id:
                inbound_shipment_plan_line_id.received_qty = received_qty or 0.0
            else:
                vals = {
                    'amazon_product_id': amazon_product.id,
                    'quantity': shipped_qty or 0.0,
                    'odoo_shipment_id': odoo_shipment_rec and odoo_shipment_rec[0].id,
                    'fn_sku': asin,
                    'received_qty': received_qty,
                    'is_extra_line': True
                }
                inbound_shipment_plan_line_obj.create(vals)

            odoo_product = amazon_product and amazon_product.product_id or False
            done_moves = move_obj.search([('picking_id.is_fba_wh_picking', '=', True), (
            'picking_id.amazon_shipment_id', '=', amazon_shipment_id),
                                          ('product_id', '=', odoo_product.id),
                                          ('state', '=', 'done')], order="id")
            source_location_id = done_moves and done_moves[0].location_id.id
            for done_move in done_moves:
                if done_move.location_dest_id.id != source_location_id:
                    received_qty = received_qty - done_move.product_qty
                else:
                    received_qty = received_qty + done_move.product_qty
            if received_qty <= 0.0:
                continue
            if not new_picking:
                new_picking = picking.copy(
                    {'is_fba_wh_picking': True, 'move_lines': False, 'group_id': False,
                     'location_id': picking.location_id.id,
                     'location_dest_id': picking.location_dest_id.id,
                     })
                new_picking.message_post(body=_("<b> Inbound Shipment Report Downloaded </b>"),
                                         attachment_ids=attachment_ids)
            move = picking.move_lines[0]
            move.copy({'picking_id': new_picking.id,
                       'product_id': odoo_product.id,
                       'product_uom_qty': received_qty,
                       'product_uom': odoo_product.uom_id.id,
                       'procure_method': 'make_to_stock',
                       'group_id': False,
                       #                                 'procurement_id':False
                       })
        if new_picking:
            new_picking.action_confirm()
            new_picking.action_assign()
            _logger.error(new_picking)
            for move in new_picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
                move_line_remaning_qty = (move.product_uom_qty) - (
                sum(move.move_line_ids.mapped('qty_done')))
                if move_line_remaning_qty > 0.0:
                    stock_move_line_obj.create(
                        {
                            'product_id': move.product_id.id,
                            'product_uom_id': move.product_id.uom_id.id,
                            'picking_id': picking.id,
                            'qty_done': float(move_line_remaning_qty) or 0,
                            'ordered_qty': float(move_line_remaning_qty) or 0,
                            'result_package_id': False,
                            'location_id': picking.location_id.id,
                            'location_dest_id': picking.location_dest_id.id,
                            'move_id': move.id,
                        })
            new_picking.with_context(
            {'auto_processed_orders_ept': True}).action_done()  
        return True

    @api.multi
    def check_status(self):
        stock_picking_obj = self.env['stock.picking']
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        amazon_shipments = []  
        # group shipments by Instance
        instance_shipment_ids = defaultdict(list)
        for shipment in self:
            if shipment.shipment_id == False or shipment.shipment_plan_id == False:
                continue
            instance = self.get_instance(shipment)
            instance_shipment_ids[instance].append(str(shipment.shipment_id))

        for instance, shipment_ids in instance_shipment_ids.items():
            proxy_data = instance.seller_id.get_proxy_server()

            account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
            dbuuid = self.env['ir.config_parameter'].sudo(
            ).get_param('database.uuid')
    
            kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token':instance.auth_token and str(instance.auth_token) or False,
                      'app_name':'amazon_ept',
                      'account_token':account.account_token,
                      'emipro_api':'check_status',
                      'dbuuid':dbuuid,
                      'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                    instance.country_id.code,
                      'proxies': proxy_data,
                      'shipment_ids': shipment_ids,}            
            
            
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
            if response.get('reason'):
                if self._context.get('is_auto_process'):
                    job_log_vals = {
                        'message': 'Import Inbound Shipment Process',
                        'application': 'other',
                        'operation_type': 'import',
                    }
                    job = amazon_log_book_obj.create(job_log_vals)  
                    
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'amazon.inbound.shipment.ept'),
                        'log_type': 'error',
                        'skip_record': True,
                        'message': response.get('reason'),
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)    
                else:
                    raise Warning(response.get('reason'))  
            else:
                amazon_shipments = response.get('amazon_shipments')

            for ship_member in amazon_shipments:
                flag = False
                cases_required = True if ship_member.get('AreCasesRequired', {}).get('value',
                                                                                     '') == 'true' else False
                shipmentid = ship_member.get('ShipmentId', {}).get('value', '')
                shipment_status = ship_member.get('ShipmentStatus', {}).get('value', '')
                odoo_shipment_rec = self.search([('shipment_id', '=', shipmentid)])
                already_returned = False
                if shipment_status in ['RECEIVING', 'CLOSED']:
                    pickings = stock_picking_obj.search(
                        [('state', 'in', ['partially_available', 'assigned']),
                         ('odoo_shipment_id', '=', odoo_shipment_rec and odoo_shipment_rec[0].id),
                         ('is_fba_wh_picking', '=', True)])
                    if pickings:
                        pickings.check_amazon_shipment_status()
                        odoo_shipment_rec.write(
                            {'state': shipment_status, 'are_cases_required': cases_required})
                        stock_picking_obj.check_qty_difference_and_create_return_picking(shipmentid,
                                                                                         odoo_shipment_rec.id,
                                                                                         instance)
                        already_returned = True
                    else:
                        pickings = stock_picking_obj.search(
                            [('state', 'in', ['draft', 'waiting', 'confirmed']),
                             ('odoo_shipment_id', '=',
                              odoo_shipment_rec and odoo_shipment_rec[0].id),
                             ('is_fba_wh_picking', '=', True)])

                        if not pickings:
                            flag = True
                            self.get_remaining_qty(instance, shipmentid, odoo_shipment_rec)
                            odoo_shipment_rec.write(
                                {'state': shipment_status, 'are_cases_required': cases_required})
                        else:
                            raise Warning("""Shipment Status is not update due to picking not found for processing  |||
                                            Amazon status : %s
                                            ERP status  : %s
                                        """ % (shipment_status, odoo_shipment_rec.state))
                    if shipment_status == 'CLOSED':
                        if not flag:
                            self.get_remaining_qty(instance, shipmentid, odoo_shipment_rec)

                        if not odoo_shipment_rec.closed_date:
                            odoo_shipment_rec.write({'closed_date': time.strftime("%Y-%m-%d")})
                        pickings = stock_picking_obj.search(
                            [('state', 'in', ['partially_available', 'assigned']),
                             ('odoo_shipment_id', '=',
                              odoo_shipment_rec and odoo_shipment_rec[0].id),
                             ('is_fba_wh_picking', '=', True)])
                        pickings and pickings.action_cancel()
                        if not already_returned:
                            stock_picking_obj.check_qty_difference_and_create_return_picking(
                                shipmentid, odoo_shipment_rec.id, instance)
                else:
                    odoo_shipment_rec.write({'state': shipment_status})
        return True

    @api.model
    def create_or_update_inbound_shipment(self, ship_plan, shipment, job=False):
        amazon_log_obj = self.env['amazon.process.log.book']
        amazon_transaction_obj = self.env['amazon.transaction.log']

        add_id = self.create_or_update_address(shipment.get('ShipToAddress', {}))
        fulfill_center_id = shipment.get('DestinationFulfillmentCenterId', {}).get('value', '')
        label_prep_type = shipment.get('LabelPrepType', {}).get('value', '')
        shipment_id = shipment.get('ShipmentId', {}).get('value', False)
        # Here We are not taking shipment id as domain because amazon create each time new shipment id & we merge with existing shipment_id in same plan
        domain = [('shipment_id','=',shipment_id),('shipment_plan_id', '=', ship_plan.id)]

        odoo_shipment = self.search(domain)
        create_or_update = ''
        if odoo_shipment:
            create_or_update = 'update'
        else:
            try:
                sequence = self.env.ref('amazon_ept.seq_inbound_shipments')
                if sequence:
                    name = sequence.next_by_id()
                else:
                    name = '/'
            except:
                name = '/'
            shipment_vals = {
                'name': name,
                'shipment_plan_id': ship_plan.id,
                'fulfill_center_id': fulfill_center_id,
                'label_prep_type': label_prep_type,
                'address_id': add_id,
                'shipment_id': shipment_id,
                'state': 'WORKING',
                'intended_boxcontents_source': ship_plan.intended_boxcontents_source
            }
            if ship_plan.shipping_type:
                shipment_vals.update({'is_partnered': ship_plan.is_partnered,
                                      'shipping_type': ship_plan.shipping_type})
            odoo_shipment = self.create(shipment_vals)
            create_or_update = 'create'
        items = []
        if not isinstance(shipment.get('Items', {}).get('member', []), list):
            items.append(shipment.get('Items', {}).get('member', []))
        else:
            items = shipment.get('Items', {}).get('member', [])

        is_are_cases_required = ship_plan and ship_plan.is_are_cases_required or False
        sku_qty_dict, sku_prep_details_dict = self.env[
            'inbound.shipment.plan.line'].create_update_plan_line(odoo_shipment, items)

        instance = ship_plan.instance_id
        address = ship_plan.ship_from_address_id
        name, add1, add2, city, postcode = address.name, address.street or '', address.street2 or '', address.city or '', address.zip or ''
        country = address.country_id and address.country_id.code or ''
        state = address.state_id and address.state_id.code or ''
        # sku_qty_dict = dict(map(lambda x:(x.get('SellerSKU',{}).get('value',''),str(x.get('Quantity',{}).get('value',0.0))),items))
        proxy_data = instance.seller_id.get_proxy_server()
        
        result = {}
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        label_prep_type = 'SELLER_LABEL' if odoo_shipment.label_prep_type == 'NO_LABEL' else odoo_shipment.label_prep_type
        if create_or_update == 'update':
            kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token':instance.auth_token and str(instance.auth_token) or False,
                      'app_name':'amazon_ept',
                      'account_token':account.account_token,
                      'emipro_api':'update_shipment_in_amazon',
                      'dbuuid':dbuuid,
                      'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                    instance.country_id.code,
                      'proxies':proxy_data,
                      'shipment_name': odoo_shipment.name,
                      'shipment_id':odoo_shipment.shipment_id,
                      'fulfill_center_id': odoo_shipment.fulfill_center_id,
                      'address_name': name,
                      'add1': add1,
                      'add2' : add2,
                      'city': city,
                      'state' : state,
                      'postcode': postcode,
                      'country': country,
                      'labelpreppreference': label_prep_type,
                      'inbound_box_content_status': odoo_shipment.intended_boxcontents_source,
                      'sku_qty_dict': sku_qty_dict,
                      'sku_prep_details_dict':sku_prep_details_dict,
                      'is_are_cases_required': is_are_cases_required,
                      'shipment_status':'WORKING'
                      }
            
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                error_value = response.get('reason')
                if not job:
                    job = amazon_log_obj.create({'application': 'other',
                                                 'operation_type': 'export',
                                                 'instance_id': instance.id,
                                                 'skip_process': True
                                                 })
                amazon_transaction_obj.create({'log_type': 'not_found',
                                               'action_type': 'terminate_process_with_log',
                                               'operation_type': 'export',
                                               'message': error_value,
                                               'model_id': amazon_transaction_obj.get_model_id(
                                                   'inbound.shipment.plan.ept'),
                                               'res_id': ship_plan.id,
                                               'job_id': job.id
                                               })
                return False, job            
        elif create_or_update == 'create':
            kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token':instance.auth_token and str(instance.auth_token) or False,
                      'app_name':'amazon_ept',
                      'account_token':account.account_token,
                      'emipro_api':'create_shipment_in_amazon',
                      'dbuuid':dbuuid,
                      'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                    instance.country_id.code,
                      'proxies':proxy_data,
                      'shipment_name': odoo_shipment.name,
                      'shipment_id':odoo_shipment.shipment_id,
                      'fulfill_center_id': odoo_shipment.fulfill_center_id,
                      'address_name': name,
                      'add1': add1,
                      'add2' : add2,
                      'city': city,
                      'state' : state,
                      'postcode': postcode,
                      'country': country,
                      'labelpreppreference': label_prep_type,
                      'inbound_box_content_status': odoo_shipment.intended_boxcontents_source,
                      'sku_qty_dict': sku_qty_dict,
                      'sku_prep_details_dict':sku_prep_details_dict,
                      'is_are_cases_required': is_are_cases_required,
                      'shipment_status':'WORKING'
                      }
            
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                error_value = response.get('reason')
                if not job:
                    job = amazon_log_obj.create({'application': 'other',
                                                 'operation_type': 'export',
                                                 'instance_id': instance.id,
                                                 'skip_process': True
                                                 })
                amazon_transaction_obj.create({'log_type': 'not_found',
                                               'action_type': 'terminate_process_with_log',
                                               'operation_type': 'export',
                                               'message': error_value,
                                               'model_id': amazon_transaction_obj.get_model_id(
                                                   'inbound.shipment.plan.ept'),
                                               'res_id': ship_plan.id,
                                               'job_id': job.id
                                               })
                return False, job

        shipment_id = result and result.get('ShipmentId', {}).get('value', '') or False
        vals = {'label_prep_type': label_prep_type}
        if shipment_id:
            vals.update({'shipment_id': shipment_id})
        odoo_shipment.write(vals)
        return odoo_shipment, job

    """Create or Update partner based on return shipping information by Amazon."""

    @api.multi
    def create_or_update_address(self, address):
        domain = []
        partner_obj = self.env['res.partner']
        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        state_id = False

        country = country_obj.search(
            [('code', '=', address.get('CountryCode', {}).get('value', ''))])
        state = address.get('StateOrProvinceCode', {}).get('value', False)

        if state:
            result_state = state_obj.search([('code', '=', state)])
            if not result_state:
                state = state_obj.create({'country_id': country.id, 'name': state, 'code': state})
                state_id = state and state.id or False
            else:
                state_id = result_state[0].id

        name = address.get('Name', {}).get('value', False)
        street = address.get('AddressLine1', {}).get('value', False)
        street2 = address.get('AddressLine2', {}).get('value', False)
        postalcode = address.get('PostalCode', {}).get('value', False)
        city = address.get('City', {}).get('value', False)

        name and domain.append(('name', '=', name))
        street and domain.append(('street', '=', street))
        street2 and domain.append(('street2', '=', street2))
        city and domain.append(('city', '=', city))
        postalcode and domain.append(('zip', '=', postalcode))
        state_id and domain.append(('state_id', '=', state_id))
        country and domain.append(('country_id', '=', country.id))

        exist_partner = partner_obj.search(domain)
        if exist_partner:
            return exist_partner.id
        else:
            partnervals = {
                'name': name, 'opt_out': True, 'is_company': False, 'customer': True,
                'street': street, 'street2': street2,
                'city': city, 'country_id': country.id, 'zip': postalcode, 'state_id': state_id,
            }
            partner = partner_obj.create(partnervals)

            return partner.id

    @api.multi
    def get_unique_package_labels(self):
        view = self.env.ref(
            'amazon_ept.amazon_inbound_shipment_print_unique_label_wizard_form_view',
            False)
        if not self.is_partnered:
            return True
        return {
            'name': _('Labels'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amazon.shipment.label.wizard',
            'view_id': view.id,
            'nodestroy': True,
            'target': 'new',
            'context': self._context,
        }

    @api.multi
    def get_package_labels(self):
        ctx = self._context.copy() or {}
        if ctx.get('label_type', '') == 'delivery':
            view = self.env.ref(
                'amazon_ept.amazon_inbound_shipment_print_delivery_label_wizard_form_view',
                False)
        else:
            view = self.env.ref(
                'amazon_ept.amazon_inbound_shipment_print_shipment_label_wizard_form_view',
                False)
            if self.shipping_type == 'sp' and self.is_partnered == True and not self.partnered_small_parcel_ids:
                raise Warning("Box dimension informations are missing!!! ")
            if self.is_partnered and self.shipping_type == 'ltl':
                ctx.update({'default_number_of_box': self.box_count})
            elif self.is_partnered and self.partnered_small_parcel_ids:
                ctx.update({'default_number_of_box': len(self.partnered_small_parcel_ids.ids),
                            'box_readonly': True})

        ctx.update({'shipping_type': self.shipping_type, })
        return {
            'name': _('Labels'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amazon.shipment.label.wizard',
            'view_id': view.id,
            'nodestroy': True,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def get_bill_of_lading(self):
        self.ensure_one()
        instance = self.get_instance(self)
        proxy_data = instance.seller_id.get_proxy_server()

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        
        kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token':instance.auth_token and str(instance.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'get_bill_of_lading',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxy_data': proxy_data,
                  'shipment_id': self.shipment_id }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            result = response.get('result')
        bol_doc = result.get('TransportDocument', {}).get('PdfDocument', {}).get('value', '')
        if bol_doc:
            bol_doc = base64.b64decode(bol_doc)
            bol_zip = open('/tmp/bill_of_landing.zip', 'wb')
            bol_zip.write(bol_doc)
            bol_zip.close()
            zip_file = open('/tmp/bill_of_landing.zip', 'rb')
            z = zipfile.ZipFile(zip_file)
            for name in z.namelist():
                path = z.extract(name, '/tmp/')
                fh = open(path, 'rb')
                datas = base64.b64encode(fh.read())
                fh.close()
                self.env['ir.attachment'].create({
                    'name': name,
                    'datas': datas,
                    'datas_fname': name,
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary'
                })
                # we don't need the file anymore, try to delete it
                try:
                    os.remove(path)
                except Exception as e:
                    pass
            zip_file.close()
            try:
                os.remove('/tmp/bill_of_landing.zip')
            except Exception as  e:
                pass
        return True

    @api.multi
    def create_pickings_ept(self):
        """
        Use: Create New Picking for Shipment
        Params: {}
        Return: {}
        ----------------------------------------------
        Added by: Dhaval Sanghani @Emipro Technologies
        Added on: 02-May-2019
        """
        self.ensure_one()
        inbound_shipment_plan_obj = self.env['inbound.shipment.plan.ept']
        inbound_shipment_plan_obj.create_procurements(self)

    @api.multi
    def open_import_inbound_shipment_report_wizard(self):
        import_inbound_shipment_view = self.env.ref(
            'amazon_ept.import_amazon_inbound_shipment_report_form_view')
        return {
            'name': 'Import Amazon Inbound Shipment Report',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'amazon.inbound.shipment.report.wizard',
            'type': 'ir.actions.act_window',
            'view_id': import_inbound_shipment_view.id,
            'target': 'new'
        }


    @api.multi
    def update_inbound_shipment_qty(self):
        """
        Use: Update Shipment Qty in Amazon
        Params: {}
        Return: {}
        ----------------------------------------------
        Added by: Dhaval Sanghani @Emipro Technologies
        Added on: 02-May-2019
        """     
        pickings = self.mapped('picking_ids').\
                                    filtered(lambda picking: picking.state in ('done'))
        if pickings:
            raise Warning("You can not Update Shipment QTY whose Pickings are in Done State")

        for shipment in self:
            ship_plan = shipment.shipment_plan_id

            if not ship_plan or not shipment.fulfill_center_id:
                raise Warning('You must have to first create Inbound Shipment Plan.')

            instance = ship_plan.instance_id
            address = ship_plan.ship_from_address_id
            name, add1, add2, city, postcode = address.name, address.street or '', \
                                               address.street2 or '', address.city or '', \
                                               address.zip or ''
            country = address.country_id and address.country_id.code or ''
            state = address.state_id and address.state_id.code or ''
            shipment_status = shipment.state

            proxy_data = instance.seller_id.get_proxy_server()
            account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
            dbuuid = self.env['ir.config_parameter'].sudo(
            ).get_param('database.uuid')               

            for x in range(0, len(shipment.odoo_shipment_line_ids), 20):
                shipment_lines = shipment.odoo_shipment_line_ids[x:x + 20]
                sku_qty_dict = {}
                for line in shipment_lines:
                    amazon_product = line.amazon_product_id
                    if not amazon_product:
                        raise Warning("Amazon Product is not available")

                    sku_qty_dict.update({str(
                        line and line.seller_sku or amazon_product.seller_sku): str(
                        int(line.quantity))})               
                kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                          'auth_token':instance.auth_token and str(instance.auth_token) or False,
                          'app_name':'amazon_ept',
                          'account_token':account.account_token,
                          'emipro_api':'update_shipment_in_amazon',
                          'dbuuid':dbuuid,
                          'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                        instance.country_id.code,
                          'proxies':proxy_data,
                          'shipment_name': shipment.name,
                          'shipment_id':shipment.shipment_id,
                          'fulfill_center_id': shipment.fulfill_center_id,
                          'address_name': name,
                          'add1': add1,
                          'add2' : add2,
                          'city': city,
                          'state' : state,
                          'postcode': postcode,
                          'country': country,
                          'labelpreppreference': shipment.label_prep_type,
                          'shipment_status': shipment_status,
                          'inbound_box_content_status': shipment.intended_boxcontents_source,
                          'sku_qty_dict': sku_qty_dict,
                          }
                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):
                    raise Warning(response.get('reason'))
            shipment.picking_ids.action_cancel()
            shipment.create_pickings_ept()

        return True
