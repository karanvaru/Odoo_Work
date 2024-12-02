import base64
import json
import requests
from odoo import tools
from zeep import Client
from odoo import models, fields, api
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('bluedart_ts', 'Blue Dart')])
    bd_user_name = fields.Char("Login")
    bd_password = fields.Char("Password")
    bd_licence_key = fields.Char("LicenceKey")
    bd_area = fields.Char("Origin Area Code")
    bd_customer_code = fields.Char("Customer Code")
    bd_pickup_after = fields.Float("Pickup Delay", default=2.0)

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'bluedart_ts':
            image_path = get_module_resource('bluedart_delivery', 'static/description', 'icon.png')
            self.image = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        return res

    @api.one
    def blue_dart_test_connection(self):
        client, request_data = self._bluedart_prepare_client('service_finder')
        request_data.update({'pinCode':'360004'})
        response = client.service.GetServicesforPincode(**request_data)
        if response.ErrorMessage != 'Valid':
            raise UserError("Something went wrong.\nError Message: {}".format(response.ErrorMessage))
        raise UserError("Test Connection Succeeded")

    def _bluedart_get_wsdl_url(self, request_type):
        if request_type == 'service_finder':
            return 'ShippingAPI/Finder/ServiceFinderQuery.svc?wsdl'
        elif request_type == 'pickup':
            return 'ShippingAPI/Pickup/PickupRegistrationService.svc?wsdl'
        elif request_type == 'waybill':
            return 'ShippingAPI/WayBill/WayBillGeneration.svc?wsdl'
        raise UserError("Technical Problem : Invalid request_type. Contact your administrator!")

    @api.model
    def _bluedart_prepare_client(self, request_type='waybill', prod_environment=True):
        request_url = self._bluedart_get_wsdl_url(request_type)
        if prod_environment:
            api_url = 'https://netconnect.bluedart.com/Ver1.9/' + request_url
        else:
            api_url = 'https://netconnect.bluedart.com/Ver1.9/Demo/' + request_url
        try:
            client_obj = Client(api_url)
        except Exception as e:
            raise UserError("%s" % str(e))
        request_data = {
            'profile':{
                'Api_type' : 'S',
                'LicenceKey' : self.bd_licence_key,
                'LoginID' :self.bd_user_name,
                'Version' : '1.9',
            }
        }
        return client_obj, request_data
