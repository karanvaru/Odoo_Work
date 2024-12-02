import json
import random
import logging
from lxml import etree
from odoo.osv import expression
from odoo import models, fields, api, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import requests
import re

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('gati_ts', "Gati")])
    gati_service_code = fields.Selection([
        ('1', 'Surface Express'),
        ('2', 'Air Express'),
    ], 'Service', required=True, default='1')
    gati_goods_code_id = fields.Many2one("gati.goods.code", string="Goods Code")
    gati_product_packaging_id = fields.Many2one('product.packaging', string="Default Package Type", help="dimension will use when no package define in delivery order.")
    gati_is_cod = fields.Boolean(string="Is COD?")
    gati_booking_type = fields.Selection([('1', 'Paid'), ('2', 'Contractual'), ('3', 'FOD')], 'Booking types', required=True, default='1')

    def gati_ts_create_vendor(self, shipper):
        if shipper.gati_cust_vend_code:
            return shipper.gati_cust_vend_code
        request_data = {
            'custCode': self.shipping_partner_id.gati_customer_code,
            'details' : [{
                "custVendorCode": shipper.id,
                "custVendorName": shipper.name,
                "vendorAdd1": shipper.street or '',
                "vendorAdd2": shipper.street2 or '',
                "vendorCity": shipper.city or '',
                "vendorPhoneNo": re.sub('[^0-9]', '', shipper.phone or ''),
                "vendorPincode": shipper.zip,
                "vendorEmail": '',
                "vendorReceiverFlag": 'V',
                "vendorTinno": "",
                "VendorGSTNO": shipper.vat or '',
            }]
        }
        response = self.shipping_partner_id._gati_send_request('GKEJCustVendDtls.jsp', request_data=request_data, prod_environment=self.prod_environment, method="POST")
        if response.get('postedData') == 'successful' and response.get('reqcnt', 0) == 1:
            shipper.write({'gati_cust_vend_code': shipper.id})
            return shipper.id
        else:
            raise UserError("Something went wrong.\nError Message: {}".format(response.get('errmsg')))

    def gati_ts_prepare_request_data(self, shipper, recipient):
        self.ensure_one()
        gati_docket_number = self.env['gati.docket.package.number'].search([('type', '=', 'docket'), ('is_used', '=', False)], limit=1)
        if not gati_docket_number:
            raise UserError(_('All the docket numbers you have generated have been used. Please generate new docket numbers'))
        gati_docket_number.write({'is_used': True})
        request_data = {'docketNo': gati_docket_number.name or '',
                        'goodsCode': self.gati_goods_code_id.code or '',
                        'deliveryStn': '',
                        'codInFavourOf': '',
                        'shipperCode': self.shipping_partner_id.gati_customer_code,
                        'receiverCode': '99999',  # Default value to be passed as 99999. However, if Customer wants delivery to their vendors than they can pass the same code, provided it is updated in Gati System (Cus-tomer Vendor Master)
                        'receiverName': recipient.name or '',
                        'receiverAdd1': recipient.street or '',
                        'receiverAdd2': recipient.street2 or 'null',
                        "receiverAdd3": '',
                        "receiverAdd4": '',
                        'receiverCity': recipient.city or '',
                        'receiverPinCode': recipient.zip or '',
                        'receiverPhoneNo': re.sub('[^0-9]', '', recipient.phone or ''),
                        'receiverMobileNo': re.sub('[^0-9]', '', recipient.mobile or recipient.phone or ''),
                        'receiverEmail': recipient.email or '',
                        'custVendCode': self.gati_ts_create_vendor(shipper),
                        'prodServCode': self.gati_service_code or '',
                        'bookingBasis': self.gati_booking_type,
                        'UOM': "I",  # to be passed I – In case of Inch, CC – In case of Cubic Centimetre, CF - In caseof Cubic Feet
                        'CustDeliveyDate': '',
                        'consignorGSTINNo': shipper.vat or '',  # Optional but response in get error
                        'ReceiverGSTINNo': recipient.vat or '',  # Optional but response in get error
                        'codAmt': 0,
                        }
        return request_data, gati_docket_number

    def _gati_ts_convert_dimension_uom(self, dimension):
        weight_uom_id = self.env.ref('uom.product_uom_cm')
        if self.env.ref('uom.product_uom_inch').id != weight_uom_id.id:
            dimension = weight_uom_id._compute_quantity(dimension, self.env.ref('uom.product_uom_inch'), round=False)
        return dimension

    @api.model
    def gati_ts_add_parcel(self, package, weight):
        gati_packet_number = self.env['gati.docket.package.number'].search([('type', '=', 'packet'), ('is_used', '=', False)], limit=1)
        if not gati_packet_number:
            raise UserError(_('All the packet numbers you have generated have been used. Please generate new packet numbers'))
        parcel_dict = {"pkgNo": gati_packet_number.name,
                       'pkgLn': self._gati_ts_convert_dimension_uom(package.length),
                       'pkgBr': self._gati_ts_convert_dimension_uom(package.width),
                       'pkgHt': self._gati_ts_convert_dimension_uom(package.height),
                       'pkgWt': weight}
        gati_packet_number.write({'is_used': True, 'act_weight': weight})
        return parcel_dict, gati_packet_number

    def _gati_ts_convert_weight(self, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if self.env.ref('uom.product_uom_kgm').id != weight_uom_id.id:
            weight = weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        return weight

    def gati_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            tracking_number_list = []
            attachments = []
            order = picking.sale_id
            if not picking.gati_from_pincode or not picking.gati_to_pincode:
                raise UserError("Please define Gati From and To Location in additional info before requesting shipment to Gati!")
            total_bulk_weight = self._gati_ts_convert_weight(picking.weight_bulk)
            from_address, to_address = picking.get_gati_from_and_to_address()
            try:
                request_data = {'custCode': self.shipping_partner_id.gati_customer_code, 'pickupRequest': picking.gati_pickup_date.strftime("%d-%m-%Y %H:%M:%S")}
                request_details, gati_docket_number = self.gati_ts_prepare_request_data(from_address, to_address)
                if self.gati_is_cod:
                    request_details.update({'codAmt': order.amount_total, 'codInFavourOf': 'S'})
                if picking.is_eway_bill:
                    request_details.update({'EWAYBILL': picking.ewaybill_number, 'EWB_EXP_DT': picking.ewaybill_date})
                picking.write({'gati_docket_id': gati_docket_number.id})
                if not picking.gati_location_code_id:
                    raise UserError(_('Please, select the Gati location'))
                else:
                    request_details.update({'locationCode': picking.gati_location_code_id.location_code or ''})
                request_details.update({'declCargoVal': picking.sale_id.amount_total or picking.purchase_id.amount_total or 0.1})
                request_details.update({'actualWt': total_bulk_weight + sum(picking.package_ids.mapped('shipping_weight')) or ''})
                request_details.update({'chargedWt': total_bulk_weight + sum(picking.package_ids.mapped('shipping_weight')) or ''})
                request_details.update({'orderNo': picking.sale_id.name or picking.purchase_id.name or picking.origin})
                request_data['details'] = [request_details]
                package_list = []
                if picking.package_ids:
                    # Create all packages
                    for package in picking.package_ids:
                        parcel_dict, gati_packet_id = self.gati_ts_add_parcel(package.packaging_id, package.shipping_weight)
                        package.write({'gati_packet_id': gati_packet_id.id})
                        package_list.append(parcel_dict)
                # Create one package with the rest (the content that is not in a package)
                if total_bulk_weight:
                    parcel_dict, gati_packet_id = self.gati_ts_add_parcel(self.gati_product_packaging_id, total_bulk_weight)
                    picking.write({'gati_packet_id': gati_packet_id.id})
                    package_list.append(parcel_dict)
                request_details.update({'noOfPkgs': len(package_list)})
                request_details.update({'pkgDetails': {"pkginfo": package_list}})
                if len(package_list) > 1:
                    request_details.update({'fromPkgNo': package_list[0].get('pkgNo')})
                    request_details.update({'toPkgNo': package_list[-1].get('pkgNo')})
                else:
                    request_details.update({'fromPkgNo': package_list[0].get('pkgNo')})
                    request_details.update({'toPkgNo': package_list[0].get('pkgNo')})
                request_details.update({'goodsDesc': ', '.join(picking.move_ids_without_package.mapped('product_id').mapped('name'))})
                response = self.shipping_partner_id._gati_send_request('GATIKWEJPICKUPLBH.jsp', request_data, self.prod_environment, method="POST")
                if response.get('postedData') == 'successful' and response.get('details')[0].get('errmsg') == 'succes':
                    label_res = self.download_gati_label_pdf(picking)
                    if label_res:
                        attachments.append(
                            ('Gati-%s.%s' % (picking.name, 'pdf'), label_res))
                else:
                    war_message = response.get('details')[0].get('errmsg')
                    raise UserError(_(war_message))
                tracking_number_list.append(response.get('details')[0].get('docketNo'))
                msg = (_('<b>Shipment created!</b><br/>'))
                picking.message_post(body=msg, attachments=attachments)
            except Exception as e:
                raise UserError(e)
            res = res + [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res

    def download_gati_label_pdf(self, picking_id):
        picking_report = self.env.ref('gati_delivery.action_report_gati_labels', raise_if_not_found=True)
        picking_id = self.env['stock.picking'].browse(int(picking_id))
        if not picking_id:
            return self.not_found("There is nothing to Print!!!")
        picking_types_pdf, _ = picking_report.render_qweb_pdf(picking_id.id)
        return picking_types_pdf

    def _get_package_vals(self, picking):
        gati_package_vals = self.env['gati.docket.package.number']
        if picking:
            gati_package_vals = picking.package_ids.mapped('gati_packet_id') + picking.gati_packet_id
        return gati_package_vals

    def gati_ts_get_tracking_link(self, picking):
        raise UserError(_('Tracking is not available'))

    def gati_ts_cancel_shipment(self, picking):
        if picking.carrier_tracking_ref:
            msg = (_('Note: Tracking number %s has been removed from Odoo not from the Gati. You may need to contact Gati to cancel it!')) % picking.carrier_tracking_ref
            picking.message_post(body=msg)
