import time
import base64
import csv
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import Warning

from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class active_product_listing_report_ept(models.Model):
    _name = "active.product.listing.report.ept"
    _inherits = {"report.request.history": 'report_history_id'}
    _description = "Active Product"
    _inherit = ['mail.thread']
    _order = 'id desc'

    instance_id = fields.Many2one('amazon.instance.ept', string='Instance')
    report_id = fields.Char('Report ID', readonly='1')
    report_request_id = fields.Char('Report Request ID', readonly='1')

    name = fields.Char(size=256, string='Name')
    attachment_id = fields.Many2one('ir.attachment', string='Attachment')
    report_history_id = fields.Many2one('report.request.history', string='Report', required=True,
                                        ondelete="cascade", index=True, auto_join=True)

    update_price_in_pricelist = fields.Boolean(string='Update price in pricelist?', default=False,
                                               help='Update or create product line in pricelist if ticked.')
    auto_create_product = fields.Boolean(string='Auto create product?', default=False,
                                         help='Create product in ERP if not found.')
    log_count = fields.Integer(compute="get_log_count", string="Log Count",
                               help="Count number of created Stock Move")

    def get_log_count(self):
        """
        Find all stock moves associated with this report
        :return:
        """
        log_obj = self.env['amazon.transaction.log']
        model_id = self.env['ir.model']._get('active.product.listing.report.ept').id
        self.log_count = log_obj.search_count([('res_id', '=', self.id), ('model_id', '=', model_id)])

    @api.model
    def create(self, vals):
        try:
            sequence = self.env.ref('amazon_ept.seq_active_product_list')
            if sequence:
                report_name = sequence.next_by_id()
            else:
                report_name = '/'
        except:
            report_name = '/'
        vals.update({'name': report_name})
        return super(active_product_listing_report_ept, self).create(vals)

    @api.multi
    def unlink(self):
        for report in self:
            if report.state == 'processed':
                raise Warning(_('You cannot delete processed report.'))
        return super(active_product_listing_report_ept, self).unlink()

    @api.model
    def default_get(self, fields):
        res = super(active_product_listing_report_ept, self).default_get(fields)
        if not fields:
            return res
        res.update({'report_type': '_GET_MERCHANT_LISTINGS_DATA_',
                    })
        return res

    @api.multi
    def request_report(self):
        instance = self.instance_id
        seller = self.instance_id.seller_id
        report_type = self.report_type

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        if not seller:
            raise Warning('Please select instance')

        proxy_data = seller.get_proxy_server()
        marketplace_ids = tuple([instance.market_place_id])
        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'request_report',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'report_type': report_type,
                  'marketplace_ids': marketplace_ids,
                  'start_date': None,
                  'end_date': None,
                  }
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            result = response.get('result')
            self.update_report_history(result)

        return True

    @api.model
    def update_report_history(self, request_result):
        report_info = request_result.get('ReportInfo', {})
        report_request_info = request_result.get('ReportRequestInfo', {})
        request_id = report_state = report_id = False
        if report_request_info:
            request_id = str(report_request_info.get('ReportRequestId', {}).get('value', ''))
            report_state = report_request_info.get('ReportProcessingStatus', {}).get('value',
                                                                                     '_SUBMITTED_')
            report_id = report_request_info.get('GeneratedReportId', {}).get('value', False)
        elif report_info:
            report_id = report_info.get('ReportId', {}).get('value', False)
            request_id = report_info.get('ReportRequestId', {}).get('value', False)

        if report_state == '_DONE_' and not report_id:
            self.get_report_list()
        vals = {}
        if not self.report_request_id and request_id:
            vals.update({'report_request_id': request_id})
        if report_state:
            vals.update({'state': report_state})
        if report_id:
            vals.update({'report_id': report_id})
        self.write(vals)
        return True

    @api.multi
    def get_report_list(self):
        self.ensure_one()
        seller = self.instance_id.seller_id
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        if not seller:
            raise Warning('Please select seller')

        proxy_data = seller.get_proxy_server()
        if not self.request_id:
            return True

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'get_report_list',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'request_ids': [self.request_id],
                  }
        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            list_of_wrapper = response.get('result')

        for result in list_of_wrapper:
            self.update_report_history(result)

        return True

    @api.multi
    def get_report_request_list(self):
        self.ensure_one()
        seller = self.instance_id.seller_id

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        if not seller:
            raise Warning('Please select Seller')

        proxy_data = seller.get_proxy_server()

        if not self.report_request_id:
            return True

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'get_report_request_list',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'request_ids': (self.report_request_id,),
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            list_of_wrapper = response.get('result')

        for result in list_of_wrapper:
            self.update_report_history(result)

        return True

    @api.multi
    def get_report(self):
        self.ensure_one()
        seller = self.instance_id.seller_id
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        if not seller:
            raise Warning('Please select seller')

        proxy_data = seller.get_proxy_server()

        if not self.report_id:
            return True

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'get_report',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'report_id': self.report_id,
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            result = response.get('result')

        result = result.encode()
        result = base64.b64encode(result)
        file_name = "Active_Product_List_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': result,
            'datas_fname': file_name,
            'res_model': 'mail.compose.message',
            'type': 'binary'
        })
        self.message_post(body=_("<b>Active Product Report Downloaded</b>"),
                          attachment_ids=attachment.ids)
        self.write({'attachment_id': attachment.id})

        return True

    @api.multi
    def download_report(self):
        self.ensure_one()
        if self.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (self.attachment_id.id),
                'target': 'self',
            }
        return True

    def get_fulfillment_type(self, fulfillment_channel):
        if fulfillment_channel and fulfillment_channel == 'DEFAULT':
            return 'MFN'
        else:
            return 'AFN'

    @api.multi
    def reprocess_sync_products(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_obj.get_model_id('active.product.listing.report.ept')
        records = amazon_transaction_obj.search(
            [('model_id', '=', model_id), ('action_type', '!=', 'create'),
             ('res_id', '=', self.id)])
        records.unlink()
        self.sync_products()

    def update_pricelist_items(self, product_id, price):
        """
            @author : Harnisha Patel
            @last_updated_on : 5/10/2019
            The below method creates or updates the price of a product in the pricelist.
            """
        pricelist_item_obj = self.env['product.pricelist.item']
        if self.instance_id.pricelist_id and self.update_price_in_pricelist:
            item = self.instance_id.pricelist_id.item_ids.filtered(
                lambda i: i.product_id.id == product_id)
            if item and not item.fixed_price == float(price):
                item.fixed_price = price
            if not item:
                pricelist_item_obj.create({'product_id': product_id,
                                           'min_quantity': 1,
                                           'fixed_price': price,
                                           'pricelist_id': self.instance_id.pricelist_id.id})
        return True
    @api.multi
    def sync_products(self):
        self.ensure_one()
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")
        if not self.instance_id:
            raise Warning("Instance not found ")
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        reader = csv.DictReader(imp_file, delimiter='\t')
        amazon_product_ept_obj = self.env['amazon.product.ept']
        product_obj = self.env['product.product']
        log_book_obj = self.env['amazon.process.log.book']
        transaction_log_obj = self.env['amazon.transaction.log']
        model_id = transaction_log_obj.get_model_id('active.product.listing.report.ept')
        transaction_vals = {}
        log_rec = False
        for row in reader:
            if 'fulfilment-channel' in row.keys():
                fulfillment_type = self.get_fulfillment_type(row.get('fulfilment-channel', ''))
            else:
                fulfillment_type = self.get_fulfillment_type(row.get('fulfillment-channel', ''))
            if fulfillment_type:
                record = amazon_product_ept_obj.search_amazon_product(self.instance_id.id,
                                                                      row.get('seller-sku', ''),
                                                                      fulfillment_by=fulfillment_type)
                if record:
                    description = row.get('item-description', '') and row.get('item-description')

                    title = row.get('item-name', '') and row.get('item-name')
                    record.write({
                        'title': title,
                        'long_description': description,
                        'seller_sku': row.get('seller-sku', ''),
                        'fulfillment_by': fulfillment_type,
                        'product_asin': row.get('asin1'),
                        'exported_to_amazon': True,
                    })
                    self.update_pricelist_items(record.product_id.id,float(row.get('price')))
                else:
                    product_record = product_obj.search(
                        [('default_code', '=', row.get('seller-sku', ''))])
                    not_found_msg = """Multiple product found for same sku %s in ERP """ % (
                        row.get('seller-sku', ''))
                    if len(product_record.ids) > 1:
                        if not log_rec:
                            log_vals = {
                                'application': 'sync_products',
                                'instance_id': self.instance_id.id,
                                'operation_type': 'import',
                            }
                            log_rec = log_book_obj.create(log_vals)

                        transaction_vals = {'model_id': model_id,
                                            'res_id': self.id,
                                            'log_type': 'not_found',
                                            'action_type': 'skip_line',
                                            'message': not_found_msg,
                                            'job_id': log_rec.id, }
                        transaction_log_obj.create(transaction_vals)
                        continue
                    if product_record:
                        description = row.get('item-description', '') and row.get(
                            'item-description')
                        title = row.get('item-name', '') and row.get('item-name')
                        amazon_product_ept_obj.create({
                            'product_id': product_record.id,
                            'instance_id': self.instance_id.id,
                            'title': title,
                            'long_description': description,
                            'product_asin': row.get('asin1'),
                            'seller_sku': row.get('seller-sku', ''),
                            'fulfillment_by': fulfillment_type,
                            'exported_to_amazon': True
                        })
                        self.update_pricelist_items(product_record.id,float(row.get('price')))
                    else:
                        if self.auto_create_product:
                            description = row.get('item-description', '') and row.get('item-description')
                            title = row.get('item-name', '') and row.get('item-name')
                            created_product = product_record.create({'default_code': row.get('seller-sku', ''),
                                                                     'name': row.get('item-name'),
                                                                     'type': 'product'})
                            amazon_product_ept_obj.create({
                                'product_id': created_product.id,
                                'instance_id': self.instance_id.id,
                                'title': title,
                                'long_description': description,
                                'product_asin': row.get('asin1'),
                                'seller_sku': row.get('seller-sku', ''),
                                'fulfillment_by': fulfillment_type,
                                'exported_to_amazon': True
                            })
                            product_created_msg = """ Product created for seller sku %s || Instance %s """ % (
                                row.get('seller-sku', ''), self.instance_id.name)
                            if not log_rec:
                                log_vals = {
                                    'application': 'sync_products',
                                    'instance_id': self.instance_id.id,
                                    'operation_type': 'import',
                                }
                                log_rec = log_book_obj.create(log_vals)
                            transaction_vals = {
                                'product_id': created_product.id,
                                'default_code': row.get('seller-sku', ''),
                                'message': product_created_msg,
                                'log_line_id': log_rec.id,
                            }
                            transaction_log_obj.create(transaction_vals)
                            if self.update_price_in_pricelist:
                                self.update_pricelist_items(created_product.id,float(row.get('price')))
                        else:
                            not_found_msg = """ Line Skipped due to product not found seller sku %s || 
                            Instance %s """ % (row.get('seller-sku', ''), self.instance_id.name)
                            if not log_rec:
                                log_vals = {
                                    'application': 'sync_products',
                                    'instance_id': self.instance_id.id,
                                    'operation_type': 'import',
                                }
                                log_rec = log_book_obj.create(log_vals)
                            transaction_vals = {
                                'model_id': model_id,
                                'res_id': self.id,
                                'log_type': 'not_found',
                                'action_type': 'skip_line',
                                'message': not_found_msg,
                                'job_id': log_rec.id,
                            }
                            transaction_log_obj.create(transaction_vals)
                            continue
        self.write({'state': 'processed'})
        return True

    def list_of_process_logs(self):
        """
            List Of Logs View
            :return:
            """
        model_id = self.env['ir.model']._get('active.product.listing.report.ept').id
        action = {
            'domain': "[('res_id', '=', " + str(self.id) + " ),('model_id','='," + str(model_id) + ")]",
            'name': 'Active Product Report',
            'view_mode': 'tree,form',
            'res_model': 'amazon.transaction.log',
            'type': 'ir.actions.act_window',
        }
        return action
