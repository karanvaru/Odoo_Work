
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap
from odoo.http import request
import requests
import json
import logging
from ..endpoint import DEFAULT_ENDPOINT

_logger = logging.getLogger(__name__)



class amazon_seller_config(models.TransientModel):
    _name = 'res.config.amazon.seller'
    _description = 'res.config.amazon.seller'

    name = fields.Char("Seller Name")
    merchant_id = fields.Char("Merchant Id")
    country_id = fields.Many2one('res.country', string="Country")
    access_key = fields.Char("Access Key")
    secret_key = fields.Char("Secret Key")

    company_id = fields.Many2one('res.company', string='Company')
    developer_id = fields.Many2one('amazon.developer.details.ept', compute="set_developer_id",
                                   string="Developer ID", store=False)
    developer_name = fields.Char("Developer Name")

    auth_token = fields.Char("Auth Token")
    amazon_selling = fields.Selection([('FBA', 'FBA'),
                                       ('FBM', 'FBM'),
                                       ('Both', 'FBA & FBM')],
                                      'Fulfillment By ?', default='FBM')

    """
    Modified: updated code to create iap account if not exist and if exist iap account than
              verify to check if credit exist for that account than it will allow to create seller
              if credit not exist than it will raise popup to purchase credits for that account.
    """

    @api.multi
    def test_amazon_connection(self):
        """
        Create Seller account in ERP if not created before.
        If auth_token and merchant_id found in ERP then raise Warning.
        If Amazon Seller Account is registered in IAP raise Warning.
        IF Amazon Seller Account is not registered in IAP then create it.
        This function will load Marketplaces automatically based on seller region.
        :return:
        """

        amazon_seller_obj = self.env['amazon.seller.ept']
        seller_exist = amazon_seller_obj.search(
            [('auth_token', '=', self.auth_token),
             ('merchant_id', '=', self.merchant_id)
             ])
        account = self.env['iap.account'].search(
            [('service_name', '=', 'amazon_ept')])

        if seller_exist:
            raise Warning('Seller already exist with given Credential.')
        elif account:
            kwargs = self.prepare_marketplace_kwargs(account)
            response = iap.jsonrpc(
                DEFAULT_ENDPOINT + '/verify_iap', params=kwargs)
        else:
            account = self.env['iap.account'].create(
                {'service_name': 'amazon_ept'})
            account._cr.commit()
            kwargs = self.prepare_marketplace_kwargs(account)
            response = iap.jsonrpc(
                DEFAULT_ENDPOINT + '/register_iap', params=kwargs)

        if response.get('error', {}):
            raise Warning(response.get('error'))
        else:
            flag = response.get('result', {})
            if flag:
                company_id = self.company_id or self.env.user.company_id or False
                seller_values = self.prepare_amazon_seller_vals(company_id)
                try:
                    seller = amazon_seller_obj.create(seller_values)
                    seller.load_marketplace()
                    self.create_transaction_type(seller)
                except Exception as e:
                    raise Warning('Exception during instance creation.\n %s' % (str(e)))
                action = self.env.ref(
                    'amazon_ept.action_amazon_configuration', False)
                result = action and action.read()[0] or {}
                result.update({'seller_id': seller.id})
                if seller.amazon_selling in ['FBA', 'Both']:
                    self.update_reimbursement_details(seller)

        return True

    @api.multi
    def create_transaction_type(self, seller):
        trans_line_obj = self.env['amazon.transaction.line.ept']
        trans_type_ids = self.env['amazon.transaction.type'].search([])
        for trans_id in trans_type_ids:
            trans_line_vals = {
                'transaction_type_id': trans_id.id,
                'seller_id': seller.id,
                'amazon_code': trans_id.amazon_code,
            }
            trans_line_obj.create(trans_line_vals)

    def prepare_amazon_seller_vals(self, company_id):
        """
        Prepare Amazon Seller values
        :param company_id: res.company()
        :return: dict
        """
        return {
            'name': self.name,
            'country_id': self.country_id.id,
            'company_id': company_id.id,
            'amazon_selling': self.amazon_selling,
            'merchant_id': self.merchant_id,
            'auth_token': self.auth_token,
            'developer_id': self.developer_id.id,
            'developer_name': self.developer_name,
        }

    def prepare_marketplace_kwargs(self, account):
        """
        Prepare Arguments for Load Marketplace.
        :return: dict{}
        """
        ir_config_parameter_obj = self.env['ir.config_parameter']
        dbuuid = ir_config_parameter_obj.sudo().get_param('database.uuid')
        return {'merchant_id': self.merchant_id and str(self.merchant_id) or False,
                'auth_token': self.auth_token and str(self.auth_token) or False,
                'app_name': 'amazon_ept',
                'account_token': account.account_token,
                'emipro_api': 'test_amazon_connection',
                'dbuuid': dbuuid,
                'amazon_selling': self.amazon_selling,
                'amazon_marketplace_code': self.country_id.amazon_marketplace_code or self.country_id.code
                }

    @api.one
    def update_reimbursement_details(self, seller):
        prod_obj = self.env['product.product']
        partner_obj = self.env['res.partner']
        product = prod_obj.search(
            [('default_code', '=', 'REIMBURSEMENT'), ('type', '=', 'service')])

        vals = {'name': 'Amazon Reimbursement'}
        partner_id = partner_obj.create(vals)

        seller.write(
            {'reimbursement_customer_id': partner_id.id, 'reimbursement_product_id': product.id})
        return True

    @api.multi
    def set_developer_id(self):
        """
        change country id on change od developer id.
        :return:
        """
        self.onchange_country_id()

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id:
            developer_id = self.env['amazon.developer.details.ept'].search(
                [('developer_country_id', '=', self.country_id.id)])
            self.update({'developer_id': developer_id.id or False,
                         'developer_name': developer_id.developer_name or False})
