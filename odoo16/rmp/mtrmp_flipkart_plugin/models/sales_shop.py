# -*- coding: utf-8 -*-
from .. import flipkart
from odoo import models, fields, api
from ..flipkart import FlipkartAPI, Authentication


class SaleShopExtend(models.Model):
    _inherit = 'sale.shop'

    is_api_connection = fields.Boolean("Is API Connection?")
    flipkart_api_key = fields.Char("API Key")
    flipkart_secret_key = fields.Char("Secret Key")
    flipkart_access_token = fields.Char("Access Token")

    def connect_in_flipkart(self, vals=False):
        api_key = self.flipkart_api_key
        secret_key = self.flipkart_secret_key
        if vals and not api_key and not secret_key:
            api_key = vals.get("flipkart_api_key")
            secret_key = vals.get("flipkart_secret_key")

        auth = Authentication(api_key, secret_key, sandbox=False)
        if not self.flipkart_access_token:
            token = auth.get_token_from_client_credentials()
            if token and token['access_token']:
                self.flipkart_access_token = token['access_token']
                self._cr.commit()
        flipkart = FlipkartAPI(self.flipkart_access_token, sandbox=False, debug=True)
        return flipkart
