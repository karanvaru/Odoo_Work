import base64
import logging
import json
from datetime import datetime
from requests import request
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("shiprocket", "Shiprocket")])
    shiprocket_chanel_id = fields.Many2one('shiprocket.channels', string="Shiprocket Channels")
    shiprocket_packaging_id = fields.Many2one('product.packaging', string="Default Package Type")
    shiprocket_payment_method = fields.Selection([('Prepaid', 'Prepaid'), ('COD', 'COD')], default="Prepaid",
                                                 string='Shiprocket Payment Method')
    one_click_generate_label = fields.Boolean(default=False, string="One Click Generate Label")

    def shiprocket_rate_shipment(self, order):
        return {'success': True, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def shiprocket_order_request_data(self, picking):
        receipient_address = picking.partner_id
        item_data = []
        total_price = sum([(line.product_id.lst_price * line.product_uom_qty) for line in picking.move_lines]) or 0.0

        for move_line in picking.move_lines:
            item_dict = {
                "name": "%s" % (move_line.product_id and move_line.product_id.name),
                "sku": "%s" % (move_line.product_id and move_line.product_id.default_code),
                "units": int(move_line.product_uom_qty),
                "selling_price": "%s" % (move_line.product_id and move_line.product_id.lst_price),
                "discount": "",
                "tax": ""}

            item_data.append(item_dict)
        today_date = datetime.now()
        phone_number = ''.join(x for x in receipient_address.phone if x.isdigit() or x == '+').replace('+91','')
        phone_number = phone_number[1:] if phone_number[0] == '0' else phone_number
        total_discount = 0
        if picking.sale_id and picking.sale_id.order_line:
            total_discount = abs(sum(picking.sale_id.order_line.filtered(lambda line: line.price_unit < 0).mapped('price_subtotal')))
        shiprocket_packaging_id = picking.package_ids[0].packaging_id if picking.package_ids and picking.package_ids[0].packaging_id else self.shiprocket_packaging_id
        request_data = {
            "order_id": "{0}_{1}".format(picking.id,picking.sale_id and picking.sale_id.id or ""),
            "channel_id": self.shiprocket_chanel_id and self.shiprocket_chanel_id.chanel_code or 0,
            "order_date": "{}".format(today_date.strftime("%Y-%m-%d")),
            "comment": "{}".format(picking.name),
            "billing_customer_name": receipient_address.name,
            "billing_last_name": "",
            "billing_address": receipient_address.street,
            "billing_address_2": receipient_address.street2 or "",
            "billing_city": receipient_address.city,
            "billing_pincode": "{}".format(receipient_address.zip),
            "billing_state": receipient_address.state_id and receipient_address.state_id.name,
            "billing_country": receipient_address.country_id and receipient_address.country_id.name,
            "billing_email": receipient_address.email,
            "billing_phone": phone_number,
            "shipping_is_billing": True,
            "shipping_customer_name": receipient_address.name,
            "shipping_last_name": "",
            "shipping_address": receipient_address.street,
            "shipping_address_2": receipient_address.street2 or "",
            "shipping_city": receipient_address.city,
            "shipping_pincode": "{}".format(receipient_address.zip),
            "shipping_country": receipient_address.country_id and receipient_address.country_id.name,
            "shipping_state": receipient_address.state_id and receipient_address.state_id.name,
            "shipping_email": receipient_address.email,
            "shipping_phone": phone_number,
            "order_items": item_data,
            "payment_method": self.shiprocket_payment_method,
            "shipping_charges": 0,
            "giftwrap_charges": 0,
            "transaction_charges": 0,
            "total_discount": "{}".format(total_discount),
            "sub_total": total_price,
            "length": "{}".format(shiprocket_packaging_id and shiprocket_packaging_id.length or 0.0),
            "breadth": "{}".format(shiprocket_packaging_id and shiprocket_packaging_id.width or 0.0),
            "height": "{}".format(shiprocket_packaging_id and shiprocket_packaging_id.height or 0.0),
            "weight": picking.shipping_weight
        }
        return request_data

    def shiprocket_send_shipping(self, pickings):
        if not self.company_id:
            raise ValidationError("Company Not set in Shiprocket delivery method!")
        for picking in pickings:
            if picking.shiprocket_order_id and picking.shiprocket_shipment_id:
                shipping_data = {'exact_price': 0.0,
                                 'tracking_number': picking.carrier_tracking_ref}
                shipping_data = [shipping_data]
                return shipping_data
            try:
                request_data = self.shiprocket_order_request_data(picking)
                response_data = self.company_id.call_post_shiprocket_api("/orders/create/adhoc", request_data)
            except Exception as e:
                raise ValidationError(_("\n Response Data : %s") % (e))
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                _logger.info("Response Data : %s" % (response_data))
                if response_data.get("order_id") and response_data.get("shipment_id"):
                    picking.shiprocket_order_id = response_data.get("order_id")
                    picking.shiprocket_shipment_id = response_data.get("shipment_id")
                    self._cr.commit()
                    if self.one_click_generate_label:
                        try:
                            self.get_shiprocket_charges(picking)
                            res_status, res_message = self.generate_shiprocket_awd(picking)
                            if not res_status:
                                if picking.batch_id:
                                    picking.batch_id.message_post(body="%s : %s" % (picking.name, res_message))
                                else:
                                    picking.message_post(body="%s : %s" % (picking.name, res_message))
                            self._cr.commit()
                            if picking.carrier_tracking_ref:
                                self.generate_shiprocket_label(picking)
                                self.generate_shiprocket_pickup(picking)
                            picking.shiprocket_shipping_charge_id and picking.shiprocket_shipping_charge_id.set_service()
                            self._cr.commit()
                        except Exception as e:
                            if picking.batch_id:
                                picking.batch_id.message_post(body=e)
                            else:
                                raise ValidationError(_("Response Data : %s ") % (e))
                    shipping_data = {'exact_price': picking.carrier_price or 0.0,
                                     'tracking_number': picking.carrier_tracking_ref}
                    shipping_data = [shipping_data]
                    return shipping_data
                else:
                    raise ValidationError(_("Response Data : %s ") % (response_data))
            else:
                raise ValidationError(
                    _("Response Code : %s Response Data : %s ") % (response_data.status_code, response_data.text))

    def get_shiprocket_charges(self, picking):
        print("picking>>>>>>>>>>>",picking)
        try:
            api_url = "/courier/serviceability/?order_id={0}&weight={1}".format(picking.shiprocket_order_id,
                                                                                picking.shipping_weight)
            response_data = self.company_id.call_get_shiprocket_api(api_url)
            print("responce>>>>>>>>>>",response_data, response_data.json())
        except Exception as e:
            raise ValidationError(_("\n Response Data : %s") % (e))
        shipping_charge = self.env['shiprocket.shipping.charge']
        if response_data.status_code in [200, 201]:
            response_data = response_data.json()
            _logger.info("Response Data : %s" % (response_data))
            if response_data.get("data").get("available_courier_companies"):
                for service_response in response_data.get("data").get("available_courier_companies"):
                    if not shipping_charge.search([('courier_id', '=', service_response.get('courier_company_id')),
                                                   ('picking_id', '=', picking.id)]):
                        shipping_charge.create({'courier_name': service_response.get('courier_name'),
                                                'courier_id': service_response.get('courier_company_id'),
                                                'rate_amount': service_response.get('rate'),
                                                'estimated_transit_time': service_response.get('etd'),
                                                'picking_id': picking.id})
                shiprocket_shipping_charge_id = shipping_charge.search([('picking_id', '=', picking.id)],order='rate_amount', limit=1)
                picking.shiprocket_shipping_charge_id = shiprocket_shipping_charge_id and shiprocket_shipping_charge_id.id
                return True, "Done"
            else:
                return False, "Response Data : %s " % (response_data)
        else:
            return False, "Response Code : %s Response Data : %s " % (response_data.status_code, response_data.text)

    def generate_shiprocket_awd(self, picking):
        try:
            request_data = {"courier_id": "{}".format(
                picking.shiprocket_shipping_charge_id and picking.shiprocket_shipping_charge_id.courier_id or ""),
                "shipment_id": "{}".format(picking.shiprocket_shipment_id)}
            response_data = self.company_id.call_post_shiprocket_api("/courier/assign/awb", request_data)
            print('responce data>>>>>>>>>',response_data)
        except Exception as e:
            raise ValidationError(_("\n Response Data : %s") % (e))
        if response_data.status_code in [200, 201]:
            response_data = response_data.json()
            _logger.info("Response Data : %s" % (response_data))
            if response_data.get("response") and response_data.get("response").get("data") and response_data.get(
                    "response").get("data").get("awb_code"):
                picking.carrier_tracking_ref = response_data.get("response").get("data").get("awb_code")
                return True, "Done"
            else:
                return False, "Response Data : %s " % (response_data)
        else:
            return False, "Response Code : %s Response Data : %s " % (response_data.status_code, response_data.text)

    def generate_shiprocket_label(self, picking):
        try:
            request_data = {"shipment_id": ["{}".format(picking.shiprocket_shipment_id)]}
            response_data = self.company_id.call_post_shiprocket_api("/courier/generate/label", request_data)
            print("request>>>>>>>",response_data, response_data.json())
        except Exception as e:
            raise ValidationError(_("\n Response Data : %s") % (e))
        if response_data.status_code in [200, 201]:
            response_data = response_data.json()
            _logger.info("Response Data : %s" % (response_data))
            if response_data.get("label_url"):
                picking.shiprocket_label_url = response_data.get("label_url")
                url = response_data.get("label_url")
                headers = {'Content-Type': "application/x-www-form-urlencoded", 'Accept': "application/pdf"}
                response_data = request(method='GET', url=url, headers=headers)
                logmessage = _("<b>Tracking Numbers:</b> %s") % (picking.carrier_tracking_ref)
                # attachment = self.env['ir.attachment'].create({'name': "%s" % (picking.id),
                #                                   #       'datas_fname': "%s.pdf" % (picking.id),
                #                                   'type': 'binary',
                #                                   'datas': base64.b64encode(response_data.content) or "",
                #                                   'mimetype': 'application/pdf',
                #                                   'res_model': 'stock.picking',
                #                                   'res_id': picking.id, 'res_name': picking.name})
                picking.message_post(body=logmessage, attachments=[( "%s.pdf" % (picking.id), response_data.content)])
                return True, "Done"
            else:
                return False, "Response Data : %s " % (response_data)
        else:
            return False, "Response Code : %s Response Data : %s " % (response_data.status_code, response_data.text)

    def generate_shiprocket_pickup(self,picking):
        try:
            request_data = {"shipment_id": ["{}".format(picking.shiprocket_shipment_id)]}
            response_data = self.company_id.call_post_shiprocket_api("/courier/generate/pickup", request_data)
        except Exception as e:
            return False, "\n Response Data : %s" % (e)
        if response_data.status_code in [200, 201]:
            response_data = response_data.json()
            _logger.info("Response Data : %s" % (response_data))
            if response_data.get("pickup_status") == 1:
                picking.shiprocket_pickup = True
                return True, "Done"
            else:
                return False, "Response Data : %s " % (response_data)
        else:
            return False, "Response Code : %s Response Data : %s " % (response_data.status_code, response_data.text)

    def shiprocket_get_tracking_link(self, pickings):
        return "https://shiprocket.co/tracking/{0}".format(pickings.carrier_tracking_ref)
