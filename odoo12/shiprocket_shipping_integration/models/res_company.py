# -*- coding: utf-8 -*-
from requests import request
import logging
import json
from odoo import fields, models, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = "res.company"
    shiprocket_username = fields.Char(string="Shiprocket Username", help="Username provided by shiprocket.",copy=False)
    shiprocket_password = fields.Char(string="Shiprocket Password", help="Password provided by shiprocket.")
    shiprocket_api_token = fields.Char(string="API Auth Token", help="Once you click on generate the auth button")
    shiprocket_api_url = fields.Char(copy=False,string='API URL', help="API URL, Redirect to this URL when calling the API.",default="https://apiv2.shiprocket.in/v1/external")
    use_shiprocket_shipping_provider = fields.Boolean(copy=False, string="Are You Use shiprocket.?",
                                                 help="If use shiprocket shipping Integration than value set TRUE.",
                                                 default=False)

    def auto_generate_authorization_shiprocket(self):
        company_ids = self.search([('use_shiprocket_shipping_provider', '=', True)])
        for company_id in company_ids:
            try:
                company_id.generate_shiprocket_api_auth()
            except Exception as e:
                continue

    def prepare_api_url(self, api_url):
        return "{0}{1}".format(self.shiprocket_api_url, api_url)

    def call_get_shiprocket_api(self, api_url=False):
        headers = {'Authorization': "Bearer {}".format(self.shiprocket_api_token),
                   'Content-Type': 'application / json',
                   'Accept': 'application/json'}
        url = self.prepare_api_url("{}".format(api_url))
        try:
            _logger.info("Send GET Request From odoo to Shiprocket: {0}".format(url))
            return request(method='GET', url=url, headers=headers)
        except Exception as e:
            _logger.info("Getting an Error in GET Req odoo to Shiprocket: {0}".format(e))
            return e

    def call_post_shiprocket_api(self, api_url=False, params=False):
        headers = {'Authorization': "Bearer {}".format(self.shiprocket_api_token),
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        url = self.prepare_api_url("{}".format(api_url))
        try:
            _logger.info("Send Post Request From odoo to Shiprocket: {0}".format(url))
            data = json.dumps(params)
            return request(method='POST', url=url, data=data, headers=headers)
        except Exception as e:
            _logger.info("Getting an Error in Post Req odoo to Shiprocket: {0}".format(e))
            return e

    def generate_shiprocket_api_auth(self):
        request_data = {"email": "{}".format(self.shiprocket_username),
                        "password": "{}".format(self.shiprocket_password)}
        response_data = self.call_post_shiprocket_api("/auth/login",request_data)
        if response_data.status_code in [200, 201]:
            response = response_data.json()
            if response.get('token'):
                self.shiprocket_api_token = response.get('token')
                return {'effect': {
                            'fadeout': 'slow',
                            'message': "Shiprocket API Auth Generated",
                            'img_url': '/web/static/src/img/smile.svg',
                            'type': 'rainbow_man'}}
            else:
                raise ValidationError(response)
        else:
            raise ValidationError("Error : {}".format(response_data.content))

    def import_all_channels_from_shiprocket_to_odoo(self):
        shiprocket_channels = self.env['shiprocket.channels']
        response_data = self.call_get_shiprocket_api("/channels")
        if response_data.status_code in [200, 201]:
            response = response_data.json()
            if response.get('data'):
                for chanel in response.get('data'):
                    if not shiprocket_channels.search([('chanel_code','=',chanel.get('id'))]):
                        shiprocket_channels.create({'chanel_status':chanel.get('status'),
                                                    'name':chanel.get('name'),
                                                    'chanel_code':chanel.get('id')})
                return {'effect': {
                    'fadeout': 'slow',
                    'message': "Shiprocket channels imported successfully!",
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man'}}
            else:
                raise ValidationError(response)
        else:
            raise ValidationError("Error : {}".format(response_data.content))
