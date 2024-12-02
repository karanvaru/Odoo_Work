# Copyright (c) 2017 Emipro Technologies Pvt Ltd (www.emiprotechnologies.com). All rights reserved.
import binascii
import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _
from odoo.addons.fedex_shipping_ept.fedex.base_service import FedexError, FedexFailure
from odoo.addons.fedex_shipping_ept.fedex.tools.conversion import basic_sobject_to_dict
from odoo.addons.fedex_shipping_ept.fedex.services.rate_service import FedexRateServiceRequest
from odoo.addons.fedex_shipping_ept.fedex.services.ship_service import FedexDeleteShipmentRequest
from odoo.addons.fedex_shipping_ept.fedex.services.ship_service import FedexProcessShipmentRequest
from odoo.addons.fedex_shipping_ept.fedex.services.upload_document_service import \
    FedexProcessUploadDocumentRequest
from odoo.addons.fedex_shipping_ept.fedex.services.address_validation_service import \
    FedexAddressValidationRequest
import logging

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('fedex_ept', "FedEx")])
    fedex_service_type = fields.Selection(
            [('EUROPE_FIRST_INTERNATIONAL_PRIORITY', 'Europe First International Priority'),
             # When Call the service given the error "Customer not eligible for service".
             ('SMART_POST', 'Smart Post'),
             # When Call the service given the error "Customer not eligible for service"
             ('FEDEX_GROUND', 'Fedex Ground'),
             # When Call the service given the error "Customer not eligible for service"

             ('FEDEX_DISTANCE_DEFERRED', 'Fedex Distance Deferred'),
             # for domestic UK pickup  Error : Customer is eligible.
             ('FEDEX_NEXT_DAY_AFTERNOON', 'Fedex Next Day Afternoon'),  # for domestic UK pickup
             ('FEDEX_NEXT_DAY_EARLY_MORNING', 'Fedex Next Day Early Morning'),
             # for domestic UK pickup
             ('FEDEX_NEXT_DAY_END_OF_DAY', 'Fedex Next Day End of Day'),  # for domestic UK pickup
             ('FEDEX_NEXT_DAY_FREIGHT', 'Fedex Next Day Freight'),  # for domestic UK pickup
             ('FEDEX_NEXT_DAY_MID_MORNING', 'Fedex Next Day Mid Morning'),  # for domestic UK pickup

             ('GROUND_HOME_DELIVERY', 'Ground Home Delivery'),
             # To Address Use: 33122 Florida Doral US. From Add use: 33122 Florida Doral US and Package type box is your_packaging.
             ('INTERNATIONAL_ECONOMY', 'International Economy'),
             # To Address Use: 33122 Florida Doral US. From Add use: 12277 Germany Berlin Penna.
             ('INTERNATIONAL_FIRST', 'International First'),
             # To Address Use: 33122 Florida Doral US. From Add use: 12277 Germany Berlin Penna.
             ('INTERNATIONAL_PRIORITY', 'International Priority'),
             # To Address Use: 33122 Florida Doral US. From Add use: 73377 "Le Bourget du Lac" France

             ('FIRST_OVERNIGHT', 'First Overnight'),  # for US
             ('PRIORITY_OVERNIGHT', 'Priority Overnight'),  # for US
             ('FEDEX_2_DAY', 'Fedex 2 Day'),  # for US Use: 33122 Florida Doral
             ('FEDEX_2_DAY_AM', 'Fedex 2 Day AM'),  # for US Use: 33122 Florida Doral
             ('FEDEX_EXPRESS_SAVER', 'Fedex Express Saver'),  # for US Use: 33122 Florida Doral
             ('STANDARD_OVERNIGHT', 'Standard Overnight')  # for US Use: 33122 Florida Doral
             # ('SAME_DAY_CITY', 'Same Day City'),  # for US
             # ('SAME_DAY', 'Same Day'),  # for US Test but get response always service not allowed.
             # ('INTERNATIONAL_PRIORITY_DISTRIBUTION','International priority distribution'),
             # ('FEDEX_1_DAY_FREIGHT', 'Fedex 1 Day Freight'), not supported in app
             # ('FEDEX_2_DAY_FREIGHT', 'Fedex 2 Day Freight'), not supported in app
             # ('FEDEX_3_DAY_FREIGHT', 'Fedex 3 Day Freight'), not supported in app
             # ('FEDEX_FIRST_FREIGHT', 'Fedex First Freight'), # for US j
             # ('FEDEX_FREIGHT_ECONOMY', 'Fedex Freight Economy'), # for US j
             # ('INTERNATIONAL_ECONOMY_FREIGHT', 'International Economy Freight'), j
             # ('INTERNATIONAL_PRIORITY_FREIGHT', 'International Priority Freight'), j
             ], string="Service Type", help="Shipping Services those are accepted by Fedex")

    fedex_droppoff_type = fields.Selection([('BUSINESS_SERVICE_CENTER', 'Business Service Center'),
                                            ('DROP_BOX', 'Drop Box'),
                                            ('REGULAR_PICKUP', 'Regular Pickup'),
                                            ('REQUEST_COURIER', 'Request Courier'),
                                            ('STATION', 'Station')],
                                           string="Drop-off Type",
                                           default='REGULAR_PICKUP',
                                           help="Identifies the method by which the package is to be tendered to FedEx.")
    fedex_default_product_packaging_id = fields.Many2one('product.packaging',
                                                         string="Default Package Type")
    fedex_weight_uom = fields.Selection([('LB', 'LB'),
                                         ('KG', 'KG')], default='LB', string="Weight UoM",
                                        help="Weight UoM of the Shipment")
    fedex_shipping_label_stock_type = fields.Selection([
        # These values display a thermal format label
        ('PAPER_4X6', 'Paper 4X6 '),
        ('PAPER_4X8', 'Paper 4X8'),
        ('PAPER_4X9', 'Paper 4X9'),

        # These values display a plain paper format shipping label
        ('PAPER_7X4.75', 'Paper 7X4.75'),
        ('PAPER_8.5X11_BOTTOM_HALF_LABEL', 'Paper 8.5X11 Bottom Half Label'),
        ('PAPER_8.5X11_TOP_HALF_LABEL', 'Paper 8.5X11 Top Half Label'),
        ('PAPER_LETTER', 'Paper Letter'),

        # These values for Stock Type label
        ('STOCK_4X6', 'Stock 4X6'),
        ('STOCK_4X6.75_LEADING_DOC_TAB', 'Stock 4X6.75 Leading Doc Tab'),
        ('STOCK_4X6.75_TRAILING_DOC_TAB', 'Stock 4X6.75 Trailing Doc Tab'),
        ('STOCK_4X8', 'Stock 4X8'),
        ('STOCK_4X9_LEADING_DOC_TAB', 'Stock 4X9 Leading Doc Tab'),
        ('STOCK_4X9_TRAILING_DOC_TAB', 'Stock 4X9 Trailing Doc Tab')], string="Label Stock Type",
            help="Specifies the type of paper (stock) on which a document will be printed.")
    fedex_shipping_label_file_type = fields.Selection([('DPL', 'DPL'),
                                                       ('EPL2', 'EPL2'),
                                                       ('PDF', 'PDF'),
                                                       ('PNG', 'PNG'),
                                                       ('ZPLII', 'ZPLII')],
                                                      string="Label File Type")
    fedex_onerate = fields.Boolean("Want To Use FedEx OneRate Service?", default=False)
    is_commercial_invoce = fields.Boolean(string="Generate Commerical invoice",
                                          help="Generate Commercial Invoice for international shipment, You Must set single package for the generate commerical invoice",
                                          default=False)

    @api.onchange('fedex_default_product_packaging_id', 'fedex_service_type')
    def fedex_onchange_service_and_package(self):
        self.fedex_onerate = False

    @api.model
    def do_address_validation(self, address):
        """
        Call to get the validated address from Fedex or
        Classification : Can be used to determine the address classification to figure out if Residential fee should apply.
                        values are return in classification : MIXED, RESIDENTIAL, UNKNOWN, BUSINESS
        @param address: recordset of Partner
        @return: returns a dict containing Address result
        @note: To use address validation services, client need to request fedex to enable this service for his account.
               By default, The service is disable and you will receive authentication failed.
        @author: Jignesh Jarsaniya on dated : 21-April-2017
        """
        try:
            FedexConfig = self.shipping_instance_id.get_fedex_api_object()
            avs_request = FedexAddressValidationRequest(FedexConfig)
            address_to_validate = avs_request.create_wsdl_object_of_type('AddressToValidate')
            street_lines = []
            if address.street:
                street_lines.append(address.street)
            if address.street2:
                street_lines.append(address.street2)
            address_to_validate.Address.StreetLines = street_lines
            address_to_validate.Address.City = address.city
            if address.state_id:
                address_to_validate.Address.StateOrProvinceCode = address.state_id.code
            address_to_validate.Address.PostalCode = address.zip
            if address.country_id:
                address_to_validate.Address.CountryCode = address.country_id.code
            avs_request.add_address(address_to_validate)
            avs_request.send_request()
            response = basic_sobject_to_dict(avs_request.response)
            if response.get('AddressResults'):
                return response['AddressResults'][0]  # Classification
        except FedexError as ERROR:
            raise ValidationError(ERROR.value)
        except FedexFailure as ERROR:
            raise ValidationError(ERROR.value)
        except Exception as e:
            raise ValidationError(e)

    @api.multi
    def prepare_shipment_request(self, instance, request_obj, shipper, recipient, package_type):
        """
        Preparation of Fedex Shipping Request
        @param instance: recordset of Shipping Instance
        @param request_obj: Object of Fedex Request
        @param shipper: recordset of Partner
        @param recipient: recordset of Partner
        @return: Updated Fedex request object
        @author: Jignesh Jarsaniya on dated : 22-April-2017
        """
        self.ensure_one()
        # If you wish to have transit data returned with your request you
        request_obj.ReturnTransitAndCommit = True
        request_obj.RequestedShipment.ShipTimestamp = datetime.datetime.now().replace(
            microsecond=0).isoformat()
        request_obj.RequestedShipment.DropoffType = self.fedex_droppoff_type
        request_obj.RequestedShipment.ServiceType = self.fedex_service_type
        request_obj.RequestedShipment.PackagingType = package_type

        # Shipper's address
        residential = True
        if instance.use_address_validation_service:
            validated_address = self.do_address_validation(shipper)
            residential = validated_address.get('Classification') != 'BUSINESS'

        # request_obj.RequestedShipment.FreightShipmentDetail.PrintedReferences = "BILL_OF_LADING"
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightAccountNumber = self.shipping_instance_id.fedex_account_number
        #
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Contact.PhoneNumber = shipper.phone
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Contact.PersonName = shipper.name
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.StreetLines = shipper.street
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.City = shipper.city
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.PostalCode = shipper.zip
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.CountryCode = shipper.country_id.code
        # request_obj.RequestedShipment.FreightShipmentDetail.FedExFreightBillingContactAndAddress.Address.StateOrProvinceCode = shipper.state_id.code

        request_obj.RequestedShipment.Shipper.Contact.PersonName = shipper.name if not shipper.is_company else ''
        request_obj.RequestedShipment.Shipper.Contact.CompanyName = shipper.name if shipper.is_company else ''
        request_obj.RequestedShipment.Shipper.Contact.PhoneNumber = shipper.phone
        request_obj.RequestedShipment.Shipper.Address.StreetLines = shipper.street and shipper.street2 and [
            shipper.street, shipper.street2] or [shipper.street]
        request_obj.RequestedShipment.Shipper.Address.City = shipper.city or None
        request_obj.RequestedShipment.Shipper.Address.StateOrProvinceCode = shipper.state_id and shipper.state_id.code or None
        request_obj.RequestedShipment.Shipper.Address.PostalCode = shipper.zip
        request_obj.RequestedShipment.Shipper.Address.CountryCode = shipper.country_id.code
        request_obj.RequestedShipment.Shipper.Address.Residential = residential

        # Recipient address
        residential = False
        if instance.use_address_validation_service:
            validated_address = self.do_address_validation(recipient)
            residential = validated_address.get('Classification') != 'BUSINESS'

        request_obj.RequestedShipment.Recipient.Contact.PersonName = recipient.name if not recipient.is_company else ''
        request_obj.RequestedShipment.Recipient.Contact.CompanyName = recipient.name if recipient.is_company else ''
        request_obj.RequestedShipment.Recipient.Contact.PhoneNumber = recipient.mobile or recipient.phone
        request_obj.RequestedShipment.Recipient.Address.StreetLines = recipient.street and recipient.street2 and [
            recipient.street, recipient.street2] or [recipient.street]
        request_obj.RequestedShipment.Recipient.Address.City = recipient.city
        request_obj.RequestedShipment.Recipient.Address.StateOrProvinceCode = recipient.state_id and recipient.state_id.code or ''
        request_obj.RequestedShipment.Recipient.Address.PostalCode = recipient.zip
        request_obj.RequestedShipment.Recipient.Address.CountryCode = recipient.country_id.code
        request_obj.RequestedShipment.Recipient.Address.Residential = residential
        # include estimated duties and taxes in rate quote, can be ALL or NONE
        request_obj.RequestedShipment.EdtRequestType = 'NONE'

        request_obj.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = instance.fedex_account_number
        request_obj.RequestedShipment.ShippingChargesPayment.PaymentType = "SENDER"

        # request_obj.RequestedShipment.SpecialServicesRequested.SpecialServicesTypes='RETURN_SHIPMENT'
        # request_obj.RequestedShipment.SpecialServicesRequested.ReturnShipmentDetail.ReturnType='PRINT_RETURN_LABEL'
        return request_obj

    @api.model
    def manage_fedex_packages(self, rate_request, weight, number=1):
        package_weight = rate_request.create_wsdl_object_of_type('Weight')
        package_weight.Value = weight
        package_weight.Units = self.fedex_weight_uom
        package = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
        package.Weight = package_weight
        if self.fedex_default_product_packaging_id.shipper_package_code:
            package.Dimensions.Length = self.fedex_default_product_packaging_id.length
            package.Dimensions.Width = self.fedex_default_product_packaging_id.width
            package.Dimensions.Height = self.fedex_default_product_packaging_id.height
            package.Dimensions.Units = 'IN' if self.fedex_weight_uom == 'LB' else 'CM'
        package.PhysicalPackaging = 'BOX'
        package.GroupPackageCount = 1
        if number:
            package.SequenceNumber = number
        return package

    @api.model
    def add_fedex_package(self, picking, ship_request, weight, package_count, number=1,
                          master_tracking_id=False, package=False):
        package_weight = ship_request.create_wsdl_object_of_type('Weight')
        package_weight.Value = weight
        package_weight.Units = self.fedex_weight_uom
        package_request = ship_request.create_wsdl_object_of_type('RequestedPackageLineItem')
        package_request.Weight = package_weight
        if package:
            package_request.Dimensions.Length = package[0].packaging_id.length
            package_request.Dimensions.Width = package[0].packaging_id.width
            package_request.Dimensions.Height = package[0].packaging_id.height
            package_request.Dimensions.Units = 'IN' if self.fedex_weight_uom == 'LB' else 'CM'
        elif self.fedex_default_product_packaging_id.shipper_package_code:
            package_request.Dimensions.Length = self.fedex_default_product_packaging_id.length
            package_request.Dimensions.Width = self.fedex_default_product_packaging_id.width
            package_request.Dimensions.Height = self.fedex_default_product_packaging_id.height
            package_request.Dimensions.Units = 'IN' if self.fedex_weight_uom == 'LB' else 'CM'
        package_request.PhysicalPackaging = 'BOX'
        if number:
            package_request.SequenceNumber = number


        ship_request.RequestedShipment.RequestedPackageLineItems = package_request
        ship_request.RequestedShipment.TotalWeight.Value = weight
        ship_request.RequestedShipment.PackageCount = package_count
        if master_tracking_id:
            ship_request.RequestedShipment.MasterTrackingId.TrackingIdType = 'FEDEX'
            ship_request.RequestedShipment.MasterTrackingId.TrackingNumber = master_tracking_id
        # Hemangi================================================================================
        if package and self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_FIRST',
                                                   'INTERNATIONAL_PRIORITY'] or (
                        picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN'):
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            order_currency = picking.sale_id.currency_id or picking.company_id.currency_id
            commodity_country_of_manufacture = picking.picking_type_id.warehouse_id.partner_id.country_id.code
            commodity_weight_units = self.fedex_weight_uom
            total_commodities_amount = 0.0
            for product_list in picking.move_line_ids:
                if product_list.result_package_id == package:
                    total_commodities_amount += (
                    product_list.qty_done * product_list.product_id.list_price)
                    Commodity = ship_request.create_wsdl_object_of_type('Commodity')
                    Commodity.UnitPrice.Currency = order_currency.name
                    Commodity.UnitPrice.Amount = product_list.product_id.list_price
                    Commodity.NumberOfPieces = '1'
                    Commodity.CountryOfManufacture = commodity_country_of_manufacture
                    Commodity.Weight.Units = commodity_weight_units
                    Commodity.Weight.Value = (
                    product_list.qty_done * product_list.product_id.weight)
                    Commodity.Description = product_list.product_id.name
                    Commodity.Quantity = product_list.qty_done
                    Commodity.QuantityUnits = 'EA'
                    Commodity.CustomsValue.Amount = (
                    product_list.qty_done * product_list.product_id.list_price)
                    Commodity.CustomsValue.Currency = order_currency.name
                    ship_request.RequestedShipment.CustomsClearanceDetail.Commodities.append(
                        Commodity)

            # By: Nimesh , For Generate Commercial invoice for the international shipment
            # package_count <= 1 and
            if package_count <= 1 and self.is_commercial_invoce:
                commercial_invoice_detail = ship_request.create_wsdl_object_of_type(
                        'CommercialInvoiceDetail')
                commercial_invoice_detail.Format.ImageType.value = 'PDF'
                commercial_invoice_detail.Format.StockType.value = 'PAPER_LETTER'
                ship_request.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail = commercial_invoice_detail
                ship_request.RequestedShipment.ShippingDocumentSpecification.ShippingDocumentTypes = 'COMMERCIAL_INVOICE'
            ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = 'SENDER'
            ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.AccountNumber = self.shipping_instance_id.fedex_account_number
            ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Address.CountryCode = picking.picking_type_id.warehouse_id.partner_id.country_id.code
            ship_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = total_commodities_amount
            ship_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = picking.sale_id.currency_id.name or picking.company_id.currency_id.name
            if picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN':
                ship_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose.value = "SOLD"
        return ship_request

    def fedex_ept_rate_shipment(self, orders):
        res = []
        shipping_charge = 0.0
        for order in orders:

            # check the address validation
            check_value = self.check_required_value_to_ship(order)
            if check_value:
                return {'success':False, 'price':0.0, 'error_message':check_value,
                        'warning_message':False}

            # Shipper and Recipient Address
            shipper_address = order.warehouse_id.partner_id
            recipient_address = order.partner_shipping_id
            shipping_instance_id = self.shipping_instance_id

            total_weight = sum([(line.product_id.weight * line.product_uom_qty) for line in
                                order.order_line]) or 0.0
            total_weight = self.convert_weight(
                    order.company_id and order.company_id.weight_unit_of_measurement_id,
                    self.weight_uom_id, total_weight)
            max_weight = self.convert_weight(
                    order.company_id and order.company_id.weight_unit_of_measurement_id,
                    self.weight_uom_id, self.fedex_default_product_packaging_id.max_weight)
            # total_weight = self.convert_weight(self.fedex_weight_uom, total_weight)
            # max_weight = self.convert_weight(self.fedex_weight_uom, self.fedex_default_product_packaging_id.max_weight)

            try:
                # This is the object that will be handling our request.
                FedexConfig = self.shipping_instance_id.get_fedex_api_object(self.prod_environment)
                rate_request = FedexRateServiceRequest(FedexConfig)
                package_type = self.fedex_default_product_packaging_id.shipper_package_code
                total_amount = order.amount_total
                currency = order.company_id.currency_id.name
                rate_request.RequestedShipment.TotalWeight.Units = self.fedex_weight_uom
                rate_request = self.prepare_shipment_request(shipping_instance_id, rate_request,
                                                             shipper_address, recipient_address,
                                                             package_type)
                rate_request.RequestedShipment.PreferredCurrency = order.currency_id.name
                if max_weight and total_weight > max_weight:
                    total_package = int(total_weight / max_weight)
                    last_package_weight = total_weight % max_weight

                    for index in range(1, total_package + 1):
                        package = self.manage_fedex_packages(rate_request, max_weight, index)
                        rate_request.add_package(package)
                    if last_package_weight:
                        index = total_package + 1
                        package = self.manage_fedex_packages(rate_request, last_package_weight,
                                                             index)
                        rate_request.add_package(package)
                        #                         rate_request.RequestedShipment.RequestedPackageLineItems.append(package)
                else:
                    total_package = 1
                    package = self.manage_fedex_packages(rate_request, total_weight)
                    rate_request.add_package(package)
                # rate_request.RequestedShipment.TotalWeight.Value = total_weight
                #                 rate_request.RequestedShipment.PackageCount = total_package
                # Hemangi - For One rate service.
                if self.fedex_onerate:
                    rate_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = [
                        'FEDEX_ONE_RATE']
                if shipper_address.company_id.country_id.code == "IN":
                    rate_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor \
                        .ResponsibleParty.AccountNumber = shipping_instance_id.fedex_account_number
                    rate_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType.value = "SENDER"
                    rate_request.RequestedShipment.CustomsClearanceDetail.DocumentContent.value = "NON_DOCUMENTS"
                    rate_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = currency
                    rate_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = total_amount
                    rate_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose.value = "SOLD"
                rate_request.send_request()
            except FedexError as ERROR:
                return {'success':False, 'price':0.0, 'error_message':ERROR.value,
                        'warning_message':False}
                # raise ValidationError(ERROR.value)
            except FedexFailure as ERROR:
                return {'success':False, 'price':0.0, 'error_message':ERROR.value,
                        'warning_message':False}
                # raise ValidationError(ERROR.value)
            except Exception as e:
                return {'success':False, 'price':0.0, 'error_message':e, 'warning_message':False}
                # raise ValidationError(e)
            for shipping_service in rate_request.response.RateReplyDetails:
                for rate_info in shipping_service.RatedShipmentDetails:
                    shipping_charge = float(rate_info.ShipmentRateDetail.TotalNetFedExCharge.Amount)
                    shipping_charge_currency = rate_info.ShipmentRateDetail.TotalNetFedExCharge.Currency
                    if order.currency_id.name != rate_info.ShipmentRateDetail.TotalNetFedExCharge.Currency:
                        rate_currency = self.env['res.currency'].search(
                                [('name', '=', shipping_charge_currency)], limit=1)
                        if rate_currency:
                            shipping_charge = rate_currency.compute(float(shipping_charge),
                                                                    order.currency_id)
        return {'success':True,
                'price':float(shipping_charge),
                'error_message':False,
                'warning_message':False}

    @api.multi
    def get_fedex_tracking_and_label(self, package_count, picking, ship_request):
        self.ensure_one()
        CompletedPackageDetails = \
        ship_request.response.CompletedShipmentDetail.CompletedPackageDetails[0]

        # By: Nimesh , For Generate Commercial invoice for the international shipment
        if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_FIRST',
                                       'INTERNATIONAL_PRIORITY'] and package_count <= 1 and self.is_commercial_invoce:

            shipment_documents = ship_request.response.CompletedShipmentDetail.ShipmentDocuments[0]
            if shipment_documents:
                attachments = []
                invoice_data = shipment_documents.Parts[0].Image
                invoice_label_binary_data = binascii.a2b_base64(invoice_data)
                attachments.append((
                    'Fedex Commercial Invoice.%s' % self.fedex_shipping_label_file_type,
                    invoice_label_binary_data))
                msg = (_('<b>Commercial Invoice Generated!</b><br/>'))
                picking.message_post(body=msg, attachments=attachments)
        shipping_charge = 0.0
        if hasattr(CompletedPackageDetails, 'PackageRating'):
            shipping_charge = CompletedPackageDetails.PackageRating.PackageRateDetails[
                0].NetCharge.Amount
        else:
            _logger.info("No shipping rate found")

        tracking_number = CompletedPackageDetails.TrackingIds[0].TrackingNumber
        ascii_label_data = \
        ship_request.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[
            0].Image

        label_binary_data = binascii.a2b_base64(ascii_label_data)
        if not tracking_number and ascii_label_data:
            raise ValidationError("Tracking Detail And Label Not Found In Response!")
        return shipping_charge, tracking_number, label_binary_data

    def fedex_ept_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            traking_number = []
            attachments = []
            list = []
            for line in picking.move_lines:
                if line.product_id.type != 'service' and line.product_id.weight <= 0:
                    list.append(line.product_id.name)
            if list:
                raise Warning('Please define weight for the Products !    :%s' % list)
            total_bulk_weight = self.convert_weight(picking.weight_uom_id, self.weight_uom_id,
                                                    picking.weight_bulk)
            package_count = len(picking.package_ids)
            if total_bulk_weight:
                package_count += 1
            shipper_address = picking.picking_type_id.warehouse_id.partner_id
            recipient_address = picking.partner_id
            shipping_instance_id = self.shipping_instance_id
            try:
                FedexConfig = self.shipping_instance_id.get_fedex_api_object(self.prod_environment)
                ship_request = FedexProcessShipmentRequest(FedexConfig)


                picking.check_packages_are_identical()

                package_type = picking.package_ids and picking.package_ids[
                    0].packaging_id.shipper_package_code or self.fedex_default_product_packaging_id.shipper_package_code
                ship_request = self.prepare_shipment_request(shipping_instance_id, ship_request,
                                                             shipper_address, recipient_address,
                                                             package_type)

                # Supported LabelFormatType by fedex
                # COMMON2D, FEDEX_FREIGHT_STRAIGHT_BILL_OF_LADING, LABEL_DATA_ONLY, VICS_BILL_OF_LADING
                ship_request.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'
                ship_request.RequestedShipment.LabelSpecification.ImageType = self.fedex_shipping_label_file_type
                ship_request.RequestedShipment.LabelSpecification.LabelStockType = self.fedex_shipping_label_stock_type
                #                 if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_FIRST', 'INTERNATIONAL_PRIORITY']:
                #                     ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['ELECTRONIC_TRADE_DOCUMENTS']
                #                     ship_request.RequestedShipment.SpecialServicesRequested.EtdDetail.RequestedDocumentCopies = ['COMMERCIAL_INVOICE']
                #                     ship_request.RequestedShipment.ShippingDocumentSpecification.ShippingDocumentTypes = ['COMMERCIAL_INVOICE']
                #                     ship_request.RequestedShipment.ShippingDocumentSpecification.CertificateOfOrigin.DocumentFormat.ImageType = "PDF"
                #                     ship_request.RequestedShipment.ShippingDocumentSpecification.CertificateOfOrigin.DocumentFormat.StockType = ['PAPER_LETTER']
                # This indicates if the top or bottom of the label comes out of the printer first.
                # BOTTOM_EDGE_OF_TEXT_FIRST, TOP_EDGE_OF_TEXT_FIRST
                ship_request.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'BOTTOM_EDGE_OF_TEXT_FIRST'

                # Specify the order in which the labels will be returned : SHIPPING_LABEL_FIRST, SHIPPING_LABEL_LAST
                ship_request.RequestedShipment.LabelSpecification.LabelOrder = "SHIPPING_LABEL_FIRST"

                fedex_master_tracking_id = False
                for sequence, package in enumerate(picking.package_ids, start=1):
                    # A multiple-package shipment (MPS) consists of two or more packages shipped to the same recipient.
                    # The first package in the shipment request is considered the master package.

                    # Note: The maximum number of packages in an MPS request is 200.
                    package_weight = self.convert_weight(picking.weight_uom_id, self.weight_uom_id,
                                                         package.shipping_weight)
                    ship_request = self.add_fedex_package(picking, ship_request, package_weight,
                                                          package_count, number=sequence,
                                                          master_tracking_id=fedex_master_tracking_id,
                                                          package=package)
                    if self.fedex_onerate:
                        ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = [
                            'FEDEX_ONE_RATE']
                    ship_request.send_request()
                    shipping_charge, tracking_number, label_binary_data = self.get_fedex_tracking_and_label(
                            package_count, picking, ship_request)
                    attachments.append(('Fedex-%s.%s' % (
                        tracking_number, self.fedex_shipping_label_file_type), label_binary_data))
                    exact_price += float(shipping_charge)
                    traking_number.append(tracking_number)
                    if sequence == 1 and package_count > 1:
                        fedex_master_tracking_id = ship_request.response.CompletedShipmentDetail.MasterTrackingId.TrackingNumber
                if total_bulk_weight:
                    if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_FIRST',
                                                   'INTERNATIONAL_PRIORITY'] or (
                                    picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN'):
                        order = picking.sale_id
                        company = order.company_id or picking.company_id or self.env.user.company_id
                        order_currency = picking.sale_id.currency_id or picking.company_id.currency_id
                        commodity_country_of_manufacture = picking.picking_type_id.warehouse_id.partner_id.country_id.code
                        commodity_weight_units = self.fedex_weight_uom
                        total_commodities_amount = 0.0
                        for product_list in picking.move_line_ids:
                            if not product_list.result_package_id:
                                total_commodities_amount += (
                                product_list.qty_done * product_list.product_id.list_price)
                                Commodity = ship_request.create_wsdl_object_of_type('Commodity')
                                Commodity.UnitPrice.Currency = order_currency.name
                                Commodity.UnitPrice.Amount = product_list.product_id.list_price
                                Commodity.NumberOfPieces = '1'
                                Commodity.CountryOfManufacture = commodity_country_of_manufacture
                                Commodity.Weight.Units = commodity_weight_units
                                Commodity.Weight.Value = (
                                product_list.qty_done * product_list.product_id.weight)
                                Commodity.Description = product_list.product_id.name
                                Commodity.Quantity = product_list.qty_done
                                Commodity.QuantityUnits = 'EA'
                                Commodity.CustomsValue.Amount = (
                                product_list.qty_done * product_list.product_id.list_price)
                                Commodity.CustomsValue.Currency = order_currency.name
                                ship_request.RequestedShipment.CustomsClearanceDetail.Commodities.append(
                                        Commodity)

                        # By: Nimesh , For Generate Commercial invoice for the international shipment
                        # package_count <= 1 and
                        if package_count <= 1 and self.is_commercial_invoce:
                            commercial_invoice_detail = ship_request.create_wsdl_object_of_type(
                                    'CommercialInvoiceDetail')
                            commercial_invoice_detail.Format.ImageType.value = 'PDF'
                            commercial_invoice_detail.Format.StockType.value = 'PAPER_LETTER'
                            ship_request.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail = commercial_invoice_detail
                            ship_request.RequestedShipment.ShippingDocumentSpecification.ShippingDocumentTypes = 'COMMERCIAL_INVOICE'

                        ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = 'SENDER'
                        ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.AccountNumber = self.shipping_instance_id.fedex_account_number
                        ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Address.CountryCode = picking.picking_type_id.warehouse_id.partner_id.country_id.code
                        ship_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = total_commodities_amount
                        ship_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = order_currency.name
                        if picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN':
                            ship_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose.value = "SOLD"
                        # Hemangi===========================================================================================
                    ship_request = self.add_fedex_package(picking, ship_request, total_bulk_weight,
                                                          package_count, number=package_count,
                                                          master_tracking_id=fedex_master_tracking_id,
                                                          package=False)
                    if self.fedex_onerate:
                        ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = [
                            'FEDEX_ONE_RATE']
                    ship_request.send_request()
                    shipping_charge, tracking_number, label_binary_data = self.get_fedex_tracking_and_label(
                            package_count, picking, ship_request)
                    exact_price += float(shipping_charge)
                    traking_number.append(tracking_number)
                    attachments.append(('Fedex-%s.%s' % (
                        tracking_number, self.fedex_shipping_label_file_type), label_binary_data))
                msg = (_('<b>Shipment created!</b><br/>'))
                picking.message_post(body=msg, attachments=attachments)
            except FedexError as ERROR:
                raise ValidationError(ERROR.value)
            except FedexFailure as ERROR:
                raise ValidationError(ERROR.value)
            except Exception as e:
                raise ValidationError(e)
            res = res + [{'exact_price':exact_price, 'tracking_number':",".join(traking_number)}]
        return res

    def fedex_ept_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = picking.carrier_id and picking.carrier_id.shipping_instance_id and picking.carrier_id.shipping_instance_id.tracking_link or "https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber="
            res = '%s %s' % (link, picking.carrier_tracking_ref)
        return res

    def fedex_ept_cancel_shipment(self, picking):
        try:
            FedexConfig = self.shipping_instance_id.get_fedex_api_object(self.prod_environment)
            delete_request = FedexDeleteShipmentRequest(FedexConfig)
            delete_request.DeletionControlType = "DELETE_ALL_PACKAGES"
            delete_request.TrackingId.TrackingNumber = picking.carrier_tracking_ref.split(',')[
                0]  # master tracking number
            # What kind of shipment the tracking number used.
            # EXPRESS, GROUND, or USPS
            delete_request.TrackingId.TrackingIdType = 'FEDEX'
            delete_request.send_request()
            assert delete_request.response.HighestSeverity in ['SUCCESS', 'WARNING'], \
                "%s : %s" % (picking.carrier_tracking_ref.split(',')[0],
                             delete_request.response.Notifications[0].Message)
        except FedexError as ERROR:
            raise ValidationError(ERROR.value)
        except FedexFailure as ERROR:
            raise ValidationError(ERROR.value)
        except Exception as e:
            raise ValidationError(e)
