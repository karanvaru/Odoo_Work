from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import json
from datetime import datetime
from requests import request
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

    pickup_location_id = fields.Char('Pickup Location')


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    shiprocket_order_id = fields.Char(string="Shiprocket Order ID", help="", copy=False)
    shiprocket_shipment_id = fields.Char(string="Shiprocket Shipment ID", help="", copy=False)
    shiprocket_label_url = fields.Char(string="Shiprocket Label URL", help="", copy=False)
    shiprocket_shipping_charge_ids = fields.One2many("shiprocket.shipping.charge", "picking_id", string="Shiprocket Rate Matrix")
    shiprocket_shipping_charge_id = fields.Many2one("shiprocket.shipping.charge", string="Recommended Courier",help="This Method Is Use Full For Generating The Label",copy=False)
    shiprocket_pickup = fields.Boolean(string="Shiprocket Pickup", default=False)

    def get_shiprocket_charges(self):
        if self.delivery_type == "shiprocket" and self.shiprocket_shipment_id:
            res_status, res_message = self.carrier_id and self.carrier_id.get_shiprocket_charges(self)
            if not res_status:
                raise ValidationError(res_message)
            else:
                return {'effect': {
                    'fadeout': 'slow',
                    'message': "Shipping Charges Imported Successfully..",
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man'}}

    def generate_shiprocket_pickup_manually(self):
        if self.delivery_type == "shiprocket" and not self.shiprocket_pickup:
            pickup_done , message = self.carrier_id.generate_shiprocket_pickup(self)
            if not pickup_done:
                raise ValidationError(message)

    def generate_shiprocket_awd(self):
        if self.delivery_type == "shiprocket" and self.shiprocket_shipment_id:
            res_status, res_message = self.carrier_id and self.carrier_id.generate_shiprocket_awd(self)
            if not res_status:
                raise ValidationError(res_message)
            else:
                return {'effect': {
                    'fadeout': 'slow',
                    'message': "AWD Imported Successfully..",
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man'}}

    def generate_shiprocket_label(self):
        if self.delivery_type == "shiprocket" and self.shiprocket_shipment_id:
            res_status, res_message = self.carrier_id and self.carrier_id.generate_shiprocket_label(self)
            if not res_status:
                raise ValidationError(res_message)
            else:
                return {'effect': {
                    'fadeout': 'slow',
                    'message': "Label Imported Successfully..",
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man'}}

    def _prepaire_address_data(self):
        print("partner>>>>>>>>",self.partner_id.mobile)
        phone_number = ''.join(x for x in self.partner_id.mobile if x.isdigit() or x == '+').replace('+91','')
        phone_number = phone_number[1:] if phone_number[0] == '0' else phone_number
        return {
            "pickup_location": 'rdpret',
            "name": self.partner_id.name,
            "email": self.partner_id.email,
            "phone": phone_number,
            "address": self.partner_id.street,
            "address_2": "",
            "city": self.partner_id.city,
            "state":self.partner_id and self.partner_id.state_id.name,
            "country": self.partner_id and self.partner_id.country_id.name,
            "pin_code": self.partner_id and self.partner_id.zip}

    def get_pickup_location(self):
        try:
            company_id = self.env.user.company_id
            headers = {'Authorization': "Bearer {}".format(company_id.shiprocket_api_token),'Content-Type': 'application/json','Accept': 'application/json'}
            url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"
            if self.partner_id and not self.partner_id.pickup_location_id:
                params = self._prepaire_address_data()
                self.partner_id.pickup_location_id = 874021
                return self.partner_id.pickup_location_id
            else:
                return self.partner_id.pickup_location_id
        except Exception as e:
            raise ValidationError(_("\n Response Data : %s") % (e))

    def _prepaire_items(self):
        item_data = []
        for move_line in self.move_lines:
            item_dict = {
                "name": "%s" % (move_line.product_id and move_line.product_id.name),
                "sku": "%s" % (move_line.product_id and move_line.product_id.default_code),
                "units": int(move_line.product_uom_qty),
                "selling_price": "%s" % (move_line.product_id and move_line.product_id.lst_price),
                "discount": "",
                "tax": ""}
            item_data.append(item_dict)
        return item_data


    def get_subtotal(self):
        total_price = sum([(line.product_id.lst_price * line.product_uom_qty) for line in self.move_lines]) or 0.0
        return total_price

    def shiprocket_return_request_data(self):
        today_date = datetime.now()
        company_id = self.env.user.company_id
        pickup_phone_number = ''.join(x for x in self.partner_id.mobile if x.isdigit() or x == '+').replace('+91','')
        pickup_phone_number = pickup_phone_number[1:] if pickup_phone_number[0] == '0' else pickup_phone_number
        shipping_phone_number = ''.join(x for x in company_id.phone if x.isdigit() or x == '+').replace('+91','')
        shipping_phone_number = shipping_phone_number[1:] if shipping_phone_number[0] == '0' else shipping_phone_number
        shiprocket_packaging_id = self.package_ids[0].packaging_id if self.package_ids and self.package_ids[0].packaging_id else self.carrier_id.shiprocket_packaging_id
        request_data = {
            "order_id": "{0}".format(self.id or ""),
            "order_date":"{}".format(today_date.strftime("%Y-%m-%d")),
            "channel_id": self.carrier_id and self.carrier_id.shiprocket_chanel_id.chanel_code or 0,
            "pickup_customer_name": self.partner_id.name,
            "pickup_last_name": "",
            "pickup_address": self.partner_id.street,
            "pickup_address_2": self.partner_id.street2,
            "pickup_city": self.partner_id.city,
            "pickup_state": self.partner_id and self.partner_id.state_id.name,
            "pickup_country":  self.partner_id and self.partner_id.country_id.name,
            "pickup_pincode":  self.partner_id and self.partner_id.zip,
            "pickup_email": self.partner_id.email,
            "pickup_phone": pickup_phone_number,
            "pickup_isd_code": "",
            "pickup_location_id": self.get_pickup_location(),
            "shipping_customer_name": company_id.name,
            "shipping_last_name": "",
            "shipping_address": company_id.street,
            "shipping_address_2": "",
            "shipping_city": company_id.city,
            "shipping_country": company_id.country_id and company_id.country_id.name,
            "shipping_pincode": company_id.zip,
            "shipping_state": company_id.state_id and company_id.state_id.name,
            "shipping_email": company_id.email,
            "shipping_isd_code": "",
            "shipping_phone": shipping_phone_number,
            'order_items': self._prepaire_items(),
            "payment_method": "Prepaid",
            "total_discount": 0.0,
            "sub_total": self.get_subtotal() or 0.0,
            "length": "{}".format(shiprocket_packaging_id and shiprocket_packaging_id.length or 0.0),
            "breadth": "{}".format(shiprocket_packaging_id and shiprocket_packaging_id.width or 0.0),
            "height": "{}".format(shiprocket_packaging_id and shiprocket_packaging_id.height or 0.0),
            "weight": "{}".format(self.shipping_weight or 0.0)
            }
        return request_data

    def create_reorder(self):
        params = self.shiprocket_return_request_data()
        try:
            company_id = self.env.user.company_id
            headers = {'Authorization': "Bearer {}".format(company_id.shiprocket_api_token),'Content-Type': 'application/json','Accept': 'application/json'}
            url = "https://apiv2.shiprocket.in/v1/external/orders/create/return"
            response = request("POST", url, headers=headers,  data = json.dumps(params))
            if response.status_code in [200, 201]:
                response_data = response.json()
                _logger.info("Response Data : %s" % (response_data))
                if response_data.get("order_id") and response_data.get("shipment_id"):
                    self.shiprocket_order_id = response_data.get("order_id")
                    self.shiprocket_shipment_id = response_data.get("shipment_id")
                    self.generate_shiprocket_awd()
                    self.generate_shiprocket_label()
            else:
                raise ValidationError("Error : {}".format(response.content))

        except Exception as e:
            raise ValidationError(_("\n Response Data : %s") % (e))

    def prepare_data_chargis(self):
        company_id = self.env.user.company_id
        return {"pickup_postcode":  self.partner_id and self.partner_id.zip, 'delivery_postcode' : company_id.zip, 'cod' : 1, 'weight' : "{}".format(self.shipping_weight or 0.0)}

    def call_shiprocket_api(self, api_url=False):
        company_id = self.env.user.company_id
        headers = {'Authorization': "Bearer {}".format(company_id.shiprocket_api_token),
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
        data = json.dumps(self.prepare_data_chargis())
        try:
            _logger.info("Send GET Request From odoo to Shiprocket: {0}".format(url))
            return request("GET", url, headers=headers, data = data)
        except Exception as e:
            _logger.info("Getting an Error in GET Req odoo to Shiprocket: {0}".format(e))
            return e

    def get_incoming_shiprocket_charges(self):
        try:
            response_data = self.call_shiprocket_api()
        except Exception as e:
            raise ValidationError(_("\n Response Data : %s") % (e))
        shipping_charge = self.env['shiprocket.shipping.charge']
        if response_data.status_code in [200, 201]:
            response_data = response_data.json()
            _logger.info("Response Data : %s" % (response_data))
            if response_data.get("data").get("available_courier_companies"):
                for service_response in response_data.get("data").get("available_courier_companies"):
                    if not shipping_charge.search([('courier_id', '=', service_response.get('courier_company_id')),
                                                   ('picking_id', '=', self.id)]):
                        shipping_charge.create({'courier_name': service_response.get('courier_name'),
                                                'courier_id': service_response.get('courier_company_id'),
                                                'rate_amount': service_response.get('rate'),
                                                'estimated_transit_time': service_response.get('etd'),
                                                'picking_id': self.id})
                shiprocket_shipping_charge_id = shipping_charge.search([('picking_id', '=', self.id)],order='rate_amount', limit=1)
                self.shiprocket_shipping_charge_id = shiprocket_shipping_charge_id and shiprocket_shipping_charge_id.id
                return True
            else:
                return False, "Response Data : %s " % (response_data)
        else:
            raise ValidationError("Response Code : %s Response Data : %s " % (response_data.status_code, response_data.text))
