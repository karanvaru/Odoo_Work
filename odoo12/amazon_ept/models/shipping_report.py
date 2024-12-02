import logging
import time
from datetime import datetime, timedelta
import base64
import csv
from io import StringIO
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from dateutil import parser
from odoo.api import Environment
from odoo.tools.float_utils import float_round, float_compare
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT

utc = pytz.utc
_logger = logging.getLogger(__name__)

class shipping_report_history(models.Model):
    _name = "shipping.report.order.history"
    
    instance_id = fields.Many2one("amazon.instance.ept",string="Amazon Instance",index=True)
    amazon_order_ref = fields.Char("Amazon Order Ref",index=True)
    order_line_ref = fields.Char("Order Line Ref")
    shipment_id = fields.Char("Shipment ID")
    shipment_line_id = fields.Char("Shipment Line ID")
    
    def check_order_existing_or_not(self,row,instance):
        record = self.search([('instance_id','=',instance.id),
                     ('amazon_order_ref','=',row.get('amazon-order-id'))]).filtered(lambda l:l.order_line_ref == row.get('amazon-order-item-id')
                                                                                    and l.shipment_id == row.get('shipment-id')
                                                                                    and l.shipment_line_id == row.get('shipment-item-id'))
        if record:
            return True
        return False
class shipping_report_request_history(models.Model):
    _name = "shipping.report.request.history"
    _inherits = {"report.request.history": 'report_history_id'}
    _description = "Shipping Report"
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.one
    def get_order_count(self):
        self.order_count = len(self.amazon_sale_order_ids.ids)

    @api.one
    def get_log_count(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('shipping.report.request.history')
        records = amazon_transaction_log_obj.search(
            [('model_id', '=', model_id), ('res_id', '=', self.id)])
        self.log_count = len(records.ids)

    name = fields.Char(size=256, string='Name')
    report_history_id = fields.Many2one('report.request.history', string='Report', required=True,
                                        ondelete="cascade", index=True, auto_join=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('_SUBMITTED_', 'SUBMITTED'), ('_IN_PROGRESS_', 'IN_PROGRESS'),
         ('_CANCELLED_', 'CANCELLED'), ('_DONE_', 'DONE'),
         ('partially_processed', 'Partially Processed'),
         ('_DONE_NO_DATA_', 'DONE_NO_DATA'), ('processed', 'PROCESSED')
         ],
        string='Report Status', default='draft')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    auto_generated = fields.Boolean('Auto Generated Record ?', default=False)
    amazon_sale_order_ids = fields.One2many('sale.order', 'amz_shipment_report_id',
                                            string="Sales Order Ids")
    order_count = fields.Integer(compute="get_order_count", string="Order Count")
    log_count = fields.Integer(compute="get_log_count", string="Log Count")

    @api.multi
    def list_of_sales_orders(self):
        action = {
            'domain': "[('id', 'in', " + str(self.amazon_sale_order_ids.ids) + " )]",
            'name': 'Amazon Sales Orders',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.multi
    def list_of_logs(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('shipping.report.request.history')
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

    @api.multi
    def unlink(self):
        for report in self:
            if report.state == 'processed':
                raise Warning(_('You cannot delete processed report.'))
        return super(shipping_report_request_history, self).unlink()

    @api.model
    def default_get(self, fields):
        res = super(shipping_report_request_history, self).default_get(fields)
        if not fields:
            return res
        res.update({'report_type': '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_',
                    })
        return res

    @api.model
    def create(self, vals):
        try:
            sequence = self.env.ref('amazon_ept.seq_import_shipping_report_job')
            if sequence:
                report_name = sequence.next_by_id()
            else:
                report_name = '/'
        except:
            report_name = '/'
        vals.update({'name': report_name})
        return super(shipping_report_request_history, self).create(vals)

    @api.onchange('seller_id')
    def on_change_seller_id(self):
        value = {}
        if self.seller_id:
            start_date = datetime.now() + timedelta(
                days=self.seller_id.fba_shipment_report_days * -1 or -3)
            value.update({'start_date': start_date, 'end_date': datetime.now()})
        return {'value': value}

    """Method added by Dhruvi[10-09-2018]
        It will not confirm sale order as they are already confirmed while processing 
        shipment report.
        It will only create and validate invoice."""

    @api.model
    def fba_auto_workflow_process(self, auto_workflow_process_id=False, ids=[]):
        transaction_log_obj = self.env['transaction.log.ept']
        with Environment.manage():
            env_thread1 = Environment(self._cr, self._uid, self._context)
            sale_order_obj = env_thread1['sale.order']
            sale_order_line_obj = env_thread1['sale.order.line']
            account_payment_obj = env_thread1['account.payment']
            workflow_process_obj = env_thread1['sale.workflow.process.ept']
            if not auto_workflow_process_id:
                work_flow_process_records = workflow_process_obj.search([])
            else:
                work_flow_process_records = workflow_process_obj.browse(auto_workflow_process_id)

            if not work_flow_process_records:
                return True

            for work_flow_process_record in work_flow_process_records:
                if not ids:
                    orders = sale_order_obj.search(
                        [('auto_workflow_process_id', '=', work_flow_process_record.id),
                         ('state', 'not in', ('done', 'cancel', 'sale')),
                         ('invoice_status', '!=', 'invoiced')])  # ('invoiced','=',False)
                else:
                    orders = sale_order_obj.search(
                        [('auto_workflow_process_id', '=', work_flow_process_record.id),
                         ('id', 'in', ids)])
                if not orders:
                    continue
                for order in orders:
                    if order.invoice_status and order.invoice_status == 'invoiced':
                        continue
                    if work_flow_process_record.invoice_policy == 'delivery':
                        continue
                    if not work_flow_process_record.invoice_policy and not sale_order_line_obj.search(
                            [('product_id.invoice_policy', '!=', 'delivery'),
                             ('order_id', 'in', order.ids)]):
                        continue
                    if not order.invoice_ids:
                        if work_flow_process_record.create_invoice:
                            try:
                                order.action_invoice_create()
                            except Exception as e:
                                transaction_log_obj.create({
                                    'message': "Error while Create invoice for Order %s\n%s" % (
                                        order.name, e),
                                    'mismatch_details': True,
                                    'type': 'invoice'
                                })
                                continue
                    if work_flow_process_record.validate_invoice:
                        for invoice in order.invoice_ids:
                            try:
                                invoice.action_invoice_open()
                            except Exception as e:
                                transaction_log_obj.create({
                                    'message': "Error while open Invoice for Order %s\n%s" % (
                                        order.name, e),
                                    'mismatch_details': True,
                                    'type': 'invoice'
                                })
                                continue
                            if work_flow_process_record.register_payment:
                                if invoice.residual:
                                    # Create Invoice and Make Payment
                                    vals = {
                                        'journal_id': work_flow_process_record.journal_id.id,
                                        'invoice_ids': [(6, 0, [invoice.id])],
                                        'communication': invoice.reference,
                                        'currency_id': invoice.currency_id.id,
                                        'payment_type': 'inbound',
                                        'partner_id': invoice.commercial_partner_id.id,
                                        'amount': invoice.residual,
                                        'payment_method_id': work_flow_process_record.journal_id.inbound_payment_method_ids.id,
                                        'partner_type': 'customer'
                                    }
                                    try:
                                        new_rec = account_payment_obj.create(vals)
                                        new_rec.post()
                                    except Exception as e:
                                        transaction_log_obj.create({
                                            'message': "Error while Validating Invoice for Order %s\n%s" % (
                                                order.name, e),
                                            'mismatch_details': True,
                                            'type': 'invoice'
                                        })
                                        continue
        return True

    @api.model
    def auto_import_shipment_report(self, args):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].browse(int(seller_id))
            if seller.shipping_report_last_sync_on:
                start_date = seller.shipping_report_last_sync_on
                try :
                    start_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S.%f')
                except:
                    start_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')                    
                start_date = start_date - timedelta(hours=10)
            else:
                today = datetime.now()
                earlier = today - timedelta(days=30)
                start_date = earlier.strftime("%Y-%m-%d %H:%M:%S")
            start_date = datetime.now() + timedelta(days=seller.fba_shipment_report_days * -1 or -3)
            start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
            end_date = datetime.now()
            end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")

            report_type = '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_'
            if not seller.is_another_soft_create_fba_shipment:
                if not self.search([('start_date', '=', start_date),
                                    ('end_date', '=', end_date),
                                    ('seller_id', '=', seller_id), ('report_type', '=', report_type)]):
                    shipment_report = self.create({'report_type': report_type,
                                                   'seller_id': seller_id,
                                                   'state': 'draft',
                                                   'start_date': start_date,
                                                   'end_date': end_date,
                                                   'requested_date': time.strftime("%Y-%m-%d %H:%M:%S")
                                                   })
                    shipment_report.with_context(is_auto_process=True).request_report()
            else:
                date_start = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                date_end = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                list_of_wrapper = self.get_reports_from_other_softwares(seller, report_type, date_start, date_end)
                for reports in list_of_wrapper:
                    for report in reports.get('ReportRequestInfo', {}):
                        report_id = report.get('GeneratedReportId', {}).get('value')
                        request_id = report.get('ReportRequestId', {}).get('value')
                        if not self.search([('report_id', '=', report_id),
                                            ('report_request_id', '=', request_id),
                                            ('report_type', '=', report_type)]):
                            start = report.get('StartDate', {}).get('value', {}).split('+')
                            end = report.get('EndDate', {}).get('value', {}).split('+')
                            self.create({
                                'seller_id': seller_id,
                                'state': report.get('ReportProcessingStatus', {}).get('value'),
                                'start_date': datetime.strptime(start[0], '%Y-%m-%dT%H:%M:%S'),
                                'end_date': datetime.strptime(end[0], '%Y-%m-%dT%H:%M:%S'),
                                'report_type': report.get('ReportType', {}).get('value'),
                                'report_id': report.get('GeneratedReportId', {}).get('value'),
                                'report_request_id': report.get('ReportRequestId', {}).get('value'),
                                'requested_date': time.strftime("%Y-%m-%d %H:%M:%S")
                            })
            seller.write({'shipping_report_last_sync_on': end_date})
        return True

    @api.multi
    def get_reports_from_other_softwares(self, seller, report_type, start_date, end_date):
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].with_user(self.env.user).get_param('database.uuid')
        instances_obj = self.env['amazon.instance.ept']
        instances = instances_obj.search([('seller_id', '=', seller.id)])
        marketplaceids = tuple(map(lambda x: x.market_place_id, instances))

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'emipro_api': 'get_shipping_or_inventory_report',
                  'account_token': account.account_token,
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'marketplaceids': marketplaceids,
                  'report_type': '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_',
                  'start_date': start_date,
                  'end_date': end_date
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if not response.get('reason'):
            list_of_wrapper = response.get('result')
        else:
            raise Warning(response.get('reason'))
        return list_of_wrapper

    @api.model
    def auto_process_shipment_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            shipment_reports = self.search(
                [('seller_id', '=', seller.id), ('state', 'in', ['_SUBMITTED_', '_IN_PROGRESS_'])])
            if shipment_reports:
                total_length = len(shipment_reports.ids)
                for x in range(0, total_length, 20):
                    reports = shipment_reports[x:x + 20]
                    reports.with_context(is_auto_process=True).get_report_request_list_via_cron(seller)

                    reports = self.search([('seller_id', '=', seller.id),
                                           ('state', '=', '_DONE_'),
                                           ('report_id', '!=', False)
                                           ], order='id asc')
                    for report in reports:
                        while True:
                            report.with_context(is_auto_process=True).get_report()
                            break
                        try:
                            report.process_shipment_file()
                            self._cr.commit()
                        except:
                            continue
                        time.sleep(3)
            else:
                reports = self.search([('seller_id', '=', seller.id),
                                       ('state', '=', '_DONE_'),
                                       ], order='id asc')
                for report in reports:
                    if not report.attachment_id:
                        while True:
                            report.with_context(is_auto_process=True).get_report()
                            break
                    try:
                        report.process_shipment_file()
                        self._cr.commit()
                    except:
                        continue
                    time.sleep(3)
        return True

    @api.multi
    def get_report_request_list_via_cron(self, seller):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        results = []
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
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Shipping Report Process',
                    'application': 'other',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'shipping.report.request.history'),
                    'log_type': 'error',
                    'skip_record': True,
                    'message': response.get('reason'),
                    'job_id': job.id
                }
                amazon_transaction_obj.create(log_line_vals)
            else:
                raise Warning(response.get('reason'))
        else:
            results = response.get('result')
            for result in results:
                self.update_report_history_via_cron(result, report_info_records)

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
    def request_report(self):
        seller, report_type, start_date, end_date = self.seller_id, self.report_type, self.start_date, self.end_date
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False

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

        instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])

        marketplaceids = tuple(map(lambda x: x.market_place_id, instances))

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'shipping_request_report',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'marketplaceids': marketplaceids,
                  'report_type': report_type,
                  'start_date': start_date,
                  'end_date': end_date, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Shipping Report Process',
                    'application': 'other',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'shipping.report.request.history'),
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

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            list_of_wrapper = response.get('result')

        for result in list_of_wrapper:
            self.update_report_history(result)

        return True

    @api.multi
    def get_report_list(self):
        self.ensure_one()
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        seller = self.seller_id
        list_of_wrapper = []
        if not seller:
            raise Warning('Please select seller')

        proxy_data = seller.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'get_report_list',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'request_id': [self.request_id]}

        if not self.request_id:
            return True

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Shipping Report Process',
                    'application': 'other',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'shipping.report.request.history'),
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
    def get_report(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        self.ensure_one()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        seller = self.seller_id
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
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Shipping Report Process',
                    'application': 'other',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'shipping.report.request.history'),
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
        file_name = "Shipment_report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': result,
            'datas_fname': file_name,
            'res_model': 'mail.compose.message',
            'type': 'binary'
        })
        self.message_post(body=_("<b>Shipment Report Downloaded</b>"),
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

    @api.multi
    def check_product_exist_or_not_create_based_on_configuration(self, row, job_ids):
        marketplace_obj = self.env['amazon.marketplace.ept']
        process_log_book_obj = self.env['amazon.process.log.book']
        sales_channel = row.get('sales-channel', '')
        instance = marketplace_obj.find_instance(self.seller_id, sales_channel)
        if not instance:
            return False, []
        seller = instance.seller_id
        amazon_product_obj = self.env['amazon.product.ept']
        amazon_transaction_obj = self.env['amazon.transaction.log']
        log_action_type = 'skip_line'
        log_message = ''
        skip_order = False
        product_name = row.get('product-name')
        amazon_order_ref = row.get('amazon-order-id', False)
        sku = row.get('sku', False)
        domain = [('instance_id', '=', instance.id)]
        domain.append(('seller_sku', '=', sku))
        amazon_product = amazon_product_obj.search_amazon_product(instance.id, sku, 'AFN')
        if not amazon_product:
            erp_product = amazon_product_obj.search_product(sku)
            """
                If odoo product founds and amazon product not found then no need to check anything 
                and create new amazon product and create log for that, if odoo product not found then 
                go to check configuration which action has to be taken for that.
                
                There are following situations managed by code. 
                In any situation log that event and action.
                
                1). Amazon product and odoo product not found
                    => Check seller configuration if allow to create new product then create product.
                    => Enter log details with action.
                2). Amazon product not found but odoo product is there.
                    => Created amazon product with log and action.
            """
            product_id = False
            if erp_product:
                product_id = erp_product.id
                log_action_type = 'create'
                log_message = 'Odoo Product is already exists. ' \
                              'System have created new Amazon Product %s for %s instance' % (
                                  sku, instance.name)
                # log_message = 'Product %s created in amazon for %s instance'%(sku, instance.name )
            elif not seller.create_new_product:
                skip_order = True
                log_action_type = 'skip_line'
                log_message = 'Product %s not found for %s instance' % (sku, instance.name)
            else:
                log_action_type = 'create'
                log_message = 'System have created new Odoo Product %s for %s instance' % (
                    sku, instance.name)
                # log_message = 'Product %s created in odoo for %s instance'%(sku, instance.name )

            if not skip_order:
                sku = sku or (erp_product and erp_product[0].default_code) or False
                prod_vals = {
                    'instance_id': instance.id,
                    'seller_sku': sku,
                    'type': erp_product and erp_product[0].type or 'product',
                    'product_id': product_id,
                    'purchase_ok': True,
                    'sale_ok': True,
                    'exported_to_amazon': True,
                    'fulfillment_by': "AFN",
                }
                if not erp_product:
                    prod_vals.update({'name': product_name, 'default_code': sku,
                                      'company_id': instance.company_id.id})

                amazon_product = amazon_product_obj.create(prod_vals)

            job = process_log_book_obj.search(
                [('id', 'in', job_ids), ('instance_id', '=', instance.id)])
            if not job:
                job_log_vals = {
                    'skip_process': skip_order,
                    'application': 'sales',
                    'operation_type': 'import',
                    'instance_id': instance.id
                }
                job = self.env['amazon.process.log.book'].create(job_log_vals)
                job_ids.append(job.id)

            log_line_vals = {
                'model_id': self.env['amazon.transaction.log'].get_model_id(
                    'shipping.report.request.history'),
                'res_id': self.id or 0,
                'log_type': 'not_found',
                'action_type': log_action_type,
                'not_found_value': sku,
                'user_id': self.env.uid,
                'skip_record': skip_order,
                'amazon_order_reference': amazon_order_ref,
                'message': log_message,
                'job_id': job.id
            }
            amazon_transaction_obj.create(log_line_vals)
        return skip_order, job_ids

    @api.multi
    def create_or_update_outbound_order(self, order_details_dict, order_lines_details_dict,
                                        odoo_available_order_line_dict,
                                        odoo_available_order_line_service_dict):
        already_taken_orders = []
        odoo_order_wh_dict = {}
        odoo_order_ids = []
        order_line_obj = self.env['sale.order.line']
        amazon_product_obj = self.env['amazon.product.ept']
        # create splited order
        for order_wh, amazon_order in order_details_dict.items():
            warehouse = order_wh[1]
            if amazon_order.order_line:
                amazon_order.order_line.sudo().unlink()
            fulfillment_instance = amazon_order.amz_instance_id
            if amazon_order.id in already_taken_orders:
                new_amazon_order = self.copy_amazon_order(amazon_order, warehouse,
                                                          fulfillment_instance)
                new_amazon_order.write({'amz_fulfillment_instance_id': fulfillment_instance.id,
                                        'date_order': amazon_order.date_order})
                already_taken_orders.append(new_amazon_order.id)
                amazon_order = new_amazon_order
            else:
                already_taken_orders.append(amazon_order.id)
                if amazon_order.warehouse_id.id != warehouse.id:
                    amazon_order.write({'warehouse_id': warehouse.id})
                amazon_order.partner_id.write({'company_id': fulfillment_instance.company_id.id})
                amazon_order.onchange_warehouse_id()

                """Changes by Dhruvi fba_auto_workflow_id is fetched according to seller wise."""
                amazon_order.write({
                    'auto_workflow_process_id': fulfillment_instance.seller_id.fba_auto_workflow_id.id,
                    'amz_shipment_report_id': self.id})
            odoo_order_wh_dict.update({order_wh: amazon_order})
            odoo_order_ids.append(amazon_order.id)

            # create  order line
        for wh_order_item_key, line_data in order_lines_details_dict.items():
            warehouse = wh_order_item_key[0]
            amazon_order = line_data.get('amazon_order')
            order_id = line_data.get('amazon_order_id')
            amazon_order_item_id = line_data.get('amazon_order_item_id')
            fulfillment_center = line_data.get('fulfillment_center', False)
            fulfillment_instance = line_data.get('fulfillment_instance_id')
            order_line_data = {
                'shipped_qty': line_data.get('shipped_qty', 0.0),
                'amz_fulfillment_center': fulfillment_center,
                'amazon_order_item_id': amazon_order_item_id,
                'name': line_data.get('product_name', ''),
                'sku': line_data.get('sku', False)
            }
            seller_sku = line_data.get('sku', False)
            amazon_product = amazon_product_obj.search_amazon_product(fulfillment_instance.id,
                                                                      seller_sku, 'AFN')
            product = amazon_product and amazon_product.product_id
            price_unit = odoo_available_order_line_dict.get(amazon_order, {}).get(product, {}).get(
                'price', 0.0)
            line_qty = odoo_available_order_line_dict.get(amazon_order, {}).get(product, {}).get(
                'qty', 0.0)
            odoo_available_order_line_dict.get(amazon_order, {}).get(product, {}).update(
                {'qty': line_qty - line_data.get('shipped_qty', 0.0)})
            discount = odoo_available_order_line_dict.get(amazon_order, {}).get(product, {}).get(
                'discount', 0.0)
            order_line_data.update({'item_price': price_unit or 0.0, 'discount': discount or 0.0})

            amazon_splitedorder = odoo_order_wh_dict.get((order_id, warehouse))
            amazon_line_rec = amazon_product and order_line_obj.search(
                [('order_id', '=', amazon_splitedorder.id),
                 ('product_id', '=', amazon_product.product_id.id),
                 ('amz_fulfillment_center_id', '=', fulfillment_center.id)])
            if not amazon_line_rec:
                amazon_line_rec = self.create_sale_order_line(amazon_splitedorder, order_line_data,
                                                              is_outbound_order=True)
            else:
                amazon_line_rec.write({
                    'product_uom_qty': amazon_line_rec.product_uom_qty + line_data.get(
                        'shipped_qty', 0.0)})

            # This method is for add shipping charge in  split order
            for product, line in odoo_available_order_line_service_dict.get(amazon_order,
                                                                            {}).items():
                discount = line.get('discount', 0.0)
                price = line.get('price', 0.0)
                qty = line.get('qty', 0.0)
                new_record = order_line_obj.new({'order_id': amazon_splitedorder.id,
                                                 'company_id': amazon_splitedorder.company_id.id,
                                                 'product_id': product.id,
                                                 'product_uom': product.uom_id.id,
                                                 'name': product.name
                                                 })
                new_record.product_id_change()
                order_vals = new_record._convert_to_write(new_record._cache)
                order_vals.update({
                    'product_uom_qty': qty,
                    'amazon_order_qty': qty,
                    'name': product.name,
                    'price_unit': price,
                    'state': 'draft',
                    'product_id': product.id,
                    'discount': discount,
                    #                         'amazon_product_id':amazon_product.id,
                })
                order_line_obj.create(order_vals)
            if amazon_order in odoo_available_order_line_service_dict:
                del odoo_available_order_line_service_dict[amazon_order]

        # create order for remaining qty who not deliver or not availble at a time
        new_pending_quotations = {}
        for amazon_order, line_data in odoo_available_order_line_dict.items():
            for product, line in line_data.items():
                if line.get('qty') > 0.0:
                    if not new_pending_quotations.get(amazon_order):
                        new_pending_quotation = self.copy_amazon_order(amazon_order,
                                                                       line.get('warehouse_id'),
                                                                       line.get('instance_id'))
                        new_pending_quotations.update({amazon_order: new_pending_quotation})
                    else:
                        new_pending_quotation = new_pending_quotations.get(amazon_order)
                    remaining_qty = line.get('qty')
                    price_unit = line.get('price')
                    price = line.get('price')
                    new_record = order_line_obj.new({'order_id': new_pending_quotation.id,
                                                     'company_id': new_pending_quotation.company_id.id,
                                                     'product_id': product.id,
                                                     'product_uom': product.uom_id.id,
                                                     'name': product.name
                                                     })
                    new_record.product_id_change()
                    order_vals = new_record._convert_to_write(new_record._cache)
                    order_vals.update({
                        'product_uom_qty': remaining_qty,
                        'amazon_order_qty': remaining_qty,
                        'name': product.name,
                        'price_unit': price_unit,
                        'state': 'draft',
                        'product_id': product.id,
                        'discount': line.get('discount'),
                        #                         'amazon_product_id':amazon_product.id,
                    })
                    order_line_obj.create(order_vals)

        return odoo_order_ids, odoo_order_wh_dict

    @api.multi
    def process_outbound_orders(self, outbound_order_rows):
        shipment_details_dict = {}
        order_lines_details_dict = {}
        order_details_dict = {}
        instance_data = {}
        job = False
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        order_obj = self.env['sale.order']
        odoo_available_order_line_dict = {}
        odoo_available_order_line_service_dict = {}
        for row in outbound_order_rows:
            odoo_sale_order_id = row.get('merchant-order-id', False)
            amazon_order = order_obj.search(
                [('amazon_reference', '=', odoo_sale_order_id), ('state', '=', 'draft')])
            if not amazon_order:
                log_message = 'Order %s not found in ERP.' % (odoo_sale_order_id)
                if not amazon_transaction_obj.search(
                        [('message', '=', log_message), ('manually_processed', '=', False)]):
                    if not job:
                        job_log_vals = {
                            'skip_process': True,
                            'application': 'sales',
                            'operation_type': 'import',
                        }
                    job = amazon_log_book_obj.create(job_log_vals)
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'shipping.report.request.history'),
                        'res_id': self.id or 0,
                        'log_type': 'not_found',
                        'not_found_value': odoo_sale_order_id,
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'operation_type': 'import',
                        'amazon_order_reference': odoo_sale_order_id,
                        'message': log_message,
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                continue
            if amazon_order not in odoo_available_order_line_dict:
                odoo_available_order_line_dict.update({amazon_order: {}})
                odoo_available_order_line_service_dict.update({amazon_order: {}})
                for line in amazon_order.order_line:
                    qty = odoo_available_order_line_dict.get(amazon_order, {}).get(
                        line.product_id.id, {}).get('qty', 0.0)
                    if line.product_id.type != 'service':
                        odoo_available_order_line_dict.get(amazon_order).update({line.product_id: {
                            'qty': line.product_uom_qty + qty, 'price': line.price_unit,
                            'discount': line.discount, 'warehouse_id': amazon_order.warehouse_id,
                            'instance_id': amazon_order.amz_instance_id}})
                    else:
                        odoo_available_order_line_service_dict.get(amazon_order).update({
                            line.product_id: {
                                'qty': line.product_uom_qty + qty,
                                'price': line.price_unit,
                                'discount': line.discount}})
            fulfillment_instance = amazon_order.amz_instance_id
            instance_data.update({row.get('sales-channel'): fulfillment_instance})
            fulfillment_id = row.get('fulfillment-center-id')
            fulfillment_center, warehouse = self.get_warehouse(fulfillment_id, fulfillment_instance)
            amazon_order_id = row.get('merchant-order-id', False)
            order_wh_key = (amazon_order_id, warehouse)
            if order_wh_key not in order_details_dict.keys():
                order_details_dict.update({order_wh_key: amazon_order})
            sku = row.get('sku', '')
            amazon_order_item_id = row.get('amazon-order-item-id', False)
            shipped_qty = float(row.get('quantity-shipped', 0.0))
            gift_wrap_tax = row.get('gift-wrap-tax', 0.0)
            promotion_discount = row.get('item-promotion-discount', 0.0)
            line_data = {
                'amazon_order_id': amazon_order_id,
                'amazon_order_item_id': amazon_order_item_id,
                'sku': sku,
                'shipped_qty': shipped_qty,
                'product_name': row.get('product-name', ''),
                'gift_wrapper_charge': row.get('gift-wrap-price', 0.0) and float(
                    row.get('gift-wrap-price', 0.0)) or 0.0,
                'gift_wrapper_tax': gift_wrap_tax and float(gift_wrap_tax) or 0.0,
                'promotion_discount': promotion_discount and float(promotion_discount) or 0.0,
                'fulfillment_center': fulfillment_center,
                'fulfillment_instance_id': fulfillment_instance,
                'amazon_order': amazon_order
            }
            wh_order_item_key = (warehouse, amazon_order_item_id)

            if wh_order_item_key in order_lines_details_dict:
                order_lines_details_dict[wh_order_item_key]['shipped_qty'] += line_data.get(
                    'shipped_qty', 0.0)
                order_lines_details_dict[wh_order_item_key]['gift_wrapper_charge'] += line_data.get(
                    'gift_wrapper_charge', 0.0)
                order_lines_details_dict[wh_order_item_key]['gift_wrapper_tax'] += line_data.get(
                    'gift_wrapper_tax', 0.0)
                order_lines_details_dict[wh_order_item_key]['promotion_discount'] += line_data.get(
                    'promotion_discount', 0.0)
            else:
                order_lines_details_dict.update({wh_order_item_key: line_data})

            tracking_number = row.get('tracking-number', '')
            ship_date = row.get('shipment-date', False)
            shipment_id = row.get('shipment-id')
            order_ship_wh_key = (amazon_order_id, shipment_id, warehouse)
            if order_ship_wh_key not in shipment_details_dict:
                shipment_details_dict.update({order_ship_wh_key: [{
                    'amazon_reference': amazon_order_id,
                    'amazon_order_item_id': amazon_order_item_id,
                    'shipped_qty': shipped_qty,
                    'sku': sku,
                    'tracking_number': tracking_number,
                    'ship_date': ship_date,
                    'carrier': row.get('carrier')
                }]})

            else:
                shipment_details_dict.get(order_ship_wh_key).append({
                    'amazon_reference': amazon_order_id,
                    'amazon_order_item_id': amazon_order_item_id,
                    'shipped_qty': shipped_qty,
                    'sku': sku,
                    'tracking_number': tracking_number,
                    'ship_date': ship_date,
                    'carrier': row.get('carrier')
                })

        odoo_order_ids, odoo_order_wh_dict = self.create_or_update_outbound_order(
            order_details_dict, order_lines_details_dict, odoo_available_order_line_dict,
            odoo_available_order_line_service_dict)
        odoo_order_ids = list(set(odoo_order_ids))
        order_ids = order_obj.browse(odoo_order_ids)

        """Added by Dhruvi [10-09-2018]
        Loop for confirming sale order
        It calls fba_auto_workflow_process to create and validate invoice."""

        for order_id in order_ids:
            try:
                order_id.action_confirm()
                order_id.write({'confirmation_date': order_id.date_order})
            except Exception as e:
                amazon_transaction_obj.create({
                    'message': "Error while confirm Sale Order %s\n%s" % (order_id.name, e),
                    'mismatch_details': True,
                    'type': 'sales'
                })
                order_id.state = 'draft'
                continue
        #         odoo_order_ids and self.env['sale.workflow.process.ept'].
        # auto_workflow_process(ids=odoo_order_ids)
        odoo_order_ids and self.fba_auto_workflow_process(ids=odoo_order_ids)
        odoo_order_ids and self.process_delivery_orders_new(shipment_details_dict,
                                                            odoo_order_wh_dict)
        return True

    @api.multi
    def re_process_shipment_file(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_obj.get_model_id('shipping.report.request.history')
        records = amazon_transaction_obj.search(
            [('model_id', '=', model_id), ('action_type', '!=', 'create'),
             ('res_id', '=', self.id)])
        records.unlink()
        #         self.with_context({'re_process_file':True}).process_shipment_file()
        self.process_shipment_file()

    @api.multi
    def process_shipment_file(self):
        self.ensure_one()
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        reader = csv.DictReader(imp_file, delimiter='\t')
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        marketplace_obj = self.env['amazon.marketplace.ept']
        shipment_history_obj = self.env['shipping.report.order.history']
        order_obj = self.env['sale.order']
        fulfillment_warehouse = {}
        orders_lines_dict = {}
        order_details_dict = {}
        exist_order_details_dict = {}
        new_order_details_dict = {}
        exist_order_lines_details_dict = {}
        new_order_lines_details_dict = {}
        shipment_details_dict = {}
        instances = {}
        split_order_line_dict = {}
        odoo_order_ids = []
        job = False
        job_ids = []
        skip_orders = []
        outbound_order_rows = []
        for row in reader:
            sales_channel = row.get('sales-channel', '')
            if sales_channel not in instances:
                instance = marketplace_obj.find_instance(self.seller_id, sales_channel)
                instances.update({sales_channel: instance})
            instance = instances.get(sales_channel)
            if instance:
                order_exist = shipment_history_obj.check_order_existing_or_not(row,instance)
                if order_exist:
                    continue
            order_exist = False
            skip_order, job_ids = self.check_product_exist_or_not_create_based_on_configuration(row,
                                                                                                job_ids)
            if skip_order:
                continue
            if row.get('amazon-order-id') in skip_orders:
                continue
            if row.get('merchant-order-id', False):
                outbound_order_rows.append(row)
                continue
            if not instance:
                skip_orders.append(row.get('amazon-order-id'))
                if not job:
                    job_log_vals = {
                        'skip_process': True,
                        'message': 'Amazon FBA Shipment Report',
                        'application': 'sales',
                        'operation_type': 'import',
                        'instance_id': instance.id
                    }
                    job = amazon_log_book_obj.create(job_log_vals)
                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'shipping.report.request.history'),
                    'res_id': self.id or 0,
                    'log_type': 'not_found',
                    'not_found_value': sales_channel,
                    'action_type': 'skip_line',
                    'user_id': self.env.uid,
                    'skip_record': True,
                    'amazon_order_reference': row.get('amazon-order-id', False),
                    'message': 'Order skiped due to instance not found in ERP for sales channel %s' % (
                        sales_channel),
                    'job_id': job.id
                }
                amazon_transaction_obj.create(log_line_vals)
                continue
            fulfillment_id = row.get('fulfillment-center-id')
            if fulfillment_id not in fulfillment_warehouse:
                fulfillment_center, fn_warehouse = self.get_warehouse(fulfillment_id, instance)
                if not fn_warehouse:
                    skip_orders.append(row.get('amazon-order-id'))
                    if not job:
                        job_log_vals = {
                            'skip_process': True,
                            'message': 'Amazon FBA Shipment Report',
                            'application': 'sales',
                            'operation_type': 'import',
                            'instance_id': instance.id
                        }
                        job = amazon_log_book_obj.create(job_log_vals)
                    log_line_vals = {
                        'model_id': self.env['amazon.transaction.log'].get_model_id(
                            'shipping.report.request.history'),
                        'res_id': self.id or 0,
                        'log_type': 'not_found',
                        'not_found_value': fulfillment_id,
                        'action_type': 'skip_line',
                        'user_id': self.env.uid,
                        'skip_record': True,
                        'amazon_order_reference': row.get('amazon-order-id', False),
                        'message': 'Order skiped due to warehouse not found in ERP for fulfillment center %s' % (
                            fulfillment_id),
                        'job_id': job.id
                    }
                    amazon_transaction_obj.create(log_line_vals)
                    continue
                fulfillment_warehouse.update({fulfillment_id: [fn_warehouse, fulfillment_center]})
            warehouse = fulfillment_warehouse.get(fulfillment_id, [False])[0]
            fullfillment_center = fulfillment_warehouse.get(fulfillment_id, [False])[1]
            shipment_id = row.get('shipment-id', False)
            amazon_order_id = row.get('amazon-order-id', False)
            order_wh_key = (amazon_order_id, warehouse)
            amazon_orders = order_obj.search(
                [('amazon_reference', '=', amazon_order_id), ('amz_instance_id', '=', instance.id)],
                order="id desc")
            if amazon_orders.mapped('picking_ids').filtered(lambda l:l.amazon_shipment_id == shipment_id):
                continue
            if order_wh_key not in order_details_dict:

                order_exist = False
                amazon_order = amazon_orders.filtered(lambda r: r and r.state in ['draft'])
                if amazon_order:
                    row.update({'instance': instance, 'amazon_order': amazon_order,
                                'fulfillment_center': fullfillment_center, 'warehouse': warehouse})
                    exist_order_details_dict.update({order_wh_key: row})
                    order_exist = True
                else:
                    new_order_details_dict.update({order_wh_key: row})
                    order_exist = False
                order_details_dict.update({order_wh_key: instance})
            else:
                if order_wh_key in exist_order_details_dict.keys():
                    order_exist = True
                else:
                    order_exist = False
            amazon_order_item_id = row.get('amazon-order-item-id', False)
            shipment_item_id =row.get('shipment-item-id')
            sku = row.get('sku', False)
            line_data = {
                'amazon_order_id': amazon_order_id,
                'amazon_order_item_id': row.get('amazon-order-item-id', False),
                'sku': sku,
                'item_price': row.get('item-price', 0.0) and float(row.get('item-price', 0.0)) or 0,
                'shipped_qty': float(row.get('quantity-shipped', 0.0)),
                'tax_amount': row.get('item-tax', 0.0) and float(row.get('item-tax', 0.0)) or 0,
                'name': row.get('product-name', ''),
                'shipping_charge': row.get('shipping-price', 0.0) and float(
                    row.get('shipping-price', 0.0)) or 0,
                'shipping_tax': row.get('shipping-tax', 0.0) and float(
                    row.get('shipping-tax', 0.0)) or 0,
                'shipping_discount': row.get('ship-promotion-discount', 0.0) and float(
                    row.get('ship-promotion-discount', 0.0)) or 0,
                'gift_wrapper_charge': row.get('gift-wrap-price', 0.0) and float(
                    row.get('gift-wrap-price', 0.0)) or 0,
                'gift_wrapper_tax': row.get('gift-wrap-tax', 0.0) and float(
                    row.get('gift-wrap-tax', 0.0)) or 0,
                'promotion_discount': row.get('item-promotion-discount', 0.0) and float(
                    row.get('item-promotion-discount', 0.0)) or 0,
                'fulfillment_center': fullfillment_center,
                'warehouse': warehouse,
            }
            wh_order_item_key = (warehouse, amazon_order_item_id)
            if order_exist:
                order_lines_details_dict = exist_order_lines_details_dict
            else:
                order_lines_details_dict = new_order_lines_details_dict
            if wh_order_item_key in order_lines_details_dict:
                order_lines_details_dict[wh_order_item_key]['item_price'] += line_data.get(
                    'item_price', 0.0)
                order_lines_details_dict[wh_order_item_key]['shipped_qty'] += line_data.get(
                    'shipped_qty', 0.0)
                order_lines_details_dict[wh_order_item_key]['tax_amount'] += line_data.get(
                    'tax_amount', 0.0)
                order_lines_details_dict[wh_order_item_key]['shipping_charge'] += line_data.get(
                    'shipping_charge', 0.0)
                order_lines_details_dict[wh_order_item_key]['shipping_tax'] += line_data.get(
                    'shipping_tax', 0.0)
                order_lines_details_dict[wh_order_item_key]['shipping_discount'] += line_data.get(
                    'shipping_discount', 0.0)
                order_lines_details_dict[wh_order_item_key]['gift_wrapper_charge'] += line_data.get(
                    'gift_wrapper_charge', 0.0)
                order_lines_details_dict[wh_order_item_key]['gift_wrapper_tax'] += line_data.get(
                    'gift_wrapper_tax', 0.0)
                order_lines_details_dict[wh_order_item_key]['promotion_discount'] += line_data.get(
                    'promotion_discount', 0.0)
            else:
                order_lines_details_dict.update({wh_order_item_key: line_data})
            if order_wh_key not in orders_lines_dict:
                orders_lines_dict.update({order_wh_key: [amazon_order_item_id]})
            else:
                orders_lines_dict[order_wh_key].append(amazon_order_item_id)

            tracking_number = row.get('tracking-number', '')
            ship_date = row.get('shipment-date', False)

            if (amazon_order_id, shipment_id, warehouse) not in shipment_details_dict:
                shipment_details_dict.update({(amazon_order_id, shipment_id, warehouse): [{
                    'amazon_reference': amazon_order_id,
                    'amazon_order_item_id': amazon_order_item_id,
                    'shipment_item_id':shipment_item_id,                    
                    'shipped_qty': float(row.get('quantity-shipped', 0.0)),
                    'sku': sku,
                    'tracking_number': tracking_number,
                    'ship_date': ship_date,
                    'estimated_arrival_date': row.get('estimated-arrival-date', False),
                    'purchase_date': row.get('purchase-date', False),
                    'shipment_date': row.get('shipment-date', False),
                    'carrier': row.get('carrier')
                }]})

            else:
                shipment_details_dict.get((amazon_order_id, shipment_id, warehouse)).append({
                    'amazon_reference': amazon_order_id,
                    'amazon_order_item_id': amazon_order_item_id,
                    'shipment_item_id':shipment_item_id,
                    'shipped_qty': float(row.get('quantity-shipped', 0.0)),
                    'sku': sku,
                    'tracking_number': tracking_number,
                    'ship_date': ship_date,
                    'estimated_arrival_date': row.get('estimated-arrival-date', False),
                    'purchase_date': row.get('purchase-date', False),
                    'shipment_date': row.get('shipment-date', False),
                    'carrier': row.get('carrier')
                })

        if len(outbound_order_rows) > 0:
            self.process_outbound_orders(outbound_order_rows)

        odoo_order_wh_dict = {}
        new_order_references = []
        for order_wh, row in new_order_details_dict.items():
            warehouse = order_wh[1]
            order_ref = order_wh[0]

            instance = order_details_dict.get(order_wh)
            if order_ref in new_order_references:
                amazon_order = order_obj.search(
                    [('amazon_reference', '=', order_ref), ('amz_instance_id', '=', instance.id)],
                    order="id desc")
                if amazon_order and amazon_order[0].warehouse_id.id == warehouse.id:
                    continue
                else:
                    new_amazon_order = self.copy_amazon_order(amazon_order[0], warehouse, instance)
                    new_amazon_order.write(
                        {'amz_instance_id': instance.id, 'date_order': amazon_order[0].date_order})
                    odoo_order_ids.append(new_amazon_order.id)
                    odoo_order_wh_dict.update({order_wh: new_amazon_order})
                    continue
            amazon_order = self.create_amazon_order(instance, warehouse, row)
            odoo_order_wh_dict.update({order_wh: amazon_order})
            odoo_order_ids.append(amazon_order.id)
            new_order_references.append(order_ref)
        for wh_order_item_key, line_data in new_order_lines_details_dict.items():
            warehouse = wh_order_item_key[0]
            order_id = line_data.get('amazon_order_id')
            amazon_order = odoo_order_wh_dict.get((order_id, warehouse))
            self.create_sale_order_line(amazon_order, line_data)

        already_taken_orders = []
        for order_wh, row in exist_order_details_dict.items():
            warehouse = order_wh[1]
            instance = order_details_dict.get(order_wh)
            amazon_order = row.get('amazon_order')
            order_item_ids = orders_lines_dict.get(order_wh, [])
            order_item_ids = list(set(order_item_ids))
            if len(amazon_order) == 1 and amazon_order.state in ['draft', 'sent']:
                if amazon_order.id in already_taken_orders:
                    new_amazon_order = self.copy_amazon_order(amazon_order, warehouse, instance)
                    new_amazon_order.write(
                        {'amz_instance_id': instance.id, 'date_order': amazon_order.date_order})
                    already_taken_orders.append(new_amazon_order.id)
                    odoo_order_wh_dict.update({order_wh: new_amazon_order})
                    odoo_order_ids.append(new_amazon_order.id)
                else:
                    already_taken_orders.append(amazon_order.id)
                    if amazon_order.warehouse_id.id != warehouse.id:
                        amazon_order.write({'warehouse_id': warehouse.id})
                    self.update_amazon_order(amazon_order, row)
                    odoo_order_wh_dict.update({order_wh: amazon_order})
                    odoo_order_ids.append(amazon_order.id)

        order_line_obj = self.env['sale.order.line']
        for wh_order_item_key, line_data in exist_order_lines_details_dict.items():
            warehouse = wh_order_item_key[0]
            order_id = line_data.get('amazon_order_id')
            amazon_order_item_id = line_data.get('amazon_order_item_id')
            amazon_order = odoo_order_wh_dict.get((order_id, warehouse))
            if not amazon_order:
                continue
            shipped_qty = line_data.get('shipped_qty', 0.0)
            amazon_line_rec = order_line_obj.search(
                [('amazon_order_item_id', '=', amazon_order_item_id),
                 ('order_id', '=', amazon_order.id)])
            if not amazon_line_rec:
                amazon_line_rec = order_line_obj.search(
                    [('amazon_order_item_id', '=', amazon_order_item_id),
                     ('order_id.amazon_reference', '=', amazon_order.amazon_reference)])
            if not amazon_line_rec:
                amazon_line_rec = self.create_sale_order_line(amazon_order, line_data)
            else:
                amazon_line_rec = amazon_line_rec[0]
                self.update_sale_order_line(amazon_order, amazon_line_rec, line_data)
            if round(shipped_qty, 2) != round(amazon_line_rec.product_uom_qty, 2):
                if not split_order_line_dict.get((amazon_order, warehouse), []):
                    split_order_line_dict[(amazon_order, warehouse)] = {
                        amazon_line_rec: shipped_qty}
                else:
                    split_order_line_dict[(amazon_order, warehouse)].update(
                        {amazon_line_rec: shipped_qty})

        if split_order_line_dict:
            self.split_order(split_order_line_dict)
        for order_wh, amazon_order in odoo_order_wh_dict.items():
            order_item_ids = orders_lines_dict.get(order_wh, [])
            order_item_ids = list(set(order_item_ids))
            ship_item_ids = []
            for order_item_id in order_item_ids:
                ship_item_ids += [order_item_id + '_ship', order_item_id + '_ship_discount',
                                  order_item_id + '_gift_wrap', order_item_id + '_promo_discount']
            order_item_ids += ship_item_ids
            amazon_line_ship_recs = order_line_obj.search(
                [('amazon_order_item_id', 'not in', order_item_ids),
                 ('order_id', '=', amazon_order.id)])
            if amazon_line_ship_recs:
                amazon_line_ship_recs.unlink()
        print("Start confirming orders")
        if odoo_order_ids:
            odoo_order_ids = list(set(odoo_order_ids))
            order_ids = order_obj.browse(odoo_order_ids)

            """Added by Dhruvi [10-09-2018]
                Loop for confirming sale order
                It calls fba_auto_workflow_process to create and validate invoice."""
            for order_id in order_ids:
                print(order_id)
                order_id.action_confirm()
                order_id.write({'confirmation_date': order_id.date_order})
            self.fba_auto_workflow_process(ids=odoo_order_ids)
            print("Start processing delivery order ")
            self.process_delivery_orders_new(shipment_details_dict, odoo_order_wh_dict)

        self.write({'state': 'processed'})
        return True

    @api.multi
    def get_set_product(self, move, product):
        try:
            bom_obj = self.env['mrp.bom']
            bom_point = bom_obj.sudo()._bom_find(product=product)
            from_uom = move.product_uom
            to_uom = bom_point.product_uom_id
            factor = from_uom._compute_quantity(1, to_uom) / bom_point.product_qty
            bom, lines = bom_point.explode(product, factor,
                                           picking_type=bom_point.picking_type_id)
            return lines
        except:
            return {}

    @api.model
    def get_order_sequence(self, amazon_order, order_sequence):
        order_obj = self.env['sale.order']
        new_name = "%s%s" % (
            amazon_order.amz_instance_id.seller_id.fba_order_prefix and amazon_order.amz_instance_id.seller_id.fba_order_prefix + '_' or '',
            amazon_order.amazon_reference)
        new_name = new_name + '/' + str(order_sequence)
        if order_obj.search([('name', '=', new_name)]):
            order_sequence = order_sequence + 1
            return self.get_order_sequence(amazon_order, order_sequence)
        else:
            return new_name

    @api.model
    def copy_amazon_order(self, amazon_order, warehouse, new_instance=False):
        workflow_id = amazon_order.auto_workflow_process_id and \
                      amazon_order.auto_workflow_process_id.id or False
        new_default_value = {'order_line': None, 'warehouse_id': warehouse.id,
                             'auto_workflow_process_id': workflow_id,
                             'amz_shipment_report_id': self.id}
        if not amazon_order.amz_instance_id.seller_id.is_default_odoo_sequence_in_sales_order_fba:
            new_name = self.get_order_sequence(amazon_order, 1)
            new_default_value.update({'name': new_name})
        new_sale_order = amazon_order.copy(default=new_default_value)
        new_sale_order.onchange_warehouse_id()
        return new_sale_order

    @api.model
    def split_order(self, split_order_line_dict):
        order_obj = self.env['sale.order']
        new_orders = order_obj.browse()
        for order, lines in split_order_line_dict.items():
            order_record = order[0]
            warehouse = order[1]
            new_amazon_order = self.copy_amazon_order(order_record, warehouse)
            new_amazon_order.write({'amz_shipment_report_id': False})
            for line, shipped_qty in lines.items():
                line.copy(default={'order_id': new_amazon_order.id,
                                   'product_uom_qty': (line.product_uom_qty - shipped_qty)})
                line.write({'product_uom_qty': shipped_qty})
            new_orders += new_amazon_order

        return new_orders

    @api.multi
    def create_amazon_order(self, instance, warehouse, row):
        order_obj = self.env['sale.order']
        sale_order_obj = self.env['sale.order']
        carrier_code = row.get('carrier', '')
        carrier_id = False
        amazon_exist_order = order_obj.search(
            [('amazon_reference', '=', row.get('amazon-order-id', ''))], order="id desc", limit=1)
        order_name = False
        if not instance.seller_id.is_default_odoo_sequence_in_sales_order_fba:
            if amazon_exist_order:
                order_name = self.get_order_sequence(amazon_exist_order, 1)
            else:
                order_name = "%s%s" % (
                    instance.seller_id.fba_order_prefix and instance.seller_id.fba_order_prefix + '_' or '',
                    row.get('amazon-order-id', ''))
        if carrier_code:
            """Modified by Dhruvi shipment_charge_product_id is fetched according to seller wise"""
            carrier_id = self.get_shipping_method(carrier_code,
                                                  instance.seller_id.shipment_charge_product_id)
        partner_dict = self.create_or_update_partner_amazon(instance, row)
        warehouse = warehouse or instance.fba_warehouse_id and \
                    instance.fba_warehouse_id or \
                    instance.warehouse_id
        date_order = False
        if row.get('purchase-date', False):
            date_order = parser.parse(row.get('purchase-date', False)).astimezone(utc).strftime(
                '%Y-%m-%d %H:%M:%S')
        else:
            date_order = time.strftime('%Y-%m-%d %H:%M:%S')

        vals = {'company_id': instance.company_id.id,
                'partner_id': partner_dict.get('invoice_address'),
                'partner_invoice_id': partner_dict.get('invoice_address'),
                'partner_shipping_id': partner_dict.get('delivery_address'),
                'warehouse_id': warehouse.id,
                'picking_policy': instance.seller_id.fba_auto_workflow_id and
                                  instance.seller_id.fba_auto_workflow_id.picking_policy or
                                  instance.picking_policy,
                'date_order': date_order,
                'pricelist_id': instance.pricelist_id.id or False,
                'payment_term_id': instance.seller_id.payment_term_id.id or False,
                'fiscal_position_id': False,
                'invoice_policy': instance.invoice_policy or False,
                'team_id': instance.team_id and instance.team_id.id or False,
                'client_order_ref': row.get('amazon-order-id', '') or False,
                'carrier_id': carrier_id, 'invoice_shipping_on_delivery': False
                }

        order_vals = sale_order_obj.create_sales_order_vals_ept(vals)
        order_vals.update(
            {
                'auto_workflow_process_id': instance.seller_id.fba_auto_workflow_id and
                                            instance.seller_id.fba_auto_workflow_id.id or
                                            instance.seller_id.auto_workflow_id and
                                            instance.seller_id.auto_workflow_id.id or False,
                'amz_instance_id': instance and instance.id or False,
                'amazon_reference': row.get('amazon-order-id', False),
                'amz_shipment_service_level_category': row.get('ship-service-level', False),
                'global_channel_id': instance.seller_id and instance.seller_id.global_channel_id and
                                     instance.seller_id.global_channel_id.id or False,
                'seller_id': instance.seller_id and instance.seller_id.id or False,
                'amz_fulfillment_by': 'AFN',
                'amz_shipment_report_id': self.id,
            })
        extra_vals = self.prepare_extra_order_vals(instance, row)
        extra_vals and order_vals.update(extra_vals)
        if order_name:
            order_vals.update({'name': order_name})
        fpos_id = instance.fiscal_position_id and instance.fiscal_position_id.id or False
        if not order_vals.get('fiscal_position_id', False) and fpos_id:
            order_vals.update({'fiscal_position_id': fpos_id})
        return order_obj.create(order_vals)

    @api.model
    def update_amazon_order(self, amazon_order, row):
        carrier_code = row.get('carrier', '')
        carrier_id = False
        instance = amazon_order.amz_instance_id
        if carrier_code:
            """Modified method argument by Dhruvi of shipment_charge_product by seller wise"""
            carrier_id = self.get_shipping_method(carrier_code,
                                                  instance.seller_id.shipment_charge_product_id)
        partner_dict = self.create_or_update_partner_amazon(instance, row)
        fpos_id = instance.fiscal_position_id and instance.fiscal_position_id.id or False
        amazon_order.write({
            'partner_invoice_id': partner_dict.get('invoice_address'),
            'partner_id': partner_dict.get('invoice_address'),
            'partner_shipping_id': partner_dict.get('delivery_address'),
            'fiscal_position_id': fpos_id

        })
        amazon_order.onchange_warehouse_id()
        order_vals = {}
        date_order = False
        if row.get('purchase-date', False):
            date_order = parser.parse(row.get('purchase-date', False)).astimezone(utc).strftime(
                '%Y-%m-%d %H:%M:%S')
        else:
            date_order = time.strftime('%Y-%m-%d %H:%M:%S')
            """Changes by Dhruvi fba_auto_worflow_id is fetched according to seller wise."""
        order_vals.update({
            'date_order': date_order,
            'pricelist_id': instance.pricelist_id.id,
            'amz_shipment_service_level_category': row.get('ship-service-level', 'Standard'),
            'carrier_id': carrier_id,
            'auto_workflow_process_id': instance.seller_id.fba_auto_workflow_id and
                                        instance.seller_id.fba_auto_workflow_id.id or
                                        instance.seller_id.auto_workflow_id and
                                        instance.seller_id.auto_workflow_id.id or False,

            'invoice_policy': instance.invoice_policy or False,
            'amz_fulfillment_by': 'AFN',
            'amz_shipment_report_id': self.id
        })
        amazon_order.write(order_vals)
        return True

    def get_shipping_method(self, ship_method, ship_product):
        delivery_carrier_obj = self.env['delivery.carrier']
        ship_method = ship_method.replace(' ', '')

        carrier = delivery_carrier_obj.search([('amz_delivery_carrier_code.name', '=ilike', ship_method)], limit=1)
        if not carrier:
            carrier = delivery_carrier_obj.search([('name', '=', ship_method)], limit=1)
        if carrier:
            return carrier.id
        else:
            amz_delivery_carrier_obj = self.env['amazon.delivery.carrier.code.ept']
            carrier_code = amz_delivery_carrier_obj.create({'name': ship_method})
            carrier = delivery_carrier_obj.create({
                'name': ship_method,
                'product_id': ship_product.id,
                'amz_delivery_carrier_code': carrier_code.id})
        return carrier.id

    @api.multi
    def create_or_update_partner_amazon(self, instance, row):
        return_partner = {}
        partner = False
        partner_obj = self.env['res.partner']
        sale_order_obj = self.env['sale.order']
        email = row.get('buyer-email', False)
        name = row.get('buyer-name', False)
        phone = row.get('buyer-phone-number', False)

        ship_name = row.get('recipient-name', False)
        ship_add1 = row.get('ship-address-1', False)
        ship_add2 = row.get('ship-address-2', False)
        ship_add3 = row.get('ship-address-3', False)
        ship_city = row.get('ship-city', False)
        ship_state = row.get('ship-state', False).capitalize()
        ship_country = row.get('ship-country', False)
        ship_postal_code = row.get('ship-postal-code', False)
        ship_phone = row.get('ship-phone-number', False)

        bill_add1 = row.get('bill-address-1', False)
        bill_add2 = row.get('bill-address-2', False)
        bill_add3 = row.get('bill-address-3', False)
        bill_city = row.get('bill-city', False)
        bill_state = row.get('bill-state', False).capitalize()
        bill_country = row.get('bill-country', False)
        bill_postal_code = row.get('bill-postal-code', False)

        ship_address_same = False
        if ship_add1.lower() == bill_add1.lower() and ship_add2.lower() == bill_add2.lower() and ship_add3.lower() == bill_add3.lower() and ship_city.lower() == bill_city.lower() and \
                ship_state.lower() == bill_state.lower() and ship_postal_code.lower() == bill_postal_code.lower() and ship_country.lower() == bill_country.lower():
            ship_address_same = True

        partner_id = instance.partner_id and instance.partner_id.id or False

        if instance.partner_id and instance.partner_id.property_product_pricelist.id != instance.pricelist_id.id:
            instance.partner_id.write({'property_product_pricelist': instance.pricelist_id.id})

        domain = []
        bill_add1 and domain.append(('street'))
        if bill_add2 or bill_add3:
            domain.append(('street2'))
        email and domain.append(('email'))
        phone and domain.append(('phone'))
        bill_city and domain.append(('city'))
        bill_postal_code and domain.append(('zip'))
        bill_state and domain.append(('state_id'))
        bill_country and domain.append(('country_id'))

        vals = {
            'state_code': bill_state or False,
            'state_name': bill_state or False,
            'country_code': bill_country or False,
            'country_name': bill_country or False,
            'name': name,
            'parent_id': partner_id,
            'street': bill_add1,
            'street2': False,
            'city': bill_city,
            'phone': phone,
            'email': email,
            'zip': bill_postal_code,
            'lang': instance.lang_id and instance.lang_id.code,
            'company_id': instance.company_id.id,
            'type': False,
            'is_company': False
        }

        if bill_add2 and bill_add3:
            bill_add2 = bill_add2 + ' ' + bill_add3
            vals.update({'street2': bill_add2})
        elif bill_add2:
            vals.update({'street2': bill_add2})
        elif bill_add3:
            vals.update({'street2': bill_add3})

        partnervals = sale_order_obj._prepare_amazon_partner_vals(vals)

        partnervals.update({'customer': True})

        if instance.amazon_property_account_payable_id:
            partnervals.update({'property_account_payable_id': instance.amazon_property_account_payable_id.id})

        if instance.amazon_property_account_receivable_id:
            partnervals.update({'property_account_receivable_id': instance.amazon_property_account_receivable_id.id})

        if instance.customer_is_company and not partner_id:
            partnervals.update({'is_company': True})

        if instance.pricelist_id:
            partnervals.update({'property_product_pricelist': instance.pricelist_id.id})

        invoice_partner = partner_obj._find_partner(partnervals, domain)
        if invoice_partner:
            invoice_partner = invoice_partner[0]
            if instance.amazon_property_account_payable_id:
                invoice_partner.update({'property_account_payable_id': instance.amazon_property_account_payable_id.id})

            if instance.amazon_property_account_receivable_id:
                invoice_partner.update(
                    {'property_account_receivable_id': instance.amazon_property_account_receivable_id.id})

            return_partner.update({'invoice_address': invoice_partner.id,
                                   'pricelist_id': invoice_partner.property_product_pricelist.id,
                                   'delivery_address': invoice_partner.id})
        else:
            partnervals.update({'type': 'invoice', 'name': name})
            if 'message_follower_ids' in partnervals:
                del partnervals['message_follower_ids']

            invoice_partner = partner_obj.create(partnervals)
            invoice_partner and return_partner.update({'invoice_address': invoice_partner.id,
                                                       'pricelist_id': invoice_partner.property_product_pricelist.id,
                                                       'delivery_address': invoice_partner.id})

        if not ship_address_same:
            domain = []
            ship_add1 and domain.append(('street'))
            if ship_add2 or ship_add3:
                domain.append(('street2'))
            email and domain.append(('email'))
            ship_phone and domain.append(('phone'))
            ship_city and domain.append(('city'))
            ship_postal_code and domain.append(('zip'))
            ship_state and domain.append(('state_id'))
            ship_country and domain.append(('country_id'))

            vals = {
                'state_code': ship_state or False,
                'state_name': ship_state or False,
                'country_code': ship_country or False,
                'country_name': ship_country or False,
                'name': ship_name,
                'parent_id': partner_id or invoice_partner.id,
                'street': ship_add1,
                'street2': False,
                'city': ship_city,
                'phone': ship_phone,
                'email': email,
                'zip': ship_postal_code,
                'lang': instance.lang_id and instance.lang_id.code,
                'company_id': instance.company_id.id,
                'type': False,
                'is_company': False
            }

            if ship_add2 and ship_add3:
                ship_add2 = ship_add2 + ' ' + ship_add3
                vals.update({'street2': ship_add2})
            elif ship_add2:
                vals.update({'street2': ship_add2})
            elif ship_add3:
                vals.update({'street2': ship_add3})

            partnervals = sale_order_obj._prepare_amazon_partner_vals(vals)

            partnervals.update({'customer': False})

            if instance.amazon_property_account_payable_id:
                partnervals.update({'property_account_payable_id': instance.amazon_property_account_payable_id.id})

            if instance.amazon_property_account_receivable_id:
                partnervals.update(
                    {'property_account_receivable_id': instance.amazon_property_account_receivable_id.id})

            if instance.pricelist_id:
                partnervals.update({'property_product_pricelist': instance.pricelist_id.id})

            exist_partner = partner_obj._find_partner(partnervals, domain)
            if exist_partner:
                if instance.amazon_property_account_payable_id:
                    exist_partner[0].update(
                        {'property_account_payable_id': instance.amazon_property_account_payable_id.id})

                if instance.amazon_property_account_receivable_id:
                    exist_partner[0].update(
                        {'property_account_receivable_id': instance.amazon_property_account_receivable_id.id})

                return_partner.update({'delivery_address': exist_partner[0].id})
            else:
                partnervals.pop('message_follower_ids', '')

                partnervals.update({'type': 'delivery', 'name': ship_name})
                partner = partner_obj.create(partnervals)
                return_partner.update({'delivery_address': partner.id,
                                       'pricelist_id': partner.property_product_pricelist.id})

            if not instance.customer_is_company and not partner_id:
                invoice_partner.write({'is_company': True})
        return return_partner

    def process_delivery_orders_new(self, shipment_dict, odoo_order_wh_dict):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        quant_package_obj = self.env["stock.quant.package"]
        auto_work_flow_obj = self.env['sale.workflow.process.ept']
        amazon_product_obj = self.env['amazon.product.ept']
        product_obj = self.env['product.product']
        stock_move_line_obj = self.env['stock.move.line']
        shipment_report_history_obj = self.env['shipping.report.order.history']
        pick_ids = []
        for shipment_order, datas in shipment_dict.items():
            
            order_id = shipment_order[0]
            shipment_id = shipment_order[1]
            warehouse = shipment_order[2]
            amazon_order = odoo_order_wh_dict.get((order_id, warehouse))
            if not amazon_order:
                continue
            if not amazon_order.picking_ids:
                workflow_id = amazon_order.auto_workflow_process_id and \
                              amazon_order.auto_workflow_process_id.id or False
                if not workflow_id:
                    continue
                odoo_order_ids = [amazon_order.id]
                auto_work_flow_obj.auto_workflow_process(workflow_id, odoo_order_ids)

            if not amazon_order.picking_ids:
                continue
            elif len(amazon_order.picking_ids) > 1:
                pickings = picking_obj.search(
                    [('state', 'in', ['confirmed', 'assigned', 'partially_available']),
                     ('id', 'in', amazon_order.picking_ids.ids),
                     ('picking_type_id.warehouse_id', '=', warehouse and warehouse.id)
                     ])

                if not pickings:
                    continue
            else:
                pickings = amazon_order.picking_ids
            amazon_order.invoice_shipping_on_delivery = False
            pickings.action_confirm()
            if not amazon_order.auto_workflow_process_id.auto_check_availability:
                pickings.action_assign()
            for picking in pickings:
                for data in datas:
                    shipment_report_history_obj.create({'instance_id':amazon_order.amz_instance_id.id
                                                        ,'amazon_order_ref':order_id,
                                                        'order_line_ref':data.get('amazon_order_item_id'),
                                                        'shipment_id':shipment_id,
                                                        'shipment_line_id':data.get('shipment_item_id')
                                                        })

                    move_exist = False
                    picking_vals = {}
                    file_qty = float(data.get('shipped_qty', 0))
                    if not amazon_order.amz_instance_id.manage_multi_tracking_number_in_delivery_order and not picking.carrier_tracking_ref:
                        picking_vals.update(
                            {
                                'carrier_tracking_ref': data.get('tracking_number', False)
                            }
                        )
                    if not picking.amazon_shipment_date or not picking.amazon_purchase_date or not picking.estimated_arrival_date:
                        picking_vals.update(
                            {
                                'estimated_arrival_date': data.get(
                                    'estimated_arrival_date') and data.get(
                                    'estimated_arrival_date') or False,
                                'amazon_shipment_date': data.get('shipment_date') and data.get(
                                    'shipment_date') or False,
                                'amazon_purchase_date': data.get('purchase_date') and data.get(
                                    'purchase_date') or False,
                                'date_done': data.get('shipment_date') and data.get(
                                    'shipment_date') or datetime.now(),
                            }
                        )
                    '''if not picking.amazon_shipment_id or not picking.carrier_id:
                        picking_vals.update({'amazon_shipment_id':shipment_id,'date_done':datetime.now()})
                        if amazon_order.carrier_id and amazon_order.carrier_id.amazon_code != data.get('carrier',''):
                            carrier_id = self.get_shipping_method(data.get('carrier',''), amazon_order.amz_instance_id.shipment_charge_product_id)
                            if carrier_id:
                                picking_vals.update({'carrier_id':carrier_id})'''
                    if not picking.carrier_id:
                        carrier_code = data.get('carrier', '')
                        carrier_code = carrier_code.replace(' ', '')
                        if amazon_order.carrier_id and \
                                amazon_order.carrier_id.amz_delivery_carrier_code and \
                                amazon_order.carrier_id.amz_delivery_carrier_code.name != carrier_code:
                            carrier_id = self.get_shipping_method(data.get('carrier', ''),
                                                                  amazon_order.amz_instance_id.seller_id.shipment_charge_product_id)
                            if carrier_id:
                                picking_vals.update({'carrier_id': carrier_id})
                    picking_vals and picking.write(picking_vals)
                    package = False
                    if amazon_order.amz_instance_id.manage_multi_tracking_number_in_delivery_order:
                        package = quant_package_obj.search(
                            [('tracking_no', '=', data.get('tracking_number', False))])
                        if not package:
                            package = quant_package_obj.create(
                                {'tracking_no': data.get('tracking_number', False)})

                    sku = data.get('sku')
                    amazon_product = amazon_product_obj.search_amazon_product(
                        amazon_order.amz_instance_id.id, sku, 'AFN')
                    product = amazon_product and amazon_product.product_id or False
                    if not product:
                        product = product_obj.search([('default_code', '=', sku)], limit=1)
                    move_lines = move_obj.search(
                        [('picking_id', '=', picking.id), ('product_id', '=', product.id),
                         ('state', 'in', ('confirmed', 'assigned', 'partially_available'))])
                    is_kit_product = False
                    if not move_lines:
                        move_lines = move_obj.search([('picking_id', '=', picking.id),
                                                      ('sale_line_id.product_id', '=', product.id),
                                                      ('state', 'in', ('confirmed', 'assigned',
                                                                       'partially_available'))])
                        is_kit_product = True
                    if not move_lines:
                        continue
                    if not is_kit_product:
                        qty_left = file_qty
                        for move in move_lines:
                            if qty_left <= 0.0:
                                break
                            move_exist = True
                            move_line_remaning_qty = (move.product_uom_qty) - (
                                sum(move.move_line_ids.mapped('qty_done')))
                            operations = move.move_line_ids.filtered(
                                lambda o: o.qty_done <= 0 and not o.result_package_id)
                            for operation in operations:
                                if operation.product_uom_qty <= qty_left:
                                    op_qty = operation.product_uom_qty
                                else:
                                    op_qty = qty_left
                                operation.write({'qty_done': op_qty})
                                self._put_in_pack_ept(operation, package)
                                qty_left = float_round(qty_left - op_qty,
                                                       precision_rounding=operation.product_uom_id.rounding,
                                                       rounding_method='UP')
                                move_line_remaning_qty = move_line_remaning_qty - op_qty
                                if qty_left <= 0.0:
                                    break
                            if qty_left > 0.0 and move_line_remaning_qty > 0.0:
                                if move_line_remaning_qty <= qty_left:
                                    op_qty = move_line_remaning_qty
                                else:
                                    op_qty = qty_left
                                stock_move_line_obj.create(
                                    {
                                        'product_id': move.product_id.id,
                                        'product_uom_id': move.product_id.uom_id.id,
                                        'picking_id': picking.id,
                                        'qty_done': float(op_qty) or 0,
                                        'ordered_qty': float(op_qty) or 0,
                                        'result_package_id': package and package.id or False,
                                        'location_id': picking.location_id.id,
                                        'location_dest_id': picking.location_dest_id.id,
                                        'move_id': move.id,
                                    })
                                qty_left = float_round(qty_left - op_qty,
                                                       precision_rounding=move.product_id.uom_id.rounding,
                                                       rounding_method='UP')
                                if qty_left <= 0.0:
                                    break
                        if qty_left > 0.0:
                            stock_move_line_obj.create(
                                {
                                    'product_id': move_lines[0].product_id.id,
                                    'product_uom_id': move_lines[0].product_id.uom_id.id,
                                    'picking_id': picking.id,
                                    'ordered_qty': float(qty_left) or 0,
                                    'qty_done': float(qty_left) or 0,
                                    'result_package_id': package and package.id or False,
                                    'location_id': picking.location_id.id,
                                    'location_dest_id': picking.location_dest_id.id,
                                    'move_id': move_lines[0].id,
                                })
                        pick_ids.append(picking.id)
                    else:
                        one_set_product_dict = self.get_set_product(move_lines[0], product)
                        if not one_set_product_dict:
                            continue
                        transfer_product_qty = {}
                        for bom_line, line_data in one_set_product_dict:
                            qty = line_data['qty']
                            product_id = bom_line.product_id.id
                            transfer_product_qty.update({product_id: qty})
                        for product_id, bom_qty in transfer_product_qty.items():
                            file_qty = float(data.get('shipped_qty', 0))
                            if bom_qty <= 0.0:
                                continue
                            if transfer_product_qty.get(product_id) <= 0.0:
                                continue
                            qty_left = file_qty * bom_qty
                            product_move_lines = move_lines.filtered(
                                lambda move_line: move_line.product_id.id == product_id)
                            for product_move_line in product_move_lines:
                                operations = product_move_line.move_line_ids.filtered(
                                    lambda o: o.qty_done <= 0 and not o.result_package_id)
                                move_line_remaning_qty = (product_move_line.product_uom_qty) - (
                                    sum(product_move_line.move_line_ids.mapped('qty_done')))
                                move_exist = True
                                for operation in operations:
                                    if operation.product_uom_qty <= qty_left:
                                        op_qty = operation.product_uom_qty
                                    else:
                                        op_qty = qty_left
                                    operation.write({'qty_done': op_qty})
                                    self._put_in_pack_ept(operation, package)
                                    qty_left = float_round(qty_left - op_qty,
                                                           precision_rounding=operation.product_uom_id.rounding,
                                                           rounding_method='UP')
                                    move_line_remaning_qty = move_line_remaning_qty - op_qty
                                    if qty_left <= 0.0:
                                        transfer_product_qty.update({product_id: 0.0})
                                        break
                                if qty_left > 0.0 and move_line_remaning_qty > 0.0:
                                    if move_line_remaning_qty <= qty_left:
                                        op_qty = move_line_remaning_qty
                                    else:
                                        op_qty = qty_left
                                    stock_move_line_obj.create(
                                        {
                                            'product_id': product_move_line.product_id.id,
                                            'product_uom_id': product_move_line.product_id.uom_id.id,
                                            'picking_id': picking.id,
                                            'qty_done': float(op_qty) or 0,
                                            'ordered_qty': float(op_qty) or 0,
                                            'result_package_id': package and package.id or False,
                                            'location_id': picking.location_id.id,
                                            'location_dest_id': picking.location_dest_id.id,
                                            'move_id': product_move_line.id,
                                        })
                                    qty_left = float_round(qty_left - op_qty,
                                                           precision_rounding=product_move_line.product_id.uom_id.rounding,
                                                           rounding_method='UP')
                                    if qty_left <= 0.0:
                                        transfer_product_qty.update({product_id: 0.0})
                                        break
                            if qty_left > 0.0:
                                stock_move_line_obj.create(
                                    {
                                        'product_id': product_move_lines[0].product_id.id,
                                        'product_uom_id': product_move_lines[
                                            0].product_id.uom_id.id,
                                        'picking_id': picking.id,
                                        'qty_done': float(qty_left) or 0,
                                        'ordered_qty': float(op_qty) or 0,
                                        'result_package_id': package and package.id or False,
                                        'location_id': picking.location_id.id,
                                        'location_dest_id': picking.location_dest_id.id,
                                        'move_id': product_move_lines[0].id,
                                    })
                        pick_ids.append(picking.id)
                if move_exist:
                    picking.write({'amazon_shipment_id': shipment_id})
                if picking.state == 'assigned':
                    picking.with_context({'auto_processed_orders_ept': True}).action_done()
                if picking.state != 'done':
                    picking.with_context({'auto_processed_orders_ept': True}).action_done()
        '''if pick_ids:
            pickings=picking_obj.search([('state','=','assigned'),('id','in',list(set(pick_ids)))])  
            pickings and pickings.action_done()
            pickings=picking_obj.search([('state','!=','done'),('id','in',list(set(pick_ids)))])            
            pickings and pickings.action_done()'''
        #        pick_ids and  picking_obj.browse(list(set(pick_ids))).action_done()
        return True

    def process_delivery_orders_new_ept(self, shipment_dict, odoo_order_wh_dict):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        quant_package_obj = self.env["stock.quant.package"]
        auto_work_flow_obj = self.env['sale.workflow.process.ept']
        amazon_product_obj = self.env['amazon.product.ept']
        product_obj = self.env['product.product']
        stock_move_line_obj = self.env['stock.move.line']
        sale_order_line_obj = self.env['sale.order.line']
        for shipment_order, datas in shipment_dict.items():
            pick_ids = []
            order_id = shipment_order[0]
            shipment_id = shipment_order[1]
            warehouse = shipment_order[2]
            amazon_order = odoo_order_wh_dict.get((order_id, warehouse))
            if not amazon_order:
                continue
            if not amazon_order.picking_ids:
                workflow_id = amazon_order.auto_workflow_process_id and \
                              amazon_order.auto_workflow_process_id.id or False
                if not workflow_id:
                    continue
                odoo_order_ids = [amazon_order.id]
                auto_work_flow_obj.auto_workflow_process(workflow_id, odoo_order_ids)

            if not amazon_order.picking_ids:
                continue
            elif len(amazon_order.picking_ids) > 1:
                pickings = picking_obj.search(
                    [('state', 'in', ['confirmed', 'assigned', 'partially_available']),
                     ('id', 'in', amazon_order.picking_ids.ids),
                     ('picking_type_id.warehouse_id', '=', warehouse and warehouse.id)
                     ])

                if not pickings:
                    continue
            else:
                pickings = amazon_order.picking_ids
            amazon_order.invoice_shipping_on_delivery = False
            pickings.action_confirm()
            if not amazon_order.auto_workflow_process_id.auto_check_availability:
                pickings.action_assign()
            order_lines = sale_order_line_obj.search([('order_id', '=', amazon_order.id)])
            data_track = []
            for order_line in order_lines:
                if not order_line.product_packaging:
                    data_track.append('False')
                else:
                    data_track.append('True')
            for picking in pickings:
                for data in datas:

                    picking_vals = {}
                    file_qty = float(data.get('shipped_qty', 0))
                    # if not amazon_order.amz_instance_id.manage_multi_tracking_number_in_delivery_order and not picking.carrier_tracking_ref:
                    # if not amazon_order.order_line.product_packaging and not picking.carrier_tracking_ref: #condition changed by Dhruvi
                    if not 'True' in data_track and not picking.carrier_tracking_ref:
                        picking_vals.update(
                            {
                                'carrier_tracking_ref': data.get('tracking_number', False)
                            }
                        )
                    if not picking.amazon_shipment_date or not picking.amazon_purchase_date or \
                            not picking.estimated_arrival_date:
                        picking_vals.update(
                            {
                                'estimated_arrival_date': data.get(
                                    'estimated_arrival_date') and data.get(
                                    'estimated_arrival_date') or False,
                                'amazon_shipment_date': data.get('shipment_date') and data.get(
                                    'shipment_date') or False,
                                'amazon_purchase_date': data.get('purchase_date') and data.get(
                                    'purchase_date') or False,
                                'date_done': data.get('shipment_date') and data.get(
                                    'shipment_date') or datetime.now(),
                            }
                        )
                    if not picking.amazon_shipment_id or not picking.carrier_id:
                        picking_vals.update(
                            {'amazon_shipment_id': shipment_id, 'date_done': datetime.now()})
                        if amazon_order.carrier_id and amazon_order.carrier_id.amazon_code != data.get(
                                'carrier', ''):

                            """Modified by Dhruvi shipment_charge_product according to seller wise."""
                            carrier_id = self.get_shipping_method(data.get('carrier', ''),
                                                                  amazon_order.amz_instance_id.seller_id.shipment_charge_product_id)
                            if carrier_id:
                                picking_vals.update({'carrier_id': carrier_id})
                    picking_vals and picking.write(picking_vals)
                    package = False

                    # if amazon_order.amz_instance_id.manage_multi_tracking_number_in_delivery_order:
                    # if amazon_order.order_line.product_packaging: #condition changed by Dhruvi
                    if not 'False' in data_track:
                        package = quant_package_obj.search(
                            [('tracking_no', '=', data.get('tracking_number', False))])
                        if not package:
                            package = quant_package_obj.create(
                                {'tracking_no': data.get('tracking_number', False)})

                    sku = data.get('sku')
                    amazon_product = amazon_product_obj.search_amazon_product(
                        amazon_order.amz_instance_id.id, sku, 'AFN')
                    product = amazon_product and amazon_product.product_id or False
                    if not product:
                        product = product_obj.search([('default_code', '=', sku)], limit=1)
                    move_lines = move_obj.search(
                        [('picking_id', '=', picking.id), ('product_id', '=', product.id),
                         ('state', 'in', ('confirmed', 'assigned', 'partially_available'))])
                    is_kit_product = False
                    if not move_lines:
                        move_lines = move_obj.search([('picking_id', '=', picking.id),
                                                      ('sale_line_id.product_id', '=', product.id),
                                                      ('state', 'in', ('confirmed', 'assigned',
                                                                       'partially_available'))])
                        is_kit_product = True
                    if not move_lines:
                        continue
                    if not is_kit_product:
                        qty_left = file_qty
                        for move in move_lines:
                            if qty_left <= 0.0:
                                break
                            move_line_remaning_qty = (move.product_uom_qty) - (
                                sum(move.move_line_ids.mapped('qty_done')))
                            operations = move.move_line_ids.filtered(
                                lambda o: o.qty_done <= 0 and not o.result_package_id)
                            for operation in operations:
                                if operation.product_uom_qty <= qty_left:
                                    op_qty = operation.product_uom_qty
                                else:
                                    op_qty = qty_left
                                operation.write({'qty_done': op_qty})
                                self._put_in_pack_ept(operation, package)
                                qty_left = float_round(qty_left - op_qty,
                                                       precision_rounding=operation.product_uom_id.rounding,
                                                       rounding_method='UP')
                                move_line_remaning_qty = move_line_remaning_qty - op_qty
                                if qty_left <= 0.0:
                                    break
                            if qty_left > 0.0 and move_line_remaning_qty > 0.0:
                                if move_line_remaning_qty <= qty_left:
                                    op_qty = move_line_remaning_qty
                                else:
                                    op_qty = qty_left
                                stock_move_line_obj.create(
                                    {
                                        'product_id': move.product_id.id,
                                        'product_uom_id': move.product_id.uom_id.id,
                                        'picking_id': picking.id,
                                        'qty_done': float(op_qty) or 0,
                                        'ordered_qty': float(op_qty) or 0,
                                        'result_package_id': package and package.id or False,
                                        'location_id': picking.location_id.id,
                                        'location_dest_id': picking.location_dest_id.id,
                                        'move_id': move.id,
                                    })
                                qty_left = float_round(qty_left - op_qty,
                                                       precision_rounding=move.product_id.uom_id.rounding,
                                                       rounding_method='UP')
                                if qty_left <= 0.0:
                                    break
                        if qty_left > 0.0:
                            stock_move_line_obj.create(
                                {
                                    'product_id': move_lines[0].product_id.id,
                                    'product_uom_id': move_lines[0].product_id.uom_id.id,
                                    'picking_id': picking.id,
                                    'ordered_qty': float(qty_left) or 0,
                                    'qty_done': float(qty_left) or 0,
                                    'result_package_id': package and package.id or False,
                                    'location_id': picking.location_id.id,
                                    'location_dest_id': picking.location_dest_id.id,
                                    'move_id': move_lines[0].id,
                                })
                        pick_ids.append(picking.id)
                    else:
                        one_set_product_dict = self.get_set_product(move_lines[0], product)
                        if not one_set_product_dict:
                            continue
                        transfer_product_qty = {}
                        for bom_line, line_data in one_set_product_dict:
                            qty = line_data['qty']
                            product_id = bom_line.product_id.id
                            transfer_product_qty.update({product_id: qty})
                        for product_id, bom_qty in transfer_product_qty.items():
                            file_qty = float(data.get('shipped_qty', 0))
                            if bom_qty <= 0.0:
                                continue
                            if transfer_product_qty.get(product_id) <= 0.0:
                                continue
                            qty_left = file_qty * bom_qty
                            product_move_lines = move_lines.filtered(
                                lambda move_line: move_line.product_id.id == product_id)
                            for product_move_line in product_move_lines:
                                operations = product_move_line.move_line_ids.filtered(
                                    lambda o: o.qty_done <= 0 and not o.result_package_id)
                                move_line_remaning_qty = (product_move_line.product_uom_qty) - (
                                    sum(product_move_line.move_line_ids.mapped('qty_done')))
                                for operation in operations:
                                    if operation.product_uom_qty <= qty_left:
                                        op_qty = operation.product_uom_qty
                                    else:
                                        op_qty = qty_left
                                    operation.write({'qty_done': op_qty})
                                    self._put_in_pack_ept(operation, package)
                                    qty_left = float_round(qty_left - op_qty,
                                                           precision_rounding=operation.product_uom_id.rounding,
                                                           rounding_method='UP')
                                    move_line_remaning_qty = move_line_remaning_qty - op_qty
                                    if qty_left <= 0.0:
                                        transfer_product_qty.update({product_id: 0.0})
                                        break
                                if qty_left > 0.0 and move_line_remaning_qty > 0.0:
                                    if move_line_remaning_qty <= qty_left:
                                        op_qty = move_line_remaning_qty
                                    else:
                                        op_qty = qty_left
                                    stock_move_line_obj.create(
                                        {
                                            'product_id': product_move_line.product_id.id,
                                            'product_uom_id': product_move_line.product_id.uom_id.id,
                                            'picking_id': picking.id,
                                            'qty_done': float(op_qty) or 0,
                                            'ordered_qty': float(op_qty) or 0,
                                            'result_package_id': package and package.id or False,
                                            'location_id': picking.location_id.id,
                                            'location_dest_id': picking.location_dest_id.id,
                                            'move_id': product_move_line.id,
                                        })
                                    qty_left = float_round(qty_left - op_qty,
                                                           precision_rounding=product_move_line.product_id.uom_id.rounding,
                                                           rounding_method='UP')
                                    if qty_left <= 0.0:
                                        transfer_product_qty.update({product_id: 0.0})
                                        break
                            if qty_left > 0.0:
                                stock_move_line_obj.create(
                                    {
                                        'product_id': product_move_lines[0].product_id.id,
                                        'product_uom_id': product_move_lines[
                                            0].product_id.uom_id.id,
                                        'picking_id': picking.id,
                                        'qty_done': float(qty_left) or 0,
                                        'ordered_qty': float(op_qty) or 0,
                                        'result_package_id': package and package.id or False,
                                        'location_id': picking.location_id.id,
                                        'location_dest_id': picking.location_dest_id.id,
                                        'move_id': product_move_lines[0].id,
                                    })
                        pick_ids.append(picking.id)
            pick_ids and picking_obj.browse(list(set(pick_ids))).with_context(
                {'auto_processed_orders_ept': True}).action_done()
        return True

    def _put_in_pack_ept(self, operation, package):
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
                default={'product_uom_qty': 0, 'qty_done': operation.qty_done})
            operation.write({'product_uom_qty': quantity_left_todo, 'qty_done': 0.0})
            new_operation.write({'product_uom_qty': operation.qty_done})
            operation_ids |= new_operation
        package and operation_ids.write({'result_package_id': package.id})
        return True

    @api.model
    def get_warehouse(self, fulfillment_center_id, instance):
        fulfillment_center = self.env['amazon.fulfillment.center'].search(
            [('center_code', '=', fulfillment_center_id),
             ('seller_id', '=', instance.seller_id.id)])
        fulfillment_center = fulfillment_center and fulfillment_center[0]
        warehouse = fulfillment_center and fulfillment_center.warehouse_id or instance.fba_warehouse_id and instance.fba_warehouse_id or instance.warehouse_id or False
        return fulfillment_center, warehouse

    @api.model
    def get_fiscal_position(self, warehouse, amazon_order, is_order=False):
        warehouse_partner = warehouse.partner_id or warehouse.company_id.partner_id
        partner_id = False

        origin_country_id = warehouse_partner and warehouse_partner.country_id and \
                            warehouse_partner.country_id.id or False
        ctx = self._context.copy()
        ctx.update({'origin_country_ept': origin_country_id})
        fiscal_position = self.env['account.fiscal.position'].with_context(ctx).get_fiscal_position(
            amazon_order.company_id.id, partner_id,
            amazon_order.partner_shipping_id and amazon_order.partner_shipping_id.id)

        return fiscal_position

    @api.multi
    def get_item_price(self, item_price, tax_amount):
        item_price = item_price + float(tax_amount)
        return item_price

    @api.multi
    def calculate_tax_amount(self, item_price, tax_amount, shipped_qty):
        return tax_amount

    @api.model
    def create_sale_order_line(self, amazon_order, line_data, is_outbound_order=False):
        order_line_obj = self.env['sale.order.line']
        instance = amazon_order.amz_instance_id
        amazon_product = self.search_or_create_or_update_product(line_data, instance)
        item_price = float(line_data.get('item_price', 0.0))
        tax_amount = float(line_data.get('tax_amount', 0.0))
        item_price = self.get_item_price(item_price, tax_amount)
        price_dict = order_line_obj.calculate_order_qty_and_price_based_on_asin_qty(
            amazon_product, float(item_price), line_data.get('shipped_qty', 0.0))
        tax_amount = self.calculate_tax_amount(price_dict.get('amount_per_unit', 0.0), tax_amount,
                                               line_data.get('shipped_qty', 0.0))

        shipped_qty = float(line_data.get('shipped_qty', 0.0))
        fulfillment_center = line_data.get('fulfillment_center', '')
        tax_ids = amazon_product.taxes_id.ids
        if not is_outbound_order:
            qty_price_dict = order_line_obj.calculate_order_qty_and_price_based_on_asin_qty(
                amazon_product, float(item_price), shipped_qty)
            qty_price_dict.update({'amazon_order_qty': shipped_qty,
                                   'amazon_order_item_id': line_data.get('amazon_order_item_id')})
        else:
            qty_price_dict = {'order_qty': shipped_qty, 'amount_per_unit': item_price}

        title = line_data.get('name', '')

        order_line_vals = self.create_sale_order_line_vals(qty_price_dict, tax_ids, amazon_product,
                                                           amazon_product.product_id and amazon_product.product_id.id,
                                                           amazon_order, instance, title)
        order_line_vals.update({'line_tax_amount': tax_amount})
        if 'discount' in line_data:
            order_line_vals.update({'discount': line_data.get('discount')})

        fulfillment_center and order_line_vals.update(
            {'amz_fulfillment_center_id': fulfillment_center.id})

        amazon_line_rec = order_line_obj.create(order_line_vals)
        self.create_order_charges_line(amazon_line_rec, line_data)
        return amazon_line_rec

    @api.model
    def update_sale_order_line(self, amazon_order, amazon_line_rec, line_data):
        order_line_obj = self.env['sale.order.line']
        item_price = float(line_data.get('item_price', 0.0))

        tax_amount = float(line_data.get('tax_amount'))
        price_dict = order_line_obj.calculate_order_qty_and_price_based_on_asin_qty(
            amazon_line_rec.amazon_product_id, float(item_price), line_data.get('shipped_qty', 0.0))
        tax_amount = self.calculate_tax_amount(price_dict.get('amount_per_unit'), tax_amount,
                                               line_data.get('shipped_qty', 0.0))
        item_price = self.get_item_price(item_price, tax_amount)
        shipped_qty = float(line_data.get('shipped_qty', 0.0))
        fulfillment_center = line_data.get('fulfillment_center', '')

        amazon_product = amazon_line_rec.amazon_product_id
        qty_price_dict = order_line_obj.calculate_order_qty_and_price_based_on_asin_qty(
            amazon_product, item_price, shipped_qty)
        fpos = amazon_order.fiscal_position_id

        company_id = amazon_order.company_id.id
        taxes = fpos.map_tax(amazon_product.taxes_id)
        if company_id:
            tax_ids = []
            for tax in taxes:
                if company_id == tax.company_id.id:
                    tax_ids.append(tax.id)
        else:
            tax_ids = taxes.ids
        if tax_ids:
            tax_ids = [(6, 0, tax_ids)]

        orderline_vals = {
            'price_unit': qty_price_dict.get('amount_per_unit'),
            'tax_id': tax_ids,
            'amz_fulfillment_center_id': fulfillment_center and fulfillment_center.id or False,
            'line_tax_amount': tax_amount
        }
        amazon_line_rec.write(orderline_vals)
        amazon_line_rec.write({'order_id': amazon_order.id})
        self.create_order_charges_line(amazon_line_rec, line_data)
        return amazon_line_rec

    @api.model
    def create_order_charges_line(self, amazon_line_rec, line_data):
        order_line_obj = self.env['sale.order.line']
        amazon_order = amazon_line_rec.order_id
        instance = amazon_order.amz_instance_id
        amazon_product = self.search_or_create_or_update_product(line_data, instance)
        qty_price_dict = {}
        """Shipment Charge Line"""
        shipping_charge = float(line_data.get('shipping_charge', 0.0))
        shipping_tax = float(line_data.get('shipping_tax', 0.0))
        shipping_tax = self.calculate_tax_amount(shipping_charge, shipping_tax, 0.0)
        shipping_charge = self.get_item_price(shipping_charge, shipping_tax)
        if shipping_charge:
            shipment_product = False
            shipping_charge_description = ''
            amazon_line_ship_rec = order_line_obj.search(
                [('amazon_order_item_id', '=', amazon_line_rec.amazon_order_item_id + '_ship'),
                 ('order_id', '=', amazon_order.id)])

            """Change condition by Dhruvi shipment_charge_product according to seller wise"""
            if instance.seller_id.shipment_charge_product_id:
                shipment_product = instance.seller_id.shipment_charge_product_id
            elif amazon_order.carrier_id and amazon_order.carrier_id.product_id:
                shipment_product = amazon_order.carrier_id.product_id
            else:
                shipping_charge_description = "Shipping and Handling"

            tax_id = False
            qty_price_dict.update(
                {'order_qty': 1, 'amount_per_unit': shipping_charge, 'amazon_order_qty': 1,
                 'amazon_order_item_id': amazon_line_rec.amazon_order_item_id + '_ship'})
            order_line_vals = self.create_sale_order_line_vals(qty_price_dict, tax_id, False,
                                                               shipment_product and shipment_product.id or False,
                                                               amazon_order, instance, (
                                                                       shipping_charge_description and shipping_charge_description) or (
                                                                       shipment_product and shipment_product.name))
            order_line_vals.update({'is_delivery': True,
                                    'amazon_product_id': amazon_product.id,
                                    'line_tax_amount': shipping_tax})
            amazon_line_rec and amazon_line_rec.write({'amz_shipping_charge_ept': shipping_charge,
                                                       'amz_shipping_charge_tax': shipping_tax})
            if amazon_line_ship_rec:
                amazon_line_ship_rec.write(order_line_vals)
            else:
                order_line_obj.create(order_line_vals)

        """Shipment Discount Line"""
        shipping_discount = float(line_data.get('shipping_discount', 0.0))
        if shipping_discount:
            shipping_discount = self.get_item_price(abs(shipping_discount), shipping_tax)
            shipment_product = False
            shipping_discount_description = ''
            amazon_line_ship_rec = order_line_obj.search([('amazon_order_item_id', '=',
                                                           amazon_line_rec.amazon_order_item_id + '_ship_discount'),
                                                          ('order_id', '=', amazon_order.id)])

            """Changed by Dhruvi ship_discount_product according to seller wise."""
            if instance.seller_id.ship_discount_product_id:
                shipment_product = instance.seller_id.ship_discount_product_id
            else:
                shipping_discount_description = "Shipping Discount"

            qty_price_dict.update(
                {'order_qty': 1, 'amount_per_unit': -shipping_discount, 'amazon_order_qty': 1,
                 'amazon_order_item_id': amazon_line_rec.amazon_order_item_id + '_ship_discount'})
            order_line_vals = self.create_sale_order_line_vals(qty_price_dict, False, False,
                                                               shipment_product and shipment_product.id or False,
                                                               amazon_order, instance, (
                                                                       shipping_discount_description and shipping_discount_description) or (
                                                                       shipment_product and shipment_product.name))
            order_line_vals.update({'amazon_product_id': amazon_product.id})

            amazon_line_rec and amazon_line_rec.write(
                {'amz_shipping_discount_ept': -shipping_discount})
            if amazon_line_ship_rec:
                amazon_line_ship_rec.write(order_line_vals)
            else:
                order_line_obj.create(order_line_vals)

        """Gift Wrapper Line"""
        gift_wrapper_charge = float(line_data.get('gift_wrapper_charge', 0.0))
        gift_wrapper_tax = float(line_data.get('gift_wrapper_tax', 0.0))
        gift_wrapper_tax = self.calculate_tax_amount(gift_wrapper_charge, gift_wrapper_tax, 0.0)
        gift_wrapper_charge = self.get_item_price(gift_wrapper_charge, gift_wrapper_tax)

        if gift_wrapper_charge:
            gift_wrapper_product = False
            gift_wrapper_description = ''
            amazon_line_gift_wrap_rec = order_line_obj.search(
                [('amazon_order_item_id', '=', amazon_line_rec.amazon_order_item_id + '_gift_wrap'),
                 ('order_id', '=', amazon_order.id)])

            """Changed condition by Dhruvi gift_wrapper_product according to seller wise"""
            if instance.seller_id.gift_wrapper_product_id:
                gift_wrapper_product = instance.seller_id.gift_wrapper_product_id
            else:
                gift_wrapper_description = "Gift Wrapping"

            tax_id = False
            qty_price_dict.update(
                {'order_qty': 1, 'amount_per_unit': gift_wrapper_charge, 'amazon_order_qty': 1,
                 'amazon_order_item_id': amazon_line_rec.amazon_order_item_id + '_gift_wrap'})
            order_line_vals = self.create_sale_order_line_vals(qty_price_dict, tax_id, False,
                                                               gift_wrapper_product and gift_wrapper_product.id or False,
                                                               amazon_order, instance, (
                                                                       gift_wrapper_description and gift_wrapper_description) or (
                                                                       gift_wrapper_product and gift_wrapper_product.name))
            order_line_vals.update({
                'line_tax_amount': gift_wrapper_tax
            })
            amazon_line_rec and amazon_line_rec.write(
                {'amz_gift_wrapper_charge': gift_wrapper_charge,
                 'amz_gift_wrapper_tax': gift_wrapper_tax})
            if amazon_line_gift_wrap_rec:
                amazon_line_gift_wrap_rec.write(order_line_vals)
            else:
                order_line_obj.create(order_line_vals)

        """Promotion Discount"""
        promotion_discount = float(line_data.get('promotion_discount', 0.0))
        if promotion_discount:
            promotion_discount_product = False
            promotion_discount_description = ''
            amazon_line_promo_dis_rec = order_line_obj.search([('amazon_order_item_id', '=',
                                                                amazon_line_rec.amazon_order_item_id + '_promo_discount'),
                                                               ('order_id', '=', amazon_order.id)])

            """Changed condition by Dhruvi promotion_discount_product according to seller wise."""
            if instance.seller_id.gift_wrapper_product_id:
                promotion_discount_product = instance.seller_id.promotion_discount_product_id
            else:
                promotion_discount_description = "Promotion Discount"

            qty_price_dict.update(
                {'order_qty': 1, 'amount_per_unit': promotion_discount, 'amazon_order_qty': 1,
                 'amazon_order_item_id': amazon_line_rec.amazon_order_item_id + '_promo_discount'})
            order_line_vals = self.create_sale_order_line_vals(qty_price_dict, False, False,
                                                               promotion_discount_product and promotion_discount_product.id or False,
                                                               amazon_order, instance, (
                                                                       promotion_discount_description and promotion_discount_description) or (
                                                                       promotion_discount_product and promotion_discount_product.name))
            amazon_line_rec and amazon_line_rec.write(
                {'amz_promotion_discount': promotion_discount})
            if amazon_line_promo_dis_rec:
                amazon_line_promo_dis_rec.write(order_line_vals)
            else:
                order_line_obj.create(order_line_vals)
        return True

    @api.multi
    def create_sale_order_line_vals(self, qty_price_dict, tax_id, amazon_product=False,
                                    odoo_product_id=False, amazon_order=False, instance=False,
                                    title=False):

        sale_order_line = self.env['sale.order.line']
        order_qty = qty_price_dict.get('order_qty')
        product_name = (title and title) or (amazon_product and amazon_product.name)

        if not isinstance(product_name, str):
            product_name = product_name.decode('utf-8')

        odoo_product = odoo_product_id and self.env['product.product'].browse(
            odoo_product_id) or False

        vals = ({
            'order_id': amazon_order.id or False,
            'product_id': amazon_product and amazon_product.product_id.id or odoo_product_id or False,
            'company_id': amazon_order.company_id.id or False,
            'description': product_name,
            'order_qty': order_qty,
            'price_unit': qty_price_dict.get('amount_per_unit'),
            'discount': 0.0,
            'product_uom': amazon_product and amazon_product.product_tmpl_id.uom_id or odoo_product and odoo_product.product_tmpl_id.uom_id
        })
        order_vals = sale_order_line.create_sale_order_line_ept(vals)

        order_vals.update({
            'amazon_order_qty': qty_price_dict.get('amazon_order_qty', 0.0),
            'amazon_order_item_id': qty_price_dict.get('amazon_order_item_id', False),
            'amazon_product_id': amazon_product and amazon_product.id or False
        })
        if amazon_product and amazon_product.product_asin:
            order_vals.update({'producturl': "%s%s" % (
                instance.producturl_prefix or '', amazon_product.product_asin)})

        return order_vals

    @api.multi
    def search_or_create_or_update_product(self, row, instance):
        amazon_product_obj = self.env['amazon.product.ept']
        seller_sku = row.get('sku', False)

        """Search Product Which we will deliver to the customer"""
        amazon_product = amazon_product_obj.search_amazon_product(instance.id, seller_sku, 'AFN')

        # amazon_product = amazon_product_obj.search(domain)
        if not amazon_product:
            odoo_product = amazon_product_obj.search_product(seller_sku)
            product_vals = self.create_fba_product_vals(row, instance, odoo_product)
            amazon_product = amazon_product_obj.create(product_vals)

        return amazon_product and amazon_product[0]

    @api.multi
    def create_fba_product_vals(self, row, instance, odoo_product):
        sku = row.get('sku', False) or (odoo_product and odoo_product.default_code) or False
        vals = {
            'instance_id': instance.id,
            'seller_sku': sku,
            'type': odoo_product and odoo_product.type or 'product',
            'product_id': odoo_product and odoo_product.id or False,
            'purchase_ok': True,
            'sale_ok': True,
            'exported_to_amazon': True,
            'fulfillment_by': 'AFN',
        }
        if not odoo_product:
            vals.update({'name': row.get('name', ''), 'default_code': sku})
        return vals

    @api.multi
    def prepare_extra_order_vals(self,instance, row):
        return {}
