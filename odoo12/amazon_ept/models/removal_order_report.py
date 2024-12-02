from odoo import models, fields, api, _
from datetime import datetime, timedelta
import time
import base64
import csv
from io import StringIO
from odoo.exceptions import Warning
from odoo.tools.float_utils import float_round, float_compare
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class removal_order_report_history(models.Model):
    _name = "amazon.removal.order.report.history"
    _inherits = {"report.request.history": 'report_history_id'}
    _description = "Removal Order Report"
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.multi
    def get_removal_pickings(self):
        for record in self:
            record.removal_count = len(record.removal_picking_ids.ids)

    @api.multi
    def list_of_removal_pickings(self):
        action = {
            'domain': "[('id', 'in', " + str(self.removal_picking_ids.ids) + " )]",
            'name': 'Removal Order Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.one
    def get_log_count(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('amazon.removal.order.report.history')
        records = amazon_transaction_log_obj.search([('model_id', '=', model_id), ('res_id', '=', self.id)])
        self.log_count = len(records.ids)

    name = fields.Char(size=256, string='Name')
    report_history_id = fields.Many2one('report.request.history', string='Report', required=True, ondelete="cascade",
                                        index=True, auto_join=True)
    state = fields.Selection([('draft', 'Draft'), ('_SUBMITTED_', 'SUBMITTED'), ('_IN_PROGRESS_', 'IN_PROGRESS'),
                              ('_CANCELLED_', 'CANCELLED'), ('_DONE_', 'DONE'),
                              ('_DONE_NO_DATA_', 'DONE_NO_DATA'), ('processed', 'PROCESSED')
                              ],
                             string='Report Status', default='draft')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    auto_generated = fields.Boolean('Auto Generated Record ?', default=False)
    removal_picking_ids = fields.One2many("stock.picking", 'removal_order_report_id', string="Pickings")
    removal_count = fields.Integer("Removal Count", compute="get_removal_pickings")
    log_count = fields.Integer(compute="get_log_count", string="Log Count")

    @api.model
    def auto_import_removal_order_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            if seller.removal_order_report_last_sync_on:
                start_date = seller.removal_order_report_last_sync_on
            else:
                today = datetime.now()
                earlier = today - timedelta(days=30)
                start_date = earlier.strftime("%Y-%m-%d %H:%M:%S.%f")
            date_end = datetime.now()

            rem_report = self.create({'report_type': '_GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA_',
                                      'seller_id': seller_id,
                                      'start_date': start_date,
                                      'end_date': date_end,
                                      'state': 'draft',
                                      'requested_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                      'auto_generated': True,
                                      })
            rem_report.with_context(is_auto_process=True).request_report()
            seller.write({'removal_order_report_last_sync_on': date_end})
        return True

    @api.model
    def auto_process_removal_order_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            rem_reports = self.search([('seller_id', '=', seller.id),
                                       ('state', 'in', ['_SUBMITTED_', '_IN_PROGRESS_']),
                                       ('auto_generated', '=', True)
                                       ])
            for report in rem_reports:
                report.with_context(is_auto_process=True).get_report_request_list()
            rem_reports = self.search([('seller_id', '=', seller.id),
                                       ('state', '=', '_DONE_'),
                                       ('auto_generated', '=', True),
                                       ('report_id', '!=', False)
                                       ])
            for report in rem_reports:
                report.with_context(is_auto_process=True).get_report()
                report.process_removal_order_report()
                self._cr.commit()
        return True

    @api.multi
    def on_change_seller_id(self, seller_id, start_date, end_date):
        value = {}
        if seller_id:
            seller = self.env['amazon.seller.ept'].browse(seller_id)
            value.update({'start_date': seller.removal_order_report_last_sync_on, 'end_date': datetime.now()})
        return {'value': value}

    @api.multi
    def unlink(self):
        for report in self:
            if report.state == 'processed':
                raise Warning(_('You cannot delete processed report.'))
        return super(removal_order_report_history, self).unlink()

    @api.model
    def default_get(self, fields):
        res = super(removal_order_report_history, self).default_get(fields)
        if not fields:
            return res
        res.update({'report_type': '_GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA_',
                    })
        return res

    @api.model
    def create(self, vals):
        try:
            sequence = self.env.ref('amazon_ept.seq_removal_order_report_job')
            if sequence:
                report_name = sequence.next_by_id()
            else:
                report_name = '/'
        except:
            report_name = '/'
        vals.update({'name': report_name})
        return super(removal_order_report_history, self).create(vals)

    @api.multi
    def request_report(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        seller, report_type, start_date, end_date = self.seller_id, self.report_type, self.start_date, self.end_date
        if not seller:
            raise Warning('Please select instance')

        if start_date:
            if self._context.get('is_auto_process'):
                start_date = datetime.strptime(str(start_date), "%Y-%m-%d %H:%M:%S.%f")
                start_date = str(start_date.strftime("%Y-%m-%d %H:%M:%S"))
            db_import_time = time.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S",
                                       time.gmtime(time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
            start_date = str(start_date) + 'Z'
        else:
            today = datetime.now()
            earlier = today - timedelta(days=30)
            earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
            start_date = earlier_str + 'Z'

        if end_date:
            if self._context.get('is_auto_process'):
                end_date = datetime.strptime(str(end_date), "%Y-%m-%d %H:%M:%S.%f")
                end_date = str(end_date.strftime("%Y-%m-%d %H:%M:%S"))
            db_import_time = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
            end_date = time.strftime("%Y-%m-%dT%H:%M:%S",
                                     time.gmtime(time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
            end_date = str(end_date) + 'Z'
        else:
            today = datetime.now()
            earlier_str = today.strftime("%Y-%m-%dT%H:%M:%S")
            end_date = earlier_str + 'Z'

        proxy_data = seller.get_proxy_server()

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])

        marketplaceids = tuple([x.market_place_id for x in instances])
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

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Removal Order Report Process',
                    'application': 'removal_order',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'amazon.removal.order.report.history'),
                    'log_type': 'error',
                    'skip_record': True,
                    'message': response.get('reason'),
                    'job_id': job.id
                }
                amazon_transaction_obj.create(log_line_vals)
            else:
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
            report_state = report_request_info.get('ReportProcessingStatus', {}).get('value', '_SUBMITTED_')
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
    def get_report_request_list(self):
        self.ensure_one()
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        seller = self.seller_id
        if not seller:
            raise Warning('Please select Seller')

        proxy_data = seller.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

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
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Removal Order Report Process',
                    'application': 'removal_order',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'amazon.removal.order.report.history'),
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

        for result in list_of_wrapper:
            self.update_report_history(result)

        return True

    @api.multi
    def get_report_list(self):
        self.ensure_one()
        seller = self.seller_id
        if not seller:
            raise Warning('Please select seller')

        proxy_data = seller.get_proxy_server()
        if not self.request_id:
            return True

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'get_report_request_list',
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
    def get_report(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        self.ensure_one()
        seller = self.seller_id
        if not seller:
            raise Warning('Please select seller')

        proxy_data = seller.get_proxy_server()

        if not self.report_id:
            return True

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

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

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Removal Order Report Process',
                    'application': 'removal_order',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'amazon.removal.order.report.history'),
                    'log_type': 'error',
                    'skip_record': True,
                    'message': response.get('reason'),
                    'job_id': job.id
                }
                amazon_transaction_obj.create(log_line_vals)
            else:
                raise Warning(response.get('reason'))
        else:
            result = response.get('result')

        result = result.encode()
        result = base64.b64encode(result)
        file_name = "Removal_Order_Report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': result,
            'datas_fname': file_name,
            'res_model': 'mail.compose.message',
            'type': 'binary'
        })
        self.message_post(body=_("<b>Removal Order Report Downloaded</b>"), attachment_ids=attachment.ids)
        self.write({'attachment_id': attachment.id})
        seller.write({'removal_order_report_last_sync_on': datetime.now()})
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

    @api.multi
    def view_job(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('amazon.removal.order.report.history')
        logs = amazon_transaction_log_obj.search([('model_id', '=', model_id), ('res_id', '=', self.id)])
        jobs = list(set(list([x.job_id.id for x in logs])))
        action = {
            'domain': "[('id', 'in', " + str(jobs) + " )]",
            'name': 'Job',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'amazon.process.log.book',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.model
    def check_amazon_order_exist_order_not(self, order_ref):
        order = self.env['amazon.removal.order.ept'].search([('name', '=', order_ref)])
        return order

    @api.multi
    def get_amazon_product(self, sku, instance):
        amazon_product = self.env['amazon.product.ept'].search(
            [('seller_sku', '=', sku), ('instance_id', '=', instance.id), ('fulfillment_by', '=', 'AFN')], limit=1)
        return amazon_product

    @api.multi
    def create_order_if_not_found_in_odoo(self, reader, job, model_id):
        amazon_removal_order_obj = self.env['amazon.removal.order.ept']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        instance_obj = self.env['amazon.instance.ept']
        order_dict = {}
        for row in reader:
            if not row.get('order-type'):
                continue
            order_id = row.get('order-id')
            order_type = row.get('order-type')
            order_status = row.get('order-status')
            existing_order = self.check_amazon_order_exist_order_not(order_id)
            if not existing_order and order_status == 'Completed':
                if order_id in order_dict:
                    order_dict.get(order_id).append(row)
                else:
                    order_dict.update({order_id: [row]})
        for order_id, rows in list(order_dict.items()):
            instance = instance_obj.search(
                [('seller_id', '=', self.seller_id.id), ('is_global_warehouse_in_fba', '=', True)])
            if not instance:
                instance = instance_obj.search([('seller_id', '=', self.seller_id.id)], limit=1)
            lines = []
            for row in rows:
                vals = {}
                sku = row.get('sku')
                order_type = row.get('order-type')
                amazon_product = self.get_amazon_product(sku, instance)
                if not amazon_product:
                    message = "Line is skiped due to product not found in ERP || Order ref %s || Seller sku %s" % (
                        order_id, sku)
                    amazon_transaction_log_obj.create({
                        'model_id': model_id,
                        'message': message,
                        'operation_type': 'import',
                        'res_id': self.id,
                        'job_id': job.id
                    })
                    continue
                if float(row.get('requested-quantity', 0.0)) <= 0.0:
                    message = "Line is skiped due to request qty not found in file || Order ref %s || Seller sku %s" % (
                        order_id, sku)
                    amazon_transaction_log_obj.create({
                        'model_id': model_id,
                        'message': message,
                        'res_id': self.id,
                        'operation_type': 'import',
                        'job_id': job.id,
                    })
                    continue
                vals = {'amazon_product_id': amazon_product.id, 'removal_disposition': order_type}
                if row.get('disposition') == 'Unsellable':
                    vals.update({'unsellable_quantity': float(row.get('requested-quantity', 0.0))})
                else:
                    vals.update({'sellable_quantity': float(row.get('requested-quantity', 0.0))})
                lines.append((0, 0, vals))

            if lines:
                removal_order = amazon_removal_order_obj.create({
                    'name': order_id,
                    'removal_disposition': order_type,
                    'warehouse_id': instance and instance.removal_warehouse_id.id or False,
                    'ship_address_id': self.company_id.partner_id.id,
                    'company_id': self.seller_id.company_id.id,
                    'instance_id': instance.id,
                    'removal_order_lines_ids': lines

                })
                removal_order.write({'state': 'plan_approved'})
                if order_type == 'Disposal':
                    removal_order.disposal_order_pickings()
                if order_type == 'Return':
                    pickings = removal_order.removal_order_procurements()
                    pickings.write({'removal_order_report_id': self.id})
        return True

    @api.multi
    def process_removal_order_report(self):
        self.ensure_one()
        amazon_process_job_log_obj = self.env['amazon.process.log.book']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        amazon_removal_order_config_obj = self.env['removal.order.config.ept']
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")
        if not self.seller_id:
            raise Warning("Seller is not defind for processing report")
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        reader = csv.DictReader(imp_file, delimiter='\t')
        disposal_line_dict = {}
        return_line_dict = {}
        job = amazon_process_job_log_obj.create({
            'application': 'removal_order',
            'operation_type': 'import',
            #                                                'seller_id':self.seller_id.id
        })
        self.attachment_id.copy(
            default={'res_model': 'amazon.process.log.book', 'res_id': job.id, 'name': self.attachment_id.name,
                     'datas_fname': self.attachment_id.name})
        model_id = amazon_transaction_log_obj.get_model_id('amazon.removal.order.report.history')
        self.create_order_if_not_found_in_odoo(reader, job, model_id)
        imp_file.seek(0)
        for row in reader:
            if not row.get('order-type') or row.get('order-type') == 'order-type':
                continue
            order_id = row.get('order-id')
            order_type = row.get('order-type')
            order_status = row.get('order-status')
            sku = row.get('sku')
            disposition = row.get('disposition')
            requested_qty = row.get('requested-quantity')
            message = False
            existing_order = self.check_amazon_order_exist_order_not(order_id)
            if not existing_order:
                message = "Order not found for processing order-id %s" % (order_id)
                if not amazon_transaction_log_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    amazon_transaction_log_obj.create({
                        'model_id': model_id,
                        'message': message,
                        'operation_type': 'import',
                        'res_id': self.id,
                        'job_id': job.id,
                    })
                continue

            if len(existing_order.ids) > 1:
                message = "Multiple Order found for processing order-id %s" % (order_id)
                if not amazon_transaction_log_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    amazon_transaction_log_obj.create({
                        'model_id': model_id,
                        'message': message,
                        'res_id': self.id,
                        'operation_type': 'import',
                        'job_id': job.id,
                    })
                continue
            if existing_order.state == order_status:
                message = """Order %s  Already Processed ||| order-type %s |||
                           sku %s ||| disposition %s ||| requested-qty %s                
                """ % (order_id, order_type, sku, disposition, requested_qty)
                if not amazon_transaction_log_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    amazon_transaction_log_obj.create({
                        'model_id': model_id,
                        'message': message,
                        'res_id': self.id,
                        'operation_type': 'import',
                        'job_id': job.id,
                    })
                continue
            if order_status == 'Cancelled':
                for picking in existing_order.removal_order_picking_ids:
                    if picking.state not in ['done', 'cancel']:
                        picking.action_cancel()
                continue
            config = amazon_removal_order_config_obj.search(
                [('instance_id', '=', existing_order.instance_id.id), ('removal_disposition', '=', order_type)],
                limit=1)
            if not config:
                message = "Configuration not found for order-type %s order-id" % (order_type, order_id)
                if not amazon_transaction_log_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    amazon_transaction_log_obj.create({
                        'model_id': model_id,
                        'message': message,
                        'operation_type': 'import',
                        'res_id': self.id,
                        'job_id': job.id,
                    })
                continue
            key = (existing_order, config)
            if order_type == 'Disposal':
                if key in disposal_line_dict:
                    disposal_line_dict.get(key).append(row)
                else:
                    disposal_line_dict.update({key: [row]})
            elif order_type == 'Return':
                if key in return_line_dict:
                    return_line_dict.get(key).append(row)
                else:
                    return_line_dict.update({key: [row]})
            else:
                message = "Order type skiped %s" % (order_id)
                if not amazon_transaction_log_obj.search(
                        [('message', '=', message), ('manually_processed', '=', False)]):
                    amazon_transaction_log_obj.create({
                        'model_id': model_id,
                        'message': message,
                        'operation_type': 'import',
                        'res_id': self.id,
                        'job_id': job.id,
                    })
        if disposal_line_dict or return_line_dict:
            self.process_removal_lines(disposal_line_dict, return_line_dict, job, model_id)
        self.write({'state': 'processed'})
        if not job.transaction_log_ids:
            job.unlink()
        return True

    @api.multi
    def process_removal_lines(self, disposal_line_dict, return_line_dict, job, model_id):
        if disposal_line_dict:
            self.process_disposal_lines(disposal_line_dict, job, model_id)
        if return_line_dict:
            self.process_return_lines(return_line_dict, job, model_id)
        return True

    @api.multi
    def find_amazon_product_for_process_removal_line(self, line, job, instance, model_id):
        amazon_product_obj = self.env['amazon.product.ept']
        sku = line.get('sku')
        asin = line.get('fnsku')
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        amazon_product = amazon_product_obj.search(
            [('seller_sku', '=', sku), ('fulfillment_by', '=', 'AFN'), ('instance_id', '=', instance.id)], limit=1)
        if not amazon_product:
            amazon_product = amazon_product_obj.search(
                [('product_asin', '=', asin), ('fulfillment_by', '=', 'AFN'), ('instance_id', '=', instance.id)],
                limit=1)
        product = amazon_product and amazon_product.product_id or False
        if not amazon_product:
            amazon_transaction_log_obj.create({'message': 'Product  not found for SKU %s & ASIN %s' % (sku, asin),
                                               'model_id': model_id,
                                               'job_id': job.id,
                                               'log_type': 'not_found',
                                               'operation_type': 'import',
                                               'action_type': 'skip_line',
                                               'res_id': self.id
                                               })
        return product

    @api.multi
    def process_return_lines(self, return_line_dict, job, model_id):
        stock_move_obj = self.env['stock.move']
        stock_picking_obj = self.env['stock.picking']
        procurement_rule_obj = self.env['stock.rule']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']

        pickings = []
        for order_key, rows in list(return_line_dict.items()):
            order = order_key[0]
            config = order_key[1]

            picking_ids = order.removal_order_picking_ids.ids

            picking_ids = stock_picking_obj.search([('id', 'in', picking_ids), ('is_fba_wh_picking', '=', True)]).ids
            remaining_pickings = stock_picking_obj.search(
                [('id', 'in', picking_ids), ('state', 'not in', ['done', 'cancel'])])
            processed_pickings = stock_picking_obj.search([('id', 'in', picking_ids), ('state', '=', 'done')])
            procurement_rule = procurement_rule_obj.search([('route_id', '=', config.unsellable_route_id.id),
                                                            ('location_src_id', '=', order.disposition_location_id.id)])
            unsellable_source_location_id = procurement_rule.location_src_id.id
            unsellable_dest_location_id = procurement_rule.location_id.id
            procurement_rule = procurement_rule_obj.search([('route_id', '=', config.sellable_route_id.id), (
                'location_src_id', '=', order.instance_id.fba_warehouse_id.lot_stock_id.id)])
            sellable_source_location_id = procurement_rule.location_src_id.id
            sellable_dest_location_id = procurement_rule.location_id.id

            for row in rows:
                shipped_qty = float(row.get('shipped-quantity', 0.0))
                canceled_qty = float(row.get('cancelled-quantity', 0.0))
                sku = row.get('sku')
                disposition = row.get('disposition')
                order_ref = row.get('order-id')
                product = self.find_amazon_product_for_process_removal_line(row, job, order.instance_id, model_id)
                if not product:
                    continue
                if disposition == 'Unsellable':
                    source_location_id = unsellable_source_location_id
                    location_dest_id = unsellable_dest_location_id
                else:
                    source_location_id = sellable_source_location_id
                    location_dest_id = sellable_dest_location_id
                qty = shipped_qty
                if shipped_qty > 0.00:
                    if processed_pickings:
                        qty = self.check_move_processed_or_not(product.id, picking_ids, 'done', job, sku,
                                                               source_location_id, location_dest_id, model_id,
                                                               shipped_qty, order_ref)
                    if qty <= 0.0:
                        # continue
                        pass
                    moves = stock_move_obj.search([('product_id', '=', product.id),
                                                   ('state', 'not in', ['done', 'cancel']),
                                                   ('picking_id', 'in', remaining_pickings.ids),
                                                   ('location_id', '=', source_location_id),
                                                   ('location_dest_id', '=', location_dest_id)
                                                   ])
                    if not moves:
                        message = 'Move not found for processing sku %s order ref %s' % (sku, order.name)
                        if not amazon_transaction_log_obj.search(
                                [('message', '=', message), ('manually_processed', '=', False)]):
                            amazon_transaction_log_obj.create({'message': message,
                                                               'model_id': model_id,
                                                               'job_id': job.id,
                                                               'log_type': 'not_found',
                                                               'operation_type': 'import',
                                                               'action_type': 'skip_line',
                                                               'res_id': self.id
                                                               })
                        continue
                    move_pickings = self.create_pack_operations_ept(moves, qty)
                    pickings += move_pickings
                qty = canceled_qty
                if canceled_qty > 0.0:

                    canceled_moves = stock_move_obj.search([('product_id', '=', product.id),
                                                            ('state', '=', 'cancel'),
                                                            ('picking_id', 'in', processed_pickings.ids),
                                                            ('location_id', '=', source_location_id)])
                    canceled_qty = qty

                    for record in canceled_moves:
                        canceled_qty -= record.product_qty

                    if canceled_qty <= 0:
                        continue

                    moves = stock_move_obj.search([('product_id', '=', product.id),
                                                   ('state', 'not in', ['done', 'cancel']),
                                                   ('picking_id', 'in', remaining_pickings.ids),
                                                   ('location_id', '=', source_location_id),
                                                   ('location_dest_id', '=', location_dest_id)
                                                   ])

                    self.update_cancel_qty_ept(moves, canceled_qty)
        pickings = list(set(pickings))
        self.process_picking(pickings)
        pickings = stock_picking_obj.browse(pickings)
        for picking in pickings:
            picking_ids = picking.removal_order_id.removal_order_picking_ids.ids
            if not stock_picking_obj.search(
                    [('is_fba_wh_picking', '=', True), ('id', 'in', picking_ids), ('state', '!=', 'done')]):
                picking.removal_order_id.write({'state': 'Completed'})
        return pickings

    @api.multi
    def process_disposal_lines(self, disposal_line_dict, job, model_id):
        stock_move_obj = self.env['stock.move']
        stock_picking_obj = self.env['stock.picking']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        pickings = []
        for order_key, rows in list(disposal_line_dict.items()):
            order = order_key[0]
            config = order_key[1]
            picking_ids = order.removal_order_picking_ids.ids
            remaining_pickings = stock_picking_obj.search(
                [('id', 'in', picking_ids), ('state', 'not in', ['done', 'cancel'])])
            processed_pickings = stock_picking_obj.search([('id', 'in', picking_ids), ('state', '=', 'done')])
            canceled_pickings = stock_picking_obj.search([('id', 'in', picking_ids), ('state', '=', 'cancel')])
            location_dest_id = config.location_id.id
            unsellable_source_location_id = order.disposition_location_id.id
            sellable_source_location_id = order.instance_id.fba_warehouse_id.lot_stock_id.id
            for row in rows:
                disposed_qty = float(row.get('disposed-quantity', 0.0) or 0.0)
                canceled_qty = float(row.get('cancelled-quantity', 0.0) or 0.0)
                sku = row.get('sku')
                disposition = row.get('disposition')
                order_ref = row.get('order-id')
                product = self.find_amazon_product_for_process_removal_line(row, job, order.instance_id, model_id)
                if not product:
                    continue
                if disposition == 'Unsellable':
                    source_location_id = unsellable_source_location_id
                else:
                    source_location_id = sellable_source_location_id
                qty = disposed_qty
                if disposed_qty > 0.0:
                    if processed_pickings:
                        qty = self.check_move_processed_or_not(product.id, processed_pickings.ids, 'done', job, sku,
                                                               source_location_id, location_dest_id, model_id,
                                                               disposed_qty, order_ref)
                    if qty <= 0.0:
                        continue
                    moves = stock_move_obj.search([('product_id', '=', product.id),
                                                   ('state', 'not in', ['done', 'cancel']),
                                                   ('picking_id', 'in', remaining_pickings.ids),
                                                   ('location_id', '=', source_location_id),
                                                   ('location_dest_id', '=', location_dest_id)])
                    if not moves:
                        message = 'Move not found for processing sku %s order ref %s' % (sku, order.name)
                        if not amazon_transaction_log_obj.search(
                                [('message', '=', message), ('manually_processed', '=', False)]):
                            amazon_transaction_log_obj.create({'message': message,
                                                               'model_id': model_id,
                                                               'job_id': job.id,
                                                               'log_type': 'not_found',
                                                               'action_type': 'skip_line',
                                                               'operation_type': 'import',
                                                               'res_id': self.id
                                                               })
                        continue
                    move_pickings = self.create_pack_operations_ept(moves, qty)
                    pickings += move_pickings
                qty = canceled_qty
                if canceled_qty > 0.0:
                    if canceled_pickings:
                        qty = self.check_move_processed_or_not(product.id, picking_ids, 'cancel', job, sku,
                                                               source_location_id, location_dest_id, model_id,
                                                               canceled_qty, order_ref)
                    if qty <= 0.0:
                        continue
                    moves = stock_move_obj.search([('product_id', '=', product.id),
                                                   ('state', 'not in', ['done', 'cancel']),
                                                   ('picking_id', 'in', remaining_pickings.ids),
                                                   ('location_id', '=', source_location_id),
                                                   ('location_dest_id', '=', location_dest_id)
                                                   ])
                    if not moves:
                        message = 'Move not found for processing sku %s order ref %s' % (sku, order.name)
                        if not amazon_transaction_log_obj.search(
                                [('message', '=', message), ('manually_processed', '=', False)]):
                            amazon_transaction_log_obj.create({'message': message,
                                                               'model_id': model_id,
                                                               'job_id': job.id,
                                                               'log_type': 'not_found',
                                                               'action_type': 'skip_line',
                                                               'operation_type': 'import',
                                                               'res_id': self.id
                                                               })
                        continue
                    self.update_cancel_qty_ept(moves, qty)
        pickings = list(set(pickings))
        pickings and self.process_picking(pickings)
        pickings = stock_picking_obj.browse(pickings)
        for picking in pickings:
            picking_ids = picking.removal_order_id.removal_order_picking_ids.ids
            if not stock_picking_obj.search(
                    [('is_fba_wh_picking', '=', True), ('id', 'in', picking_ids), ('state', '!=', 'done')]):
                picking.removal_order_id.write({'state': 'Completed'})
        return pickings

    @api.multi
    def process_picking(self, pickings):
        stock_picking_obj = self.env['stock.picking']
        pickings = stock_picking_obj.browse(pickings)
        for picking in pickings:
            picking.action_done()
            picking.write({'removal_order_report_id': self.id})
        return True

    @api.multi
    def check_move_processed_or_not(self, product_id, picking_ids, state, job, sku, source_location_id,
                                    location_dest_id, model_id, qty, order_ref):
        stock_move_obj = self.env['stock.move']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']

        existing_move = stock_move_obj.search([('product_id', '=', product_id),
                                               ('state', '=', state), ('picking_id', 'in', picking_ids),
                                               ('location_id', '=', source_location_id),
                                               ('location_dest_id', '=', location_dest_id),
                                               ])
        for move in existing_move:
            qty -= move.product_qty
        if qty <= 0.0:
            amazon_transaction_log_obj.create({'message': """Move already processed
                                                            Product %s || state %s
                                                            Qty %s ||  
                                                            Order ref %s 
                                                            """ % (sku, state, qty, order_ref),
                                               'model_id': model_id,
                                               'job_id': job.id,
                                               'log_type': 'not_found',
                                               'operation_type': 'import',
                                               'action_type': 'skip_line',
                                               'res_id': self.id
                                               })

        return qty

    @api.multi
    def update_cancel_qty_ept(self, moves, quantity):
        stock_move_obj = self.env['stock.move']
        for move in moves:
            if quantity > move.product_qty:
                qty = move.product_qty
            else:
                qty = quantity
            new_move_id = move._split(qty)
            new_move = stock_move_obj.browse(new_move_id)
            new_move._action_cancel()
            quantity = quantity - qty
            if quantity <= 0.0:
                break
        return True

    @api.multi
    def create_pack_operations_ept(self, moves, quantity):
        pick_ids = []
        stock_move_line_obj = self.env['stock.move.line']

        for move in moves:
            #             for quant in move.reserved_quant_ids:
            #                 key=(quant.owner_id.id,move.location_id.id,move.location_dest_id.id,move.product_id.id,move.product_id.uom_id.id,quant.package_id.id,move.picking_id.id)
            #                 if key in qty_grouped:
            #                     qty_grouped[key]+=quant.qty
            #                 else:
            #                     qty_grouped.update({key:quant.qty})
            #
            #         pack_op_qty=0.0
            #         for key, qty in list(qty_grouped.items()):
            #             if quantity>qty:
            #                 pack_op_qty=qty
            #             else:
            #                 pack_op_qty=quantity
            #             pack_op=stock_move_line_obj.with_context({'no_recompute':True}).create(
            #                 {
            #                         'product_qty':float(pack_op_qty) or 0,
            #                         'date':time.strftime('%Y-%m-%d'),
            #                         'location_id':key[1],
            #                         'location_dest_id': key[2],
            #                         'product_id': key[3],
            #                         'product_uom_id': key[4],
            #                         'processed':'true',
            #                         'qty_done':float(pack_op_qty) or 0,
            #                         'picking_id':key[6],
            #                         'owner_id':key[0],
            #                         'package_id':key[5]
            #                  })
            #             pack_operations.append(pack_op.id)
            #             pickings.append(key[6])
            #             quantity=quantity-pack_op_qty
            #             if quantity<=0.0:
            #                 break
            #
            #         if not qty_grouped or quantity>0.0:
            #             for move in moves:
            #                 if quantity>move.product_qty:
            #                     pack_op_qty=move.product_qty
            #                 else:
            #                     pack_op_qty=quantity
            #                 pack_op=stock_move_line_obj.with_context({'no_recompute':True}).create(
            #                                             {
            #                                                         'product_qty':quantity or 0,
            #                                                         'date':time.strftime('%Y-%m-%d'),
            #                                                         'location_id':move.location_id and move.location_id.id or False,
            #                                                         'location_dest_id': move.location_dest_id and move.location_dest_id.id or False,
            #                                                         'product_id': move.product_id and move.product_id.id or False,
            #                                                         'product_uom_id': move.product_id and move.product_id.uom_id and move.product_id.uom_id.id or False,
            #                                                         'processed':'true',
            #                                                         'qty_done':quantity or 0,
            #                                                         'picking_id':move.picking_id.id,
            #                                                         'owner_id':False
            #                                                  })
            #                 pickings.append(move.picking_id.id)
            #                 pack_operations.append(pack_op.id)
            #                 quantity=quantity-pack_op_qty
            #                 if quantity<=0.0:
            #                     break
            #         return pack_operations,pickings
            qty_left = quantity
            if qty_left <= 0.0:
                break
            move_line_remaning_qty = (move.product_uom_qty) - (sum(move.move_line_ids.mapped('qty_done')))
            operations = move.move_line_ids.filtered(lambda o: o.qty_done <= 0 and not o.result_package_id)
            for operation in operations:
                if operation.product_uom_qty <= qty_left:
                    op_qty = operation.product_uom_qty
                else:
                    op_qty = qty_left
                operation.write({'qty_done': op_qty})
                self._put_in_pack(operation)  # ,package)
                qty_left = float_round(qty_left - op_qty, precision_rounding=operation.product_uom_id.rounding,
                                       rounding_method='UP')
                move_line_remaning_qty = move_line_remaning_qty - op_qty
                if qty_left <= 0.0:
                    break
            picking = moves[0].picking_id
            if qty_left > 0.0 and move_line_remaning_qty > 0.0:
                if move_line_remaning_qty <= qty_left:
                    op_qty = move_line_remaning_qty
                else:
                    op_qty = qty_left
                stock_move_line_obj.create(
                    {
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_id.uom_id.id,
                        'picking_id': move.picking_id.id,
                        'qty_done': float(op_qty) or 0,
                        # 'ordered_qty':float(op_qty) or 0,
                        #                             'result_package_id':package and package.id or False,
                        'location_id': picking.location_id.id,
                        'location_dest_id': picking.location_dest_id.id,
                        'move_id': move.id,
                    })
                pick_ids.append(move.picking_id.id)
                qty_left = float_round(qty_left - op_qty, precision_rounding=move.product_id.uom_id.rounding,
                                       rounding_method='UP')
                if qty_left <= 0.0:
                    break

            if qty_left > 0.0:
                stock_move_line_obj.create(
                    {
                        'product_id': moves[0].product_id.id,
                        'product_uom_id': moves[0].product_id.uom_id.id,
                        'picking_id': picking.id,
                        # 'ordered_qty':float(qty_left) or 0,
                        'qty_done': float(qty_left) or 0,
                        #                             'result_package_id':package and package.id or False,
                        'location_id': picking.location_id.id,
                        'location_dest_id': picking.location_dest_id.id,
                        'move_id': moves[0].id,
                    })
            pick_ids.append(move.picking_id.id)
        return pick_ids

    def _put_in_pack(self, operation, package=False):
        operation_ids = self.env['stock.move.line']
        if float_compare(operation.qty_done, operation.product_uom_qty,
                         precision_rounding=operation.product_uom_id.rounding) >= 0:
            operation_ids |= operation
        else:
            quantity_left_todo = float_round(
                operation.product_uom_qty - operation.qty_done,
                precision_rounding=operation.product_uom_id.rounding,
                rounding_method='UP')
            new_operation = operation.copy(
                default={'product_uom_qty': operation.qty_done, 'qty_done': operation.qty_done})
            operation.write({'product_uom_qty': quantity_left_todo, 'qty_done': 0.0})
            operation_ids |= new_operation

        package and operation_ids.write({'result_package_id': package.id})
        return True
