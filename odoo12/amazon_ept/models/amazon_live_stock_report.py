import time
from datetime import datetime, timedelta
import base64
import csv
from io import StringIO
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class amazon_live_stock_report_ept(models.Model):
    _name = "amazon.fba.live.stock.report.ept"
    _inherits = {"report.request.history": 'report_history_id'}
    _description = "Amazon Live Stock Report"
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.model
    def create(self, vals):
        try:
            sequence = self.env.ref('amazon_ept.seq_import_live_stock_report_job')
            if sequence:
                report_name = sequence.next_by_id()
            else:
                report_name = '/'
        except:
            report_name = '/'
        vals.update({'name': report_name})
        return super(amazon_live_stock_report_ept, self).create(vals)

    name = fields.Char(size=256, string='Name')
    report_history_id = fields.Many2one('report.request.history', string='Report', required=True,
                                        ondelete="cascade", index=True, auto_join=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('_SUBMITTED_', 'SUBMITTED'), ('_IN_PROGRESS_', 'IN_PROGRESS'),
         ('_CANCELLED_', 'CANCELLED'), ('_DONE_', 'DONE'),
         ('_DONE_NO_DATA_', 'DONE_NO_DATA'), ('processed', 'PROCESSED')
         ],
        string='Report Status', default='draft')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    auto_generated = fields.Boolean('Auto Generated Record ?', default=False)
    report_date = fields.Date('Report Date')
    log_count = fields.Integer(compute="get_log_count", string="Log Count")
    inventory_ids = fields.One2many('stock.inventory', 'fba_live_stock_report_id',
                                    string='Inventory')
    amz_instance_id = fields.Many2one('amazon.instance.ept', string="Instance")
    is_pan_european = fields.Boolean(string='Is Pan European', related="seller_id.is_pan_european",
                                     readonly=True)

    @api.one
    def get_log_count(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('amazon.fba.live.stock.report.ept')
        records = amazon_transaction_log_obj.search(
            [('model_id', '=', model_id), ('res_id', '=', self.id)])
        self.log_count = len(records.ids)

    @api.multi
    def list_of_inventory(self):
        action = {
            'domain': "[('id', 'in', " + str(self.inventory_ids.ids) + " )]",
            'name': 'FBA Live Stock Inventory',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.inventory',
            'type': 'ir.actions.act_window',
        }
        return action

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

    """Modification done by Twinkal [30-07-2019] as cron transfered according to seller wise"""

    @api.model
    def auto_import_amazon_fba_live_stock_report(self, args={}):
        seller_id = args.get('seller_id', False)
        seller = self.env['amazon.seller.ept'].browse(seller_id)
        if seller:
            if seller.inventory_report_last_sync_on:
                start_date = seller.inventory_report_last_sync_on
                start_date = datetime.strftime(start_date, '%Y-%m-%d %H:%M:%S')
                start_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
                start_date = start_date + timedelta(days=seller.live_inv_adjustment_report_days * -1 or -3)

            else:
                start_date = datetime.now() and datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_end = datetime.now()
            date_end = date_end.strftime("%Y-%m-%d %H:%M:%S")

            if seller.is_another_soft_create_fba_inventory:
                vals = {'start_date': start_date,
                        'end_date': date_end,
                        'seller_id': seller
                        }
                if not seller.is_pan_european:
                    vals.update({'instance_ids': seller.instance_ids})
                self.with_context(is_auto_process=True).get_inventory_report(vals)
            elif seller.is_pan_european:
                fba_live_stock_report = self.create(
                    {'seller_id': seller.id, 'report_date': datetime.now()})
                fba_live_stock_report.request_report()
            else:
                instance_ids = seller.instance_ids
                for instance in instance_ids:
                    fba_live_stock_report = self.create(
                        {'seller_id': seller.id, 'report_date': datetime.now(), 'amz_instance_id': instance.id})
                    fba_live_stock_report.request_report()
        return True

    """added  by Twinkal [31-07-2019] as the report type of inventory is changed.
       So in repsonse file we get different headers."""

    @api.multi
    def set_fulfillment_channel_sku(self):
        self.ensure_one()
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")

        amazon_product_ept_obj = self.env['amazon.product.ept']

        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        reader = csv.DictReader(imp_file, delimiter='\t')

        for row in reader:
            seller_sku = row.get('sku', False)
            fulfillment_channel_sku = row.get('fnsku', False)

            amazon_product = amazon_product_ept_obj.search(
                [('seller_sku', '=', seller_sku), ('fulfillment_by', '=', 'AFN')])
            for product in amazon_product:
                if product:
                    if not product.fulfillment_channel_sku:
                        product.update({'fulfillment_channel_sku': fulfillment_channel_sku})
        return True

    """Modification done by Twinkal [31-07-2019] as cron is transfered according to seller wise"""

    @api.model
    def auto_process_amazon_fba_live_stock_report(self, args={}):
        seller_id = args.get('seller_id', False)
        seller = self.env['amazon.seller.ept'].browse(seller_id)
        if seller:
            fba_live_stock_report = self.search([('seller_id', '=', seller.id),
                                                 ('state', 'in', ['_SUBMITTED_', '_IN_PROGRESS_']),
                                                 ])
            fba_live_stock_report.get_report_request_list_via_cron(seller)

            reports = self.search([('seller_id', '=', seller.id),
                                   ('state', '=', '_DONE_'),
                                   ('report_id', '!=', False)
                                   ])
            for report in reports:
                report.get_report()
                report.set_fulfillment_channel_sku()
                report.process_fba_live_stock_report()
                self._cr.commit()
        return True

    @api.multi
    def list_of_logs(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('amazon.fba.live.stock.report.ept')
        records = amazon_transaction_log_obj.search(
            [('model_id', '=', model_id), ('res_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(records.ids) + " )]",
            'name': 'Feed Logs',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'amazon.transaction.log',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.model
    def create_log(self, message, model_id, job, report_id, missing_value='', log_type='not_found'):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        amazon_transaction_log_obj.create({
            'model_id': model_id,
            'message': message,
            'res_id': report_id,
            'operation_type': 'import',
            'job_id': job.id,
            'skip_record': True,
            'log_type': log_type,
            'not_found_value': missing_value or '',
            'action_type': 'skip_line',
        })

    """Method added by Dhruvi [24-04-2019]
    This method is used to prepare sellable product qty dict and unsellable product qty dict
    as per the instance selected in report.This qty will be passed to create stock inventory adjustement report."""

    @api.multi
    def fill_dictionary_from_file_by_instance(self, reader, job, report_id):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        amazon_instnace_obj = self.env['amazon.instance.ept']
        amazon_product_obj = self.env['amazon.product.ept']

        model_id = amazon_transaction_log_obj.get_model_id('amazon.fba.live.stock.report.ept')
        sellable_line_dict = {}
        unsellable_line_dict = {}
        instance_ids = amazon_instnace_obj.search([('seller_id', '=', self.seller_id.id)]).ids
        for row in reader:
            seller_sku = row.get('sku') or row.get('seller-sku')
            afn_listing = row.get('afn-listing-exists')
            odoo_product = False
            if afn_listing == '':
                continue
            if not seller_sku:
                continue
            if self.amz_instance_id:
                domain = [('seller_sku', '=', seller_sku), ('instance_id', '=', self.amz_instance_id.id)]
            else:
                domain = [('seller_sku', '=', seller_sku), ('instance_id', 'in', instance_ids)]

            amazon_product = amazon_product_obj.search(domain, limit=1)
            if not amazon_product:
                product_asin = row.get('asin')
                if self.amz_instance_id:
                    domain = [('product_asin', '=', product_asin), ('instance_id', '=', self.amz_instance_id.id)]
                else:
                    domain = [('product_asin', '=', product_asin), ('instance_id', 'in', instance_ids)]
                amazon_product = amazon_product_obj.search(domain, limit=1)
                if not amazon_product:
                    message = "Product not found for seller sku %s" % (seller_sku)
                    if not amazon_transaction_log_obj.search(
                            [('message', '=', message), ('manually_processed', '=', False)]):
                        self.create_log(message, model_id, job, report_id, missing_value=seller_sku)
                    continue

            if amazon_product:
                odoo_product = amazon_product.product_id
                sellable_qty = sellable_line_dict.get(odoo_product, 0.0)
                if self.seller_id.is_reserved_qty_included_inventory_report:
                    sellable_line_dict.update(
                        {odoo_product: sellable_qty + float(row.get('afn-fulfillable-quantity', 0.0)) + float(
                            row.get('afn-reserved-quantity', 0.0))})
                else:
                    sellable_line_dict.update(
                        {odoo_product: sellable_qty + float(row.get('afn-fulfillable-quantity', 0.0))})

                unsellable_qty = unsellable_line_dict.get(odoo_product, 0.0)
                unsellable_line_dict.update(
                    {odoo_product: unsellable_qty + float(row.get('afn-unsellable-quantity', 0.0))})
        return sellable_line_dict, unsellable_line_dict

    @api.multi
    def process_fba_live_stock_report(self):
        self.ensure_one()
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        reader = csv.DictReader(imp_file, delimiter='\t')
        amazon_process_job_log_obj = self.env['amazon.process.log.book']
        inventory_obj = self.env['stock.inventory']
        job = amazon_process_job_log_obj.create({'application': 'stock_report',
                                                 'operation_type': 'import'})  # ,'seller_id':self.seller_id and self.seller_id.id or False})

        # Condition added by Twinkal [31-07-2019] to create inventory adjustement record as per instance selected.
        if self.amz_instance_id:
            sellable_line_dict, unsellable_line_dict = self.fill_dictionary_from_file_by_instance(reader, job,
                                                                                                  self.id)

        else:
            sellable_line_dict, unsellable_line_dict = self.fill_dictionary_from_file_by_instance(reader, job,
                                                                                                  self.id)
        if self.amz_instance_id:
            warehouse = self.amz_instance_id.fba_warehouse_id
        else:
            warehouse = self.seller_id.warehouse_ids and self.seller_id.warehouse_ids[0] or False
        if warehouse:
            inventory_obj.create_stock_inventory_from_amazon_live_report(sellable_line_dict,
                                                                         unsellable_line_dict,
                                                                         warehouse, self.id,
                                                                         seller=self.seller_id,
                                                                         job=job)  # inv_mismatch_details_sellable_list,inv_mismatch_details_unsellable_list,
        self.write({'state': 'processed'})

    @api.model
    def default_get(self, fields):
        res = super(amazon_live_stock_report_ept, self).default_get(fields)
        if not fields:
            return res
        #         res.update({'report_type': '_GET_AFN_INVENTORY_DATA_',})
        res.update({'report_type': '_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA_'})
        return res

    @api.multi
    def request_report(self):
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        seller, report_type, start_date, end_date = self.seller_id, self.report_type, self.start_date, self.end_date
        if not seller:
            raise Warning('Please select Seller')

        if start_date:
            db_import_time = time.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
            start_date = str(start_date) + 'Z'
        else:
            today = datetime.now()
            earlier = today - timedelta(days=30)
            earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
            start_date = earlier_str + 'Z'

        if end_date:
            db_import_time = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
            end_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
            end_date = str(end_date) + 'Z'
        else:
            today = datetime.now()
            earlier_str = today.strftime("%Y-%m-%dT%H:%M:%S")
            end_date = earlier_str + 'Z'
        proxy_data = seller.get_proxy_server()

        if self.amz_instance_id:
            marketplaceids = self.amz_instance_id.mapped('market_place_id')
        else:
            instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])

            marketplaceids = tuple(map(lambda x: x.market_place_id, instances))

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
                  'marketplace_ids': marketplaceids,
                  'start_date': start_date,
                  'end_date': end_date,
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
            self.get_report_request_list()
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
    def get_report_request_list(self):
        self.ensure_one()
        seller = self.seller_id
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
                  'request_ids': (self.report_request_id,)}

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            list_of_wrapper = response.get('result')

        for result in list_of_wrapper:
            self.update_report_history(result)

        return True

    @api.model
    def update_report_history_via_cron(self, request_result, report_info_records):
        report_info = request_result.get('ReportInfo', {})
        if isinstance(request_result.get('ReportInfo', []), list):
            report_info = request_result.get('ReportInfo', [])
        else:
            report_info.append(request_result.get('ReportInfo', {}))
        report_request_info = []
        if isinstance(request_result.get('ReportRequestInfo', []), list):
            report_request_info = request_result.get('ReportRequestInfo', [])
        else:
            report_request_info.append(request_result.get('ReportRequestInfo', {}))
        for info in report_request_info:
            request_id = str(info.get('ReportRequestId', {}).get('value', ''))
            report_state = info.get('ReportProcessingStatus', {}).get('value', '_SUBMITTED_')
            report_id = info.get('GeneratedReportId', {}).get('value', False)
            report_record = report_info_records.get(request_id)
            vals = {}
            if report_state:
                vals.update({'state': report_state})
            if report_id:
                vals.update({'report_id': report_id})
            report_record and report_record.write(vals)
        return True

    @api.multi
    def get_report_request_list_via_cron(self, seller):
        if not seller:
            raise Warning('Please select Seller')
        proxy_data = seller.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        request_ids = [report.report_request_id for report in self]
        report_info_records = {report.report_request_id: report for report in self}
        if not request_ids:
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
                  'request_ids': request_ids, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            list_of_wrapper = response.get('result')

        for result in list_of_wrapper:
            self.update_report_history_via_cron(result, report_info_records)

        return True

    @api.multi
    def get_report(self):
        self.ensure_one()
        seller = self.seller_id
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
        file_name = "Fba_Live_report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': result,
            'datas_fname': file_name,
            'res_model': 'mail.compose.message',
            'type': 'binary'
        })
        self.message_post(body=_("<b>Live Inventory Report Downloaded</b>"),
                          attachment_ids=attachment.ids)
        self.write({'attachment_id': attachment.id})

        return True

    @api.multi
    def get_inventory_report(self, vals):
        instance_obj = self.env['amazon.instance.ept']
        inv_report_ids = []

        start_date = vals.get('start_date')
        end_date = vals.get('end_date')
        seller_id = vals.get('seller_id')

        db_import_time = time.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
        db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
        start_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
            time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))

        db_import_time = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")
        db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
        end_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
            time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))

        if seller_id.is_pan_european:
            inventory_report = self.env['amazon.fba.live.stock.report.ept'].create(
                {'report_type': '_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA_',
                 'seller_id': seller_id.id,
                 'start_date': start_date,
                 'end_date': end_date,
                 'state': 'draft',
                 })

            inventory_report.request_report()
            inv_report_ids.append(inventory_report.id)

        else:
            instance_ids = instance_obj.search([('seller_id', '=', seller_id.id)])
            inv_report_ids = self.get_live_inventory_report(instance_ids, inv_report_ids, start_date, end_date,
                                                            seller_id)

        if inv_report_ids:
            action = self.env.ref('amazon_ept.action_live_stock_report_ept', False)
            result = action and action.read()[0] or {}

            if len(inv_report_ids) > 1:
                result['domain'] = "[('id','in',[" + ','.join(map(str, inv_report_ids)) + "])]"
            else:
                res = self.env.ref('amazon_ept.amazon_live_stock_report_form_view_ept', False)
                result['views'] = [(res and res.id or False, 'form')]
                result['res_id'] = inv_report_ids and inv_report_ids[0] or False
            return result
        return True

    def get_live_inventory_report(self, instance_ids, inv_report_ids, start_date, end_date, seller_id):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        list_of_wrapper = []
        if seller_id.is_another_soft_create_fba_inventory:
            for instance in instance_ids:
                proxy_data = seller_id.get_proxy_server()
                account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
                dbuuid = self.env['ir.config_parameter'].sudo(
                ).get_param('database.uuid')

                kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                          'auth_token': instance.auth_token and str(instance.auth_token) or False,
                          'app_name': 'amazon_ept',
                          'account_token': account.account_token,
                          'emipro_api': 'get_shipping_or_inventory_report',
                          'dbuuid': dbuuid,
                          'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                                     instance.country_id.code,
                          'proxies': proxy_data,
                          'start_date': start_date,
                          'end_date': end_date,
                          'report_type': '_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA_', }

                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):
                    if self._context.get('is_auto_process'):
                        job_log_vals = {
                            'message': 'Amazon Inventory Report Process',
                            'application': 'other',
                            'operation_type': 'import',
                        }
                        job = amazon_log_book_obj.create(job_log_vals)

                        log_line_vals = {
                            'model_id': self.env['amazon.transaction.log'].get_model_id(
                                'amazon.fba.live.stock.report.ept'),
                            'log_type': 'error',
                            'skip_record': True,
                            'message': response.get('reason'),
                            'job_id': job.id
                        }
                        amazon_transaction_obj.create(log_line_vals)
                    else:
                        raise Warning(response.get('reason'))
                else:
                    list_of_wrapper = response.get('result')

                inventory_report_req_history_obj = self.env['amazon.fba.live.stock.report.ept']
                for result in list_of_wrapper:
                    report_exist = False
                    reports = []
                    if not isinstance(result.get('ReportRequestInfo', []), list):
                        reports.append(result.get('ReportRequestInfo', []))
                    else:
                        reports = result.get('ReportRequestInfo', [])
                        reports.reverse()
                    for report in reports:
                        start_date = report.get('StartDate', '').get('value', '')
                        end_date = report.get('EndDate', '').get('value', '')
                        submited_date = report.get('SubmittedDate', '').get('value', '')
                        report_id = report.get('GeneratedReportId', {}).get('value', '')
                        request_id = report.get('ReportRequestId', {}).get('value', '')
                        report_type = report.get('ReportType', {}).get('value', '')
                        state = report.get('ReportProcessingStatus', {}).get('value', '')
                        report_exist = inventory_report_req_history_obj.search(
                            ['|', ('report_request_id', '=', request_id),
                             ('report_id', '=', report_id), ('report_type', '=', report_type)])
                        if report_exist:
                            report_exist = report_exist[0]
                            inv_report_ids.append(report_exist.id)
                            continue

                        vals = {
                            'report_type': report_type,
                            'report_request_id': request_id,
                            'report_id': report_id,
                            'start_date': start_date,
                            'end_date': end_date,
                            'requested_date': submited_date,
                            'state': state,
                            'seller_id': instance.seller_id.id,
                            'amz_instance_id': instance.id,
                            'user_id': self._uid,
                        }
                        inv_report_id = inventory_report_req_history_obj.create(vals)
                        inv_report_ids.append(inv_report_id.id)
        else:
            inventory_report = self.env['amazon.fba.live.stock.report.ept'].create(
                {'report_type': '_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA_',
                 'seller_id': seller_id.id,
                 'start_date': self.start_date,
                 'end_date': self.end_date,
                 'state': 'draft',
                 })
            inv_report_ids.append(inventory_report.id)
            inventory_report.request_report()

        if inv_report_ids:
            seller_id.write({'inventory_report_last_sync_on': end_date})
        return inv_report_ids
