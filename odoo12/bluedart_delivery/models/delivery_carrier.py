import json
import random
import logging
from odoo import models, fields, api, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('bluedart_ts', "Blue Dart")])
    bd_service_id = fields.Many2one('bluedart.service', 'Service')
    bd_product_packaging_id = fields.Many2one('product.packaging', string="Default Package Type", help="dimension will use when no package define in delivery order.")

    @api.multi
    def bluedart_ts_prepare_request_data(self, shipper, recipient):
        self.ensure_one()
        request_data = {
            'Shipper': {
                'OriginArea': self.shipping_partner_id.bd_area,
                'CustomerCode': self.shipping_partner_id.bd_customer_code,
                'CustomerName': shipper.name and shipper.name[:30],
                'CustomerAddress1': shipper.street and shipper.street[:30],
                'CustomerAddress2': shipper.street2 and shipper.street2[:30] or '',
                'CustomerPincode': shipper.zip,
                'CustomerMobile': shipper.mobile or '',
                'CustomerEmailID': shipper.email or '',
                'Sender': shipper.name[:20],
                # 'IsReversePickup': False,
                'IsToPayCustomer':True,
            },
            'Consignee': {
                'ConsigneeName': recipient.name[:30],
                'ConsigneeAddress1': recipient.street and recipient.street[:30],
                'ConsigneeAddress2': recipient.street2 and recipient.street2[:30],
                'ConsigneePincode': recipient.zip,
                'ConsigneeTelephone': recipient.phone or '',
                'ConsigneeMobile': recipient.mobile or '',
                'ConsigneeEmailID': recipient.email or '',
            },
            'Services': {
                'ProductCode': self.bd_service_id.product_code,
                'SubProductCode': self.bd_service_id.product_sub_code,
                'ProductType': 'Dutiables',  # Docs/Dutiables
                'PackType': self.bd_service_id.package_type,
            }
        }
        return request_data

    def _bluedart_ts_convert_weight(self, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if self.env.ref('uom.product_uom_kgm').id != weight_uom_id.id:
            weight = weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        return weight

    def bluedart_ts_rate_shipment(self, order):
        shipping_charge = self._get_price_available(order)
        return {'success': True, 'price': shipping_charge, 'error_message': False, 'warning_message': False}

    def bluedart_check_service_availability(self, recipient, picking=False):
        client, request_data = self.shipping_partner_id._bluedart_prepare_client('service_finder', prod_environment=self.prod_environment)
        request_data.update({'pinCode': recipient.zip})
        response = client.service.GetServicesforPincode(**request_data)
        _logger.info('================================',response)
        
        if response.ErrorMessage != 'Valid':
            _logger.info('================================',response)
            raise UserError("Service not available for pincode {}.\nError Message: {}".format(recipient.zip, response.ErrorMessage))
        return True

    def bluedart_ts_prepare_item_data(self, picking=False, package=False, bulk=False):
        item_list = []
        if picking and not package and not bulk:
            for line in picking.move_ids_without_package:
                price_subtotal = line.sale_line_id.price_subtotal or line.purchase_line_id.price_subtotal or 0.1
                item_list.append({
                    'ItemID': line.product_id.id,
                    'ItemName': line.product_id.name,
                    'ProductDesc1': line.product_id.description_sale or '',
                    'ItemValue': tools.float_round(price_subtotal, precision_digits=2),
                    'SKUNumber': line.product_id.default_code or '',
                    'Itemquantity': int(line.quantity_done),
                    'HSCode': line.product_id.hs_code or '',
                })
        elif picking and package:
            for line in picking.move_line_ids.filtered(lambda x: x.result_package_id == package):
                if line.product_id.type not in ['product', 'consu']:
                    continue
                price_unit = line.move_id.sale_line_id.price_unit or line.move_id.purchase_line_id.price_unit or 0.1
                item_list.append({
                    'ItemID': line.product_id.id,
                    'ItemName': line.product_id.name,
                    'ProductDesc1': line.product_id.description_sale or '',
                    'ItemValue': tools.float_round((price_unit * line.qty_done), precision_digits=2),
                    'SKUNumber': line.product_id.default_code or '',
                    'Itemquantity': int(line.qty_done),
                    'HSCode': line.product_id.hs_code or '',
                })
        elif picking and bulk:
            for line in picking.move_line_ids.filtered(lambda x: not x.result_package_id):
                if line.product_id.type not in ['product', 'consu']:
                    continue
                price_unit = line.move_id.sale_line_id.price_unit or line.move_id.purchase_line_id.price_unit or 0.1
                item_list.append({
                    'ItemID': line.product_id.id,
                    'ItemName': line.product_id.name,
                    'ProductDesc1': line.product_id.description_sale or '',
                    'ItemValue': tools.float_round((price_unit * line.qty_done), precision_digits=2),
                    'SKUNumber': line.product_id.default_code or '',
                    'Itemquantity': int(line.qty_done),
                    'HSCode': line.product_id.hs_code or '',
                })
        return item_list

    @api.multi
    def check_required_value_bluedart_shipping_request(self, pickings):
        for picking in pickings:
            if not picking.move_lines:
                raise UserError("You don't have any item to ship.")
            else:
                lines_without_weight = picking.move_lines.filtered(lambda line_item: not line_item.product_id.weight)
                for line in lines_without_weight:
                    raise UserError("Please define weight in product : \n %s" % line.product_id.name)
        return True

    def bluedart_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            tracking_number_list = []
            attachments = []
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            is_dropship_picking = False
            if picking.picking_type_id.default_location_src_id.usage == 'supplier' and picking.picking_type_id.default_location_dest_id.usage == 'customer':
                is_dropship_picking = True
            self.check_required_value_bluedart_shipping_request(pickings=picking)
            recipient = picking.purchase_id.dest_address_id if is_dropship_picking else picking.partner_id
            self.bluedart_check_service_availability(recipient, picking=picking)
            total_bulk_weight = self._bluedart_ts_convert_weight(picking.weight_bulk)
            pickup_date = picking.carrier_pickup_time + timedelta(hours=5, minutes=30)
            package_count = len(picking.package_ids)
            if total_bulk_weight:
                package_count += 1
            waybill_request_list = []
            sender = picking.partner_id if is_dropship_picking else picking.picking_type_id.warehouse_id.partner_id
            if picking.picking_type_id.code == 'incoming':
                recipient = picking.picking_type_id.warehouse_id.partner_id  
                sender = picking.partner_id 

            prepared_data = self.bluedart_ts_prepare_request_data(sender , recipient)
            prepared_data['Services']['InvoiceNo'] = order.name or ''
            prepared_data['Services']['PickupDate'] = pickup_date.date()
            prepared_data['Services']['PickupTime'] = pickup_date.strftime('%H%M')
            prepared_data['Services']['RegisterPickup'] = True
            prepared_data['Services']['IsForcePickup'] = True
            prepared_data['Services']['PieceCount'] = 1 if self.bd_service_id.product_code == 'A' else package_count
            prepared_data['Services']['InvoiceNo'] = order.name or ''
            prepared_data['Services']['DeclaredValue'] = order.amount_total or picking.purchase_id.amount_total or 0.1
            # prepared_data['Services']['CreditReferenceNo'] = "{}".format((picking.sale_id.name or picking.purchase_id.name or picking.origin).replace(" ",""))
            prepared_data['Services']['CreditReferenceNo'] = str(picking.id) + str(order.id) + str(random.randint(1000, 9999)) if order else str(picking.id) + str(random.randint(1000, 9999))
            prepared_data['Services']['Dimensions'] = {'Dimension': []}
            prepared_data['Services']['PickupDate'] = pickup_date.date()
            prepared_data['Services']['PickupTime'] = pickup_date.strftime('%H%M')
            prepared_data['Services']['RegisterPickup'] = True
            prepared_data['Services']['IsForcePickup'] = True
            prepared_data['Services']['ItemCount'] = len(picking.move_ids_without_package)
            # if picking.picking_type_id.code == 'incoming':
            #     prepared_data['Services']['IsReversePickup'] = True
            if self.bd_service_id.product_sub_code == 'C':
                prepared_data['Services']['CollectableAmount'] = order.amount_total
            # if is_dropship_picking:
            prepared_data['Shipper']['IsToPayCustomer'] = True
            if picking.package_ids.filtered(lambda x: not x.packaging_id):
                raise UserError("Please define 'Package Type' in created package.")
            package_dict = {pack_id: picking.package_ids.filtered(lambda x: x.packaging_id == pack_id) for pack_id in picking.package_ids.mapped('packaging_id')}
            total_package_weight = 0.0

            for package_type, packages in package_dict.items():
                for package in packages:
                    if self.bd_service_id.product_code == 'A':
                        final_dict = prepared_data.copy()
                        final_dict['Services'] = prepared_data['Services'].copy()
                        final_dict['Services']['CreditReferenceNo'] = "{}".format((picking.name).replace(" ",""))
                        # final_dict['Services']['CreditReferenceNo'] = str(picking.id) + str(order.id) + package.name if order else str(picking.id) + package.name
                        final_dict['Services'].update({'Dimensions': {'Dimension': {
                            'Length': package_type.length,
                            'Breadth': package_type.width,
                            'Height': package_type.height,
                            'Count': 1}}}
                        )
                        item_details = self.bluedart_ts_prepare_item_data(picking, package)
                        final_dict['Services'].update({'ActualWeight': self._bluedart_ts_convert_weight(package.shipping_weight)})
                        final_dict['Services'].update({'itemdtl': {'ItemDetails': item_details}, 'ItemCount': len(item_details), 'DeclaredValue': sum([item.get('ItemValue') for item in item_details])})
                        waybill_request_list.append(final_dict)
                    else:
                        total_package_weight += self._bluedart_ts_convert_weight(package.shipping_weight)
                if self.bd_service_id.product_code != 'A':
                    prepared_data['Services']['Dimensions']['Dimension'].append({
                        'Length': package_type.length,
                        'Breadth': package_type.width,
                        'Height': package_type.height,
                        'Count': len(packages),
                    })
            if total_bulk_weight:
                if self.bd_service_id.product_code == 'A':
                    final_dict = prepared_data.copy()
                    final_dict['Services'] = prepared_data['Services'].copy()
                    final_dict['Services']['CreditReferenceNo'] = str(picking.id) + '/' + str(random.randint(1000, 9999))
                    final_dict['Services']['Dimensions']['Dimension'] = {
                        'Length': self.bd_product_packaging_id.length,
                        'Breadth': self.bd_product_packaging_id.width,
                        'Height': self.bd_product_packaging_id.height,
                        'Count': 1,
                    }
                    item_details = self.bluedart_ts_prepare_item_data(picking, bulk=True)
                    final_dict['Services']['ActualWeight'] = total_bulk_weight
                    final_dict['Services'].update({'itemdtl': {'ItemDetails': item_details}, 'ItemCount': len(item_details)})
                    waybill_request_list.append(final_dict)
                else:
                    prepared_data['Services']['Dimensions']['Dimension'].append({
                        'Length': self.bd_product_packaging_id.length,
                        'Breadth': self.bd_product_packaging_id.width,
                        'Height': self.bd_product_packaging_id.width,
                        'Count': 1,
                    })
            if self.bd_service_id.product_code != 'A':
                prepared_data['Services']['ActualWeight'] = total_package_weight + total_bulk_weight
                prepared_data['Services']['itemdtl'] = {'ItemDetails': self.bluedart_ts_prepare_item_data(picking)}
                waybill_request_list.append(prepared_data)

            try:
                client, request_data = self.shipping_partner_id._bluedart_prepare_client('waybill', prod_environment=self.prod_environment)
                request_data.update({'Request': {'WayBillGenerationRequest': waybill_request_list}, 'Profile': request_data.pop('profile')})
                response = client.service.ImportData(**request_data)
                _logger.info('================================',response)

                error_message = ''
                for wb in response:
                    _logger.info('================================',response)
                    if wb.IsError:
                        status_messages = wb.Status.WayBillGenerationStatus
                        for message in status_messages:
                            error_message += '{} - {}\n'.format(message.StatusCode, message.StatusInformation)
                        continue
                    tracking_number = wb.AWBNo
                    tracking_number_list.append(tracking_number)
                    attachments.append(('BlueDart-%s.%s' % (tracking_number, 'pdf'), wb.AWBPrintContent))
                if error_message:
                    raise UserError(error_message)
                # if response.IsError:
                #     status_messages = response.Status.WayBillGenerationStatus
                #     error_message = 'Blue Dart Error: \n\n'
                #     for message in status_messages:
                #         error_message += '{} - {}\n'.format(message.StatusCode, message.StatusInformation)
                #     raise UserError(error_message)
                # tracking_number = response.AWBNo
                # attachments.append(('BlueDart-%s.%s' % (tracking_number, 'pdf'), response.AWBPrintContent))
                msg = (_('<b>Shipment created!</b><br/>'))
                picking.message_post(body=msg, attachments=attachments)
            except Exception as e:
                raise UserError(e)
            res = res + [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res

    def bluedart_ts_get_tracking_link(self, picking):
        tracking_numbers = picking.carrier_tracking_ref.split(',')
        if len(tracking_numbers) == 1:
            return 'https://www.bluedart.com/trackdartresultthirdparty?trackFor=0&trackNo={}'.format(picking.carrier_tracking_ref)
        tracking_urls = []
        for tracking_number in tracking_numbers:
            tracking_urls.append((tracking_number, 'https://www.bluedart.com/trackdartresultthirdparty?trackFor=0&trackNo={}'.format(tracking_number)))
        return json.dumps(tracking_urls)

    def bluedart_ts_cancel_shipment(self, picking):
        tracking_numbers = picking.carrier_tracking_ref.split(',')
        for tracking_number in tracking_numbers:
            try:
                client, request_data = self.shipping_partner_id._bluedart_prepare_client('waybill', prod_environment=self.prod_environment)
                request_data.update({'Request': {'AWBNo': tracking_number}, 'Profile': request_data.pop('profile')})
                res = client.service.CancelWaybill(**request_data)
                if res.IsError:
                    status_messages = res.Status.WayBillGenerationStatus
                    error_message = 'Blue Dart Error: \n\n'
                    for message in status_messages:
                        error_message += '{} - {}\n'.format(message.StatusCode, message.StatusInformation)
                    raise UserError(error_message)
            except Exception as e:
                raise UserError(e)
