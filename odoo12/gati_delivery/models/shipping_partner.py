import base64
import json
import requests
from odoo import tools
from zeep import Client
from odoo import models, fields, api,_
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('gati_ts', 'Gati')])
    gati_customer_code = fields.Char("Customer Code", help="8 Digit customer code provided by Gati (Can use the code as '87654321' for testing pur-pose)", copy=False)
    gati_token = fields.Char("Token (16 digit)", copy=False)

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'gati_ts':
            image_path = get_module_resource('gati_delivery', 'static/description', 'icon.png')
            self.image = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        return res

    @api.one
    def gati_test_connection(self):
        response = self._gati_send_request('GKEPincodeserviceablity.jsp', request_data={}, prod_environment=True,
                                           params={'reqid':self.gati_token,'pincode': '360004'}, method="POST")
        if response.get('result') == 'successful':
            raise UserError("Test Connection Succeeded")
        else:
            raise UserError("Something went wrong.\nError Message: {}".format(response.get('errmsg')))

    @api.model
    def _gati_send_request(self, request_url, request_data, prod_environment=True, params={}, method='GET'):
        headers = {
            'Content-Type': 'application/json',
            'token': self.gati_token,
        }
        data = json.dumps(request_data)
        if prod_environment:
            api_url = "https://justi.gati.com/webservices/" + request_url
        else:
            api_url = "http://119.235.57.47:9080/pickupservices/" + request_url
        try:
            req = requests.request(method, api_url, headers=headers, params=params, data=data)
            req.raise_for_status()
            if isinstance(req.content, bytes):
                req = req.content.decode("utf-8")
                response = json.loads(req, strict=False)
            else:
                response = json.loads(req.content)
        except requests.HTTPError as e:
            raise Warning("%s" % req.text)
        return response

    def generate_docket_or_packet_number(self):
        view_id = self.env.ref('gati_delivery.view_generate_docket_packet_number_form').id
        return {'type': 'ir.actions.act_window',
                'name': _('Generate Docket/Packet Number'),
                'res_model': 'generate.docket.packet.number',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [[view_id, 'form']],
                }

    def action_view_docket_numbers(self):
        self.ensure_one()
        action = self.env.ref('gati_delivery.action_gati_docket_package_number_view').read()[0]
        action['domain'] = [('type', '=', 'docket')]
        return action

    def action_view_packet_numbers(self):
        self.ensure_one()
        action = self.env.ref('gati_delivery.action_gati_docket_package_number_view').read()[0]
        action['domain'] = [('type', '=', 'packet')]
        return action