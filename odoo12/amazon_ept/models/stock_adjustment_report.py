from odoo import models, fields, api, _
from datetime import datetime, timedelta
import time
import base64
import csv
from io import StringIO
import copy
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class UnicodeDictWriter(csv.DictWriter):
    def __init__(self, csvfile, fieldnames, *args, **kwargs):
        """Allows to specify an additional keyword argument encoding which
        defaults to "utf-8"
        """
        self.encoding = kwargs.pop('encoding', 'utf-8')
        csv.DictWriter.__init__(self, csvfile, fieldnames, *args, **kwargs)

    def _dict_to_list(self, rowdict):
        rv = csv.DictWriter._dict_to_list(self, rowdict)
        return [(f.encode(self.encoding, 'ignore') if isinstance(f, str) else f) \
                for f in rv]


class stock_adjustment_report_history(models.Model):
    _name = "amazon.stock.adjustment.report.history"
    _inherits = {"report.request.history": 'report_history_id'}
    _description = "Stock Adjustment Report"
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.model
    def auto_import_stock_adjustment_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            start_date = datetime.now() + timedelta(days=seller.inv_adjustment_report_days * -1 or -3)
            date_end = datetime.now()

            inv_report = self.create({'report_type': '_GET_FBA_FULFILLMENT_INVENTORY_ADJUSTMENTS_DATA_',
                                      'seller_id': seller_id,
                                      'start_date': start_date,
                                      'end_date': date_end,
                                      'state': 'draft',
                                      'requested_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                      'auto_generated': True,
                                      })
            inv_report.with_context(is_auto_process=True).request_report()
            seller.write({'stock_adjustment_report_last_sync_on': date_end})
        return True

    @api.model
    def auto_process_stock_adjustment_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            inv_reports = self.search([('seller_id', '=', seller.id),
                                       ('state', 'in', ['_SUBMITTED_', '_IN_PROGRESS_']),
                                       ('auto_generated', '=', True)
                                       ])
            for report in inv_reports:
                report.with_context(is_auto_process=True).get_report_request_list()
            inv_reports = self.search([('seller_id', '=', seller.id),
                                       ('state', '=', '_DONE_'),
                                       ('auto_generated', '=', True),
                                       ('report_id', '!=', False)
                                       ])
            for report in inv_reports:
                report.with_context(is_auto_process=True).get_report()
                report.process_stock_adjustment_report()
                self._cr.commit()
        return True

    @api.one
    def get_log_count(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('amazon.stock.adjustment.report.history')
        records = amazon_transaction_log_obj.search([('model_id', '=', model_id), ('res_id', '=', self.id)])
        self.log_count = len(records.ids)

    @api.multi
    def get_pickings(self):
        self.transfer_count = len(self.transfer_picking_ids.ids)

    name = fields.Char(size=256, string='Name')
    report_history_id = fields.Many2one('report.request.history', string='Report', required=True, ondelete="cascade",
                                        index=True, auto_join=True)
    state = fields.Selection([('draft', 'Draft'), ('_SUBMITTED_', 'SUBMITTED'), ('_IN_PROGRESS_', 'IN_PROGRESS'),
                              ('_CANCELLED_', 'CANCELLED'), ('_DONE_', 'Report Received'),
                              ('_DONE_NO_DATA_', 'DONE_NO_DATA'), ('processed', 'PROCESSED'),
                              ('partially_processed', 'Partially Processed')
                              ],
                             string='Report Status', default='draft')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    auto_generated = fields.Boolean('Auto Generated Record ?', default=False)
    instance_id = fields.Many2one("amazon.instance.ept", string="Instnace")
    transfer_picking_ids = fields.One2many("stock.picking", 'stock_adjustment_report_id', string="Pickings")
    transfer_count = fields.Integer("Transfer Count", compute="get_pickings")
    log_count = fields.Integer(compute="get_log_count", string="Log Count")

    @api.multi
    def list_of_transfer_pickings(self):
        action = {
            'domain': "[('id', 'in', " + str(self.transfer_picking_ids.ids) + " )]",
            'name': 'Stock Adjustment Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.multi
    def on_change_seller_id(self, seller_id, start_date, end_date):
        value = {}
        if seller_id:
            seller = self.env['amazon.seller.ept'].browse(seller_id)
            start_date = datetime.now() + timedelta(days=seller.inv_adjustment_report_days * -1 or -3)
            value.update({'start_date': start_date, 'end_date': datetime.now()})
        return {'value': value}

    @api.multi
    def unlink(self):
        for report in self:
            if report.state == 'processed':
                raise Warning(_('You cannot delete processed report.'))
        return super(stock_adjustment_report_history, self).unlink()

    @api.model
    def default_get(self, fields):
        res = super(stock_adjustment_report_history, self).default_get(fields)
        if not fields:
            return res
        res.update({'report_type': '_GET_FBA_FULFILLMENT_INVENTORY_ADJUSTMENTS_DATA_',
                    })
        return res

    @api.model
    def create(self, vals):
        try:
            sequence_id = self.env.ref('amazon_ept.seq_inv_adjustment_report_job').ids
            if sequence_id:
                report_name = self.env['ir.sequence'].get_id(sequence_id[0])
            else:
                report_name = '/'
        except:
            report_name = '/'
        vals.update({'name': report_name})
        return super(stock_adjustment_report_history, self).create(vals)

    @api.multi
    def request_report(self):
        seller, report_type, start_date, end_date = self.seller_id, self.report_type, self.start_date, self.end_date
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False

        if not seller:
            raise Warning('Please select instance')

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

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
                  'start_date': start_date,
                  'end_date': end_date,
                  'report_type': report_type,
                  'marketplace_ids': marketplaceids,
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'skip_process': True,
                    'message': 'Inventory Adjustment Report Process',
                    'application': 'stock_adjust',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)
                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'amazon.stock.adjustment.report.history'),
                    'res_id': self.id or 0,
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
        seller = self.seller_id
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        if not seller:
            raise Warning('Please select Seller')

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
                  'request_ids': (self.report_request_id,),
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Inventory Adjustment Report Process',
                    'application': 'stock_adjust',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'amazon.stock.adjustment.report.history'),
                    'res_id': self.id or 0,
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

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        if not self.request_id:
            return True

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'get_report_request_list',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'request_ids': (self.report_request_id,),
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
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
                  'report_id': self.report_id,
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Inventory Adjustment Report Process',
                    'application': 'stock_adjust',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'amazon.stock.adjustment.report.history'),
                    'log_type': 'error',
                    'action_type': 'terminate_process_with_log',
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
        file_name = "Inv_Adjustment_report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': result,
            'datas_fname': file_name,
            'res_model': 'mail.compose.message',
            #                                            'type': 'binary'
        })
        self.message_post(body=_("<b>Inventory Adjustment Report Downloaded</b>"), attachment_ids=attachment.ids)
        self.write({'attachment_id': attachment.id})
        seller.write({'stock_adjustment_report_last_sync_on': datetime.now()})

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
    def find_amazon_product_for_process_adjustment_line(self, line, job, model_id):
        amazon_product_obj = self.env['amazon.product.ept']
        sku = line.get('sku')
        asin = line.get('fnsku')
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        amazon_product = amazon_product_obj.search([('seller_sku', '=', sku), ('fulfillment_by', '=', 'AFN')], limit=1)
        if not amazon_product:
            amazon_product = amazon_product_obj.search([('product_asin', '=', asin), ('fulfillment_by', '=', 'AFN')],
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
    def process_non_counter_part_lines(self, config, lines, job, model_id, partially_processed, create_log):
        amazon_adjustment_reason_code_obj = self.env['amazon.adjustment.reason.code']
        fulfillment_center_obj = self.env['amazon.fulfillment.center']
        picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        group_id = config.group_id.id
        picking_ids = []
        stock_immediate_transfer_obj = self.env['stock.immediate.transfer']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        for line in lines:
            reason = line.get('reason')
            fulfillment_center_id = line.get('fulfillment-center-id')
            qty = float(line.get('quantity', 0.0))
            disposition = line.get('disposition')
            adjustment_date = line.get('adjusted-date', False)
            transaction_item_id = line.get('transaction-item-id')
            product = self.find_amazon_product_for_process_adjustment_line(line, job, model_id)
            if not product:
                continue
            fulfillment_center = fulfillment_center_obj.search(
                [('center_code', '=', fulfillment_center_id), ('seller_id', '=', self.seller_id.id)], limit=1)
            warehouse = fulfillment_center and fulfillment_center.warehouse_id or False
            if not warehouse or (disposition == 'UNSELLABLE' and not warehouse.unsellable_location_id):
                partially_processed = True
                if not warehouse:
                    message = 'Warehouse not found for fulfillment center %s' % (fulfillment_center_id)
                else:
                    message = 'Unsellable location not found for Warehouse %s' % (warehouse.name)
                amazon_transaction_log_obj.create({'message': message,
                                                   'model_id': model_id,
                                                   'job_id': job.id,
                                                   'operation_type': 'import',
                                                   'log_type': 'not_found',
                                                   'action_type': 'skip_line',
                                                   'res_id': self.id
                                                   })
                continue
            code = amazon_adjustment_reason_code_obj.search([('name', '=', reason), ('group_id', '=', group_id)])
            exist_move_domain = [('product_uom_qty', '=', abs(qty)), ('product_id', '=', product.id),
                                 ('adjusted_date', '=', adjustment_date),
                                 ('transaction_item_id', '=', transaction_item_id),
                                 ('fulfillment_center_id', '=', fulfillment_center.id), ('code_id', '=', code.id)
                                 ]
            source_location_id = False
            destination_location_id = False
            if qty < 0.0:
                if disposition == 'SELLABLE':
                    destination_location_id = config.location_id.id
                    source_location_id = warehouse.lot_stock_id.id
                else:
                    destination_location_id = config.location_id.id
                    source_location_id = warehouse.unsellable_location_id.id
            else:
                if disposition == 'SELLABLE':
                    source_location_id = config.location_id.id
                    destination_location_id = warehouse.lot_stock_id.id
                else:
                    source_location_id = config.location_id.id
                    destination_location_id = warehouse.unsellable_location_id.id

            exist_move_domain += [('location_id', '=', source_location_id),
                                  ('location_dest_id', '=', destination_location_id)]

            exist_move = stock_move_obj.search(exist_move_domain)
            if exist_move:
                if create_log:
                    amazon_transaction_log_obj.create(
                        {'message': 'Line already processed for Product %s || Code %s' % (product.name, reason),
                         'model_id': model_id,
                         'job_id': job.id,
                         'log_type': 'not_found',
                         'operation_type': 'import',
                         'action_type': 'skip_line',
                         'res_id': self.id
                         })
                continue

            vals = {}

            vals.update({
                'product_uom_qty': abs(qty),
                'product_uom': product.uom_id.id,
                'product_id': product.id,
                'name': product.name,
                'state': 'draft',
                'adjusted_date': adjustment_date,
                'transaction_item_id': transaction_item_id or False,
                'fulfillment_center_id': fulfillment_center.id,
                'code_id': code.id,
                'origin': self.name,
                'location_id': source_location_id,
                'location_dest_id': destination_location_id,
                'code_description': code.description,
            })
            picking = picking_obj.search(
                [('id', 'in', picking_ids), ('move_lines.location_id', '=', source_location_id),
                 ('move_lines.location_dest_id', '=', destination_location_id)], limit=1)
            if not picking:
                picking = picking_obj.create({
                    'picking_type_id': config.picking_type_id.id,
                    'stock_adjustment_report_id': self.id,
                    'origin': self.name,
                    'location_id': source_location_id,
                    'location_dest_id': destination_location_id,
                    'seller_id': self.seller_id and self.seller_id.id or False,
                    'global_channel_id': self.seller_id.global_channel_id and self.seller_id.global_channel_id.id or False
                })
                picking_ids.append(picking.id)
            vals.update({
                'picking_id': picking.id
            })
            stock_move_obj.create(vals)
        if picking_ids:
            pickings = picking_obj.browse(picking_ids)
            for picking in pickings:
                picking.action_confirm()
                picking.action_assign()

                if picking.state == 'assigned':
                    stock_immediate_transfer_obj.create({'pick_ids': [(4, picking.id)]}).process()

                if picking.state in ['confirmed', 'partially_available', 'assigned']:
                    stock_move_line_obj = self.env['stock.move.line']
                    for move in picking.move_lines:
                        if move.state in ['confirmed', 'partially_available']:
                            remaining_qty = move.product_uom_qty - move.reserved_availability
                            if remaining_qty > 0.0:
                                stock_move_line_obj.create(
                                    {
                                        'product_id': move.product_id.id,
                                        'product_uom_id': move.product_id.uom_id.id,
                                        'picking_id': picking.id,
                                        'qty_done': float(remaining_qty) or 0,
                                        'location_id': picking.location_id.id,
                                        'location_dest_id': picking.location_dest_id.id,
                                        'move_id': move.id,
                                    })

                picking.action_done()

        return partially_processed

    @api.multi
    def process_counter_part_lines(self, config, lines, job, model_id, partially_processed, create_log):
        temp_lines = copy.copy(lines)
        picking_obj = self.env['stock.picking']
        fulfillment_center_obj = self.env['amazon.fulfillment.center']
        transaction_item_ids = []
        amazon_adjustment_reason_code_obj = self.env['amazon.adjustment.reason.code']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        stock_move_obj = self.env['stock.move']
        group_id = config.group_id.id
        counter_line_list = []
        picking_ids = []
        stock_immediate_transfer_obj = self.env['stock.immediate.transfer']
        for line in lines:
            if line.get('transaction-item-id') in transaction_item_ids:
                continue
            reason = line.get('reason')
            code = amazon_adjustment_reason_code_obj.search([('name', '=', reason), ('group_id', '=', group_id)])
            counter_part_code = code.counter_part_id.name
            if not counter_part_code:
                continue
            for temp_line in temp_lines:
                if temp_line.get('reason') == counter_part_code and abs(float(temp_line.get('quantity', 0.0))) == abs(
                        float(line.get('quantity', 0.0))) \
                        and temp_line.get('transaction-item-id') not in transaction_item_ids:
                    if line.get('adjusted-date') == temp_line.get('adjusted-date') and line.get(
                            'fnsku') == temp_line.get('fnsku') \
                            and line.get('sku') == temp_line.get('sku') and line.get(
                        'fulfillment-center-id') == temp_line.get('fulfillment-center-id'):
                        transaction_item_ids.append(temp_line.get('transaction-item-id'))
                        counter_line_list.append((line, temp_line))
                        message = """ 
                                Counter Part Combination line ||                                
                                sku : %s || adjustment-date %s || fulfillment-center-id %s || quantity %s ||
                                Code %s - Disposition %s & %s - Disposition %s
                        """ % (line.get('sku'),
                               line.get('adjusted-date'),
                               line.get('fulfillment-center-id'),
                               line.get('quantity', 0.0),
                               reason, line.get('disposition'), temp_line.get('reason'),
                               temp_line.get('disposition')
                               )
                        if create_log:
                            amazon_transaction_log_obj.create({'message': message,
                                                               'model_id': model_id,
                                                               'job_id': job.id,
                                                               'action_type': 'create',
                                                               'operation_type': 'import',
                                                               'res_id': self.id
                                                               })
                        break
        for counter_line in counter_line_list:
            line = counter_line[0]
            p_line = counter_line[1]
            product = self.find_amazon_product_for_process_adjustment_line(line, job, model_id)
            p_line_qty = float(p_line.get('quantity', 0.0))
            adjustment_date = p_line.get('adjusted-date', False)
            transaction_item_id = p_line.get('transaction-item-id')
            fulfillment_center_id = p_line.get('fulfillment-center-id')
            p_line_disposition = p_line.get('disposition')
            other_line_disposition = line.get('disposition')
            fulfillment_center = fulfillment_center_obj.search(
                [('center_code', '=', fulfillment_center_id), ('seller_id', '=', self.seller_id.id)], limit=1)
            warehouse = fulfillment_center and fulfillment_center.warehouse_id or False
            if not warehouse or ((
                                         p_line_disposition == 'UNSELLABLE' or other_line_disposition == 'UNSELLABLE') and not warehouse.unsellable_location_id):
                partially_processed = True
                if not warehouse:
                    message = 'Warehouse not found for fulfillment center %s || Product %s' % (
                    fulfillment_center_id, line.get('sku'))
                else:
                    message = 'Unsellable location not found for Warehouse %s || Product %s' % (
                    warehouse.name, line.get('sku'))
                amazon_transaction_log_obj.create({'message': message,
                                                   'model_id': model_id,
                                                   'job_id': job.id,
                                                   'log_type': 'mismatch',
                                                   'operation_type': 'import',
                                                   'action_type': 'skip_line',
                                                   'res_id': self.id
                                                   })
                continue
            if not product:
                continue
            code = amazon_adjustment_reason_code_obj.search(
                [('name', '=', p_line.get('reason')), ('group_id', '=', group_id)])
            exist_move_domain = [('product_uom_qty', '=', p_line_qty), ('product_id', '=', product.id),
                                 ('adjusted_date', '=', adjustment_date),
                                 ('transaction_item_id', '=', transaction_item_id),
                                 ('fulfillment_center_id', '=', fulfillment_center.id), ('code_id', '=', code.id)
                                 ]
            source_location_id = False
            destination_location_id = False
            if p_line_disposition == 'UNSELLABLE':
                destination_location_id = warehouse.unsellable_location_id.id
            else:
                destination_location_id = warehouse.lot_stock_id.id

            if other_line_disposition == 'UNSELLABLE':
                source_location_id = warehouse.unsellable_location_id.id
            else:
                source_location_id = warehouse.lot_stock_id.id

            exist_move_domain += [('location_id', '=', source_location_id),
                                  ('location_dest_id', '=', destination_location_id)]

            exist_move = stock_move_obj.search(exist_move_domain)
            if exist_move:
                if create_log:
                    amazon_transaction_log_obj.create({
                                                          'message': 'Line already processed for Product %s || Code %s-%s' % (
                                                          product.name, p_line.get('reason'), line.get('reason')),
                                                          'model_id': model_id,
                                                          'job_id': job.id,
                                                          'log_type': 'not_found',
                                                          'operation_type': 'import',
                                                          'action_type': 'skip_line',
                                                          'res_id': self.id
                                                          })
                continue

            vals = {}
            vals.update({
                'product_uom_qty': abs(p_line_qty),
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'state': 'draft',
                'adjusted_date': adjustment_date,
                'origin': self.name,
                'name': product.name,
                'transaction_item_id': transaction_item_id or False,
                'fulfillment_center_id': fulfillment_center.id,
                'code_id': code.id,
                'location_id': source_location_id,
                'location_dest_id': destination_location_id,
                'code_description': code.description,
            })
            picking = picking_obj.search(
                [('id', 'in', picking_ids), ('move_lines.location_id', '=', source_location_id),
                 ('move_lines.location_dest_id', '=', destination_location_id)], limit=1)
            if not picking:
                picking = picking_obj.create({
                    'picking_type_id': config.picking_type_id.id,
                    'stock_adjustment_report_id': self.id,
                    'origin': self.name,
                    'location_id': source_location_id,
                    'location_dest_id': destination_location_id,
                    'seller_id': self.seller_id and self.seller_id.id or False,
                    'global_channel_id': self.seller_id.global_channel_id and self.seller_id.global_channel_id.id or False
                })
                picking_ids.append(picking.id)
            vals.update({
                'picking_id': picking.id
            })

            stock_move_obj.create(vals)
        if picking_ids:
            pickings = picking_obj.browse(picking_ids)
            for picking in pickings:
                picking.action_confirm()
                picking.action_assign()

                if picking.state == 'assigned':
                    stock_immediate_transfer_obj.create({'pick_ids': [(4, picking.id)]}).process()

                if picking.state in ['confirmed', 'partially_available', 'assigned']:
                    stock_move_line_obj = self.env['stock.move.line']
                    for move in picking.move_lines:
                        if move.state in ['confirmed', 'partially_available']:
                            remaining_qty = move.product_uom_qty - move.reserved_availability
                            if remaining_qty > 0.0:
                                stock_move_line_obj.create(
                                    {
                                        'product_id': move.product_id.id,
                                        'product_uom_id': move.product_id.uom_id.id,
                                        'picking_id': picking.id,
                                        'qty_done': float(remaining_qty) or 0,
                                        'location_id': picking.location_id.id,
                                        'location_dest_id': picking.location_dest_id.id,
                                        'move_id': move.id,
                                    })

                picking.action_done()

        return partially_processed

    @api.multi
    def create_email_of_unprocess_lines(self, config, lines, job):
        template = config.email_template_id
        if template:
            subtype = 'amazon_ept.amazon_stock_adjustment_subtype_ept'
        else:
            subtype = False
        #         kwargs = {
        #         'partner_ids' : [(6, 0, self.message_follower_ids.ids)],
        #         }
        field_names = []
        buff = StringIO()
        for line in lines:
            if not field_names:
                field_names = line.keys()
                csvwriter = UnicodeDictWriter(
                    buff, field_names, delimiter='\t'
                )
                csvwriter.writer.writerow(field_names)
            csvwriter.writerow(line)
        buff.seek(0)
        file_data = buff.read()
        instance_obj = self.env['amazon.instance.ept']
        instances = instance_obj.search([('seller_id', '=', self.seller_id.id)])
        amazon_encoding = instances and instances[0].amazon_encodings
        name = 'inv_unprocessed_lines.csv'
        vals = {
            'name': name,
            'datas': base64.encodestring(file_data.encode(amazon_encoding)),
            'datas_fname': name,
            'type': 'binary',
            'res_model': 'amazon.stock.adjustment.report.history',
        }
        attachment = self.env['ir.attachment'].create(vals)
        subject = template and template.render_template(template.subject, 'amazon.stock.adjustment.report.history',
                                                        self.ids) or ''
        body = template and template.render_template(template.body_html, 'amazon.stock.adjustment.report.history',
                                                     self.ids) or ''
        message_type = template and 'email' or 'notification'
        self.message_post(subject=subject, message_type=message_type, body=body, subtype=subtype,
                          attachment_ids=attachment.ids)  # ,**kwargs)
        return True

    @api.multi
    def process_group_wise_lines(self, group_of_data, job, model_id, partially_processed, create_log):
        for config, lines in group_of_data.items():
            lines.reverse()

            #             if config.id != 5:
            #                 continue
            if config.is_send_email:
                self.create_email_of_unprocess_lines(config, lines, job)
                continue
            if config.group_id.is_counter_part_group:
                partially_processed = self.process_counter_part_lines(config, lines, job, model_id, partially_processed,
                                                                      create_log)
            else:
                partially_processed = self.process_non_counter_part_lines(config, lines, job, model_id,
                                                                          partially_processed, create_log)
        return partially_processed

    @api.model
    def get_model_id(self, model_name):
        model = self.env['ir.model'].search([('model', '=', model_name)])
        if model:
            return model.id
        return False

    @api.multi
    def view_job(self):
        model_id = self.get_model_id('amazon.stock.adjustment.report.history')
        logs = self.env['amazon.transaction.log'].search([('model_id', '=', model_id), ('res_id', '=', self.id)])
        jobs = list(set(list(map(lambda x: x.job_id.id, logs))))
        if jobs:
            action = {
                'domain': "[('id', 'in', " + str(jobs) + " )]",
                'name': 'Job',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'amazon.process.log.book',
                'type': 'ir.actions.act_window',
            }
            return action
        else:
            return True

    @api.multi
    def process_stock_adjustment_report(self):
        self.ensure_one()
        amazon_adjustment_reason_code_obj = self.env['amazon.adjustment.reason.code']
        amazon_process_job_log_obj = self.env['amazon.process.log.book']
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        amazon_stock_adjustment_config_obj = self.env['amazon.stock.adjustment.config']
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")
        if not self.seller_id:
            raise Warning("Seller is not defind for processing report")
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        reader = csv.DictReader(imp_file, delimiter='\t')
        group_wise_lines_list = {}
        job = amazon_process_job_log_obj.create({
            'application': 'stock_adjust',
            'operation_type': 'import', })
        #             'instance_id':self.seller_id.id})
        self.attachment_id.copy(
            default={'res_model': 'amazon.process.log.book', 'res_id': job.id, 'name': self.attachment_id.name,
                     'datas_fname': self.attachment_id.name})
        partially_processed = False
        if self.state == 'partially_processed':
            create_log = False
        else:
            create_log = True
        for row in reader:
            if not row.get('reason'):
                continue
            reason = row.get('reason')
            code = amazon_adjustment_reason_code_obj.search([('name', '=', reason), ('group_id', '!=', False)])
            model_id = self.get_model_id('amazon.stock.adjustment.report.history')
            if not code:
                partially_processed = True
                amazon_transaction_log_obj.create(
                    {'message': 'Code %s configuration not found for processing' % (reason),
                     'model_id': model_id,
                     'job_id': job.id,
                     'log_type': 'not_found',
                     'action_type': 'skip_line',
                     'operation_type': 'import',
                     'res_id': self.id
                     })
                continue
            if len(code.ids) > 1:
                partially_processed = True
                amazon_transaction_log_obj.create(
                    {'message': 'Multiple Code %s configuration found for processing' % (reason),
                     'model_id': model_id,
                     'job_id': job.id,
                     'log_type': 'not_found',
                     'action_type': 'skip_line',
                     'operation_type': 'import',
                     'res_id': self.id
                     })
                continue
            group_id = code.group_id.id
            config = amazon_stock_adjustment_config_obj.search(
                [('group_id', '=', group_id), ('seller_id', '=', self.seller_id.id)])
            if not config:
                partially_processed = True
                amazon_transaction_log_obj.create(
                    {'message': 'Seller wise code %s configuration not found for processing' % (code.name),
                     'model_id': model_id,
                     'job_id': job.id,
                     'log_type': 'not_found',
                     'operation_type': 'import',
                     'action_type': 'skip_line',
                     'res_id': self.id
                     })
                continue
            if not config.is_send_email and (not config.location_id or not config.picking_type_id):
                partially_processed = True
                if not job:
                    job = amazon_process_job_log_obj.create({'application': 'stock_adjust', 'operation_type': 'import'})
                if not config.location_id and config.picking_type_id:
                    message = 'Location & Picking type not Configured for stock adjustment config ERP Id %s || group name %s' % (
                    config.id, config.group_id.name)
                elif not config.location_id:
                    message = 'Location not configured for stock adjustment config ERP Id %s || group name %s' % (
                    config.id, config.group_id.name)
                elif not config.picking_type_id:
                    message = 'Picking type is  not configured for stock adjustment config ERP Id %s || group name %s' % (
                    config.id, config.group_id.name)

                amazon_transaction_log_obj.create({'message': message,
                                                   'model_id': model_id,
                                                   'job_id': job.id,
                                                   'log_type': 'not_found',
                                                   'action_type': 'skip_line',
                                                   'operation_type': 'import',
                                                   'res_id': self.id
                                                   })
                continue

            if config in group_wise_lines_list:
                group_wise_lines_list.get(config).append(row)
            else:
                group_wise_lines_list.update({config: [row]})
        if not group_wise_lines_list:
            return True
        partially_processed = self.process_group_wise_lines(group_wise_lines_list, job, model_id, partially_processed,
                                                            create_log)
        partially_processed and self.write({'state': 'partially_processed'}) or self.write({'state': 'processed'})
        return True
