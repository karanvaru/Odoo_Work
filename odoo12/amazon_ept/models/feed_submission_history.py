import time
from odoo import models, fields, api
from odoo.exceptions import Warning
#from . import dicttoxml.dicttoxml
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class feed_submission_history(models.Model):
    _name = "feed.submission.history"
    _description = 'feed.submission.history'
    _rec_name = 'feed_result_id'
    _order = 'feed_submit_date desc'

    feed_result_id = fields.Char(size=256, string='Feed Result ID')
    feed_result = fields.Text('Feed Result')
    message = fields.Text('Message')
    feed_submit_date = fields.Datetime('Feed Submit Date')
    feed_result_date = fields.Datetime('Feed Result Date')
    instance_id = fields.Many2one('amazon.instance.ept', string='Instance', copy=False)
    user_id = fields.Many2one('res.users', string="Requested User")
    seller_id=fields.Many2one('amazon.seller.ept',string="Seller",copy=False)
    @api.multi
    def get_feed_submission_result(self):
        amazon_process_log_obj = self.env['amazon.process.log.book']
        instance = self.instance_id
        feed_submission_id = self.feed_result_id
        if not instance or not feed_submission_id:
            raise Warning('You must need to first set Instance and feed submission ID.')

        proxy_data = instance.seller_id.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')        
        merchant_id=instance.merchant_id or self.seller_id.merchant_id or False
        auth_token=instance.auth_token or self.seller_id.auth_token or False
        kwargs = {'merchant_id':merchant_id,
                  'auth_token':auth_token,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'get_feed_submission_result',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                instance.country_id.code,
                  'proxies':proxy_data,
                  'feed_submission_id': feed_submission_id,}

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            job = amazon_process_log_obj.search([('request_feed_id', '=', feed_submission_id)],
                                                order="id desc", limit=1)
            if job:
                job.write({'message': str(response.get('reason'))})
            else:            
                raise Warning(response.get('reason'))
        else:
            result = response.get('result')
#            result=dicttoxml(result)
            self.write(
                {'feed_result': result, 'feed_result_date': time.strftime("%Y-%m-%d %H:%M:%S")})
        return True
