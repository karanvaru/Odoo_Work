from datetime import datetime, timedelta
import time
import base64
from io import StringIO
import csv
from dateutil import parser
import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


_logger = logging.getLogger(__name__)

class sale_order_return_report(models.Model):
    _name = "sale.order.return.report"
    _inherits = {"report.request.history": 'report_history_id'}
    _inherit = ['mail.thread']
    _description = "Return Report"
    _order = 'id desc'

    @api.multi
    def get_total_returns(self):
        for record in self:
            record.return_count = len(record.picking_ids.ids)

    @api.one
    def get_log_count(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('sale.order.return.report')
        records = amazon_transaction_log_obj.search(
            [('model_id', '=', model_id), ('res_id', '=', self.id)])
        self.log_count = len(records.ids)

    @api.multi
    def list_of_logs(self):
        amazon_transaction_log_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_log_obj.get_model_id('sale.order.return.report')
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

    name = fields.Char(size=256, string='Name')
    report_history_id = fields.Many2one('report.request.history', string='Report', required=True,
                                        ondelete="cascade", index=True, auto_join=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    auto_generated = fields.Boolean('Auto Genrated Record ?', default=False)
    picking_ids = fields.One2many('stock.picking', 'return_report_id', string="Return Pickings")
    return_count = fields.Integer(compute="get_total_returns", string="Returns")
    log_count = fields.Integer(compute="get_log_count", string="Log Count")

    @api.multi
    def list_of_return_orders(self):
        action = {
            'domain': "[('id', 'in', " + str(self.picking_ids.ids) + " )]",
            'name': 'Amazon FBA returns',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.model
    def default_get(self, fields):
        res = super(sale_order_return_report, self).default_get(fields)
        if not fields:
            return res
        res.update({'report_type': '_GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA_',
                    })
        return res

    @api.model
    def create(self, vals):
        try:
            sequence = self.env.ref('amazon_ept.seq_import_customer_return_report_job')
            if sequence:
                report_name = sequence.next_by_id()
            else:
                report_name = '/'
        except:
            report_name = '/'
        vals.update({'name': report_name})
        return super(sale_order_return_report, self).create(vals)

    @api.onchange('seller_id')
    def on_change_seller_id(self):
        value = {}
        if self.seller_id:
            value.update({'start_date': self.seller_id.return_report_last_sync_on,
                          'end_date': datetime.now()})
        return {'value': value}

#     @api.multi
#     def request_report(self):
#         self.ensure_one()
#         self.env['report.request.history'].request_report(self.report_history_id, self.seller_id,
#                                                           self.report_type, self.start_date,
#                                                           self.end_date)
#         return True

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
        kwargs = {'merchant_id':seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token':seller.auth_token and str(seller.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'get_report_request_list',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':seller.country_id.amazon_marketplace_code or
                                seller.country_id.code,
                  'proxies':proxy_data,
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
    def auto_import_return_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            if not seller:
                return True
            if seller.return_report_last_sync_on:
                start_date = seller.return_report_last_sync_on
            else:
                today = datetime.now()
                earlier = today - timedelta(days=30)
                start_date = earlier.strftime("%Y-%m-%d %H:%M:%S")
            date_end = datetime.now()
            date_end = date_end.strftime("%Y-%m-%d %H:%M:%S")

            return_report = self.create(
                {'report_type': '_GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA_',
                 'seller_id': seller_id,
                 'start_date': start_date,
                 'end_date': date_end,
                 'state': 'draft',
                 'requested_date': datetime.now(),
                 'auto_generated': True,
                 })
            return_report.request_report()
            seller.write({'return_report_last_sync_on': date_end})
        return True

    @api.model
    def auto_process_return_order_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            return_reports = self.search([('seller_id', '=', seller.id),
                                          ('state', 'in', ['_SUBMITTED_', '_IN_PROGRESS_']),
                                          ('auto_generated', '=', True)
                                          ])
            for report in return_reports:
                report.get_report_request_list()
            return_reports = self.search([('seller_id', '=', seller.id),
                                          ('state', '=', '_DONE_'),
                                          ('auto_generated', '=', True),
                                          ('report_id', '!=', False)
                                          ])
            for report in return_reports:
                report.with_context(is_auto_process=True).get_report()
                report.process_return_report_file()
                self._cr.commit()
        return True

    @api.multi
    def get_report(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False        
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
        
        kwargs = {'merchant_id':seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token':seller.auth_token and str(seller.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'get_report',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':seller.country_id.amazon_marketplace_code or
                                seller.country_id.code,
                  'proxies':proxy_data,
                  'report_id': self.report_id,
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Customer Return Process',
                    'application': 'other',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)  
                
                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'sale.order.return.report'),
                    'log_type': 'error',
                    'skip_record': True,
                    'message': response.get('reason'),
                    'job_id': job.id
                }
                amazon_transaction_obj.create(log_line_vals)    
            else:
                raise Warning(response.get('reason'))
        else:
            data = response.get('result')
            
        if data:
            data = data.encode()
            result = base64.b64encode(data)
            file_name = "Return_report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'

            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'datas': result,
                'datas_fname': file_name,
                'res_model': 'mail.compose.message',
                'type': 'binary'
            })
            self.message_post(body=_("<b>Return Report Downloaded</b>"),
                              attachment_ids=attachment.ids)
            self.write({'attachment_id': attachment.id})
        else:
            raise Warning('There is no Data in the report %s' % (self.name))
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
    def get_log_vals(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        log_line_vals = {
            'res_id': self.id or 0,
            'log_type': 'not_found',
            'user_id': self.env.uid,
            'skip_record': True,
            'model_id': amazon_transaction_obj.get_model_id('sale.order.return.report'),
        }
        return log_line_vals

    @api.model
    def get_warehouse(self, fulfillment_center_id, seller, amazon_order):
        fulfillment_center = self.env['amazon.fulfillment.center'].search(
            [('center_code', '=', fulfillment_center_id), ('seller_id', '=', seller.id)], limit=1)
        warehouse = fulfillment_center and fulfillment_center.warehouse_id or \
                    amazon_order.amz_instance_id and amazon_order.amz_instance_id.fba_warehouse_id \
                    or amazon_order.amz_instance_id.warehouse_id or False
        return warehouse

    @api.multi
    def get_set_product(self, move, product, flag=False):
        try:
            bom_obj = self.env['mrp.bom']
            bom_point = bom_obj.sudo()._bom_find(product=product)
            if flag:
                return bom_point
            from_uom = move.product_uom
            to_uom = bom_point.product_uom_id
            factor = from_uom._compute_quantity(move.sale_line_id.product_qty,
                                                to_uom) / bom_point.product_qty
            bom, lines = bom_point.explode(move.sale_line_id.product_id, factor,
                                           picking_type=bom_point.picking_type_id)
            return lines
        except:
            return {}

    @api.multi
    def process_kit_type_product(self, move_lines, product, amazon_order, job, returned_qty,
                                 warehouse, return_date, sku, disposition, reason,
                                 return_picking_dict, status, fulfillment_center_id,
                                 remaning_move_qty):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        skip_moves = []
        for move in move_lines:
            if move.product_id.id in skip_moves:
                continue
            if remaning_move_qty.get(move.id) == 0.0:
                continue
            picking = move.picking_id
            if picking.state != 'done':
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order.amazon_reference,
                    'message': 'Order %s Is Skipped due to delivery picking  found in %s state ' % (
                    picking.state),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue

            one_set_product_dict = self.get_set_product(move, product)
            if not one_set_product_dict:
                continue
            if returned_qty <= 0:
                continue
            bom_qty = 0.0
            for bom_line, line in one_set_product_dict:
                if bom_line.product_id.id == move.product_id.id:
                    bom_qty = line['qty']
                    bom_qty = bom_qty / move.sale_line_id.product_qty
                    break
            if bom_qty == 0.0:
                continue
            key = (
            move, warehouse, return_date, sku, disposition, reason, status, fulfillment_center_id)

            final_return_qty = returned_qty * bom_qty

            if move.id in remaning_move_qty:
                get_remain_qty = remaning_move_qty.get(move.id)
                if get_remain_qty < final_return_qty:
                    final_return_qty = get_remain_qty
            else:
                get_remain_qty = move.product_uom_qty
            remaning_move_qty.update({move.id: get_remain_qty - final_return_qty})

            if get_remain_qty - final_return_qty == 0.0 or final_return_qty == returned_qty * bom_qty:
                skip_moves.append(move.product_id.id)

            if picking not in return_picking_dict:
                return_picking_dict.update({picking: {key: final_return_qty}})
            else:
                qty = return_picking_dict.get(picking, {}).get(key, 0.0)
                return_picking_dict[picking][key] = qty + final_return_qty

        return return_picking_dict, remaning_move_qty

    @api.multi
    def re_process_return_report_file(self):
        amazon_transaction_obj = self.env['amazon.transaction.log']
        model_id = amazon_transaction_obj.get_model_id('sale.order.return.report')
        records = amazon_transaction_obj.search(
            [('model_id', '=', model_id), ('action_type', '!=', 'create'),
             ('res_id', '=', self.id)])
        records.unlink()
        self.process_return_report_file()
        return True

    @api.multi
    def process_return_report_file(self):
        self.ensure_one()
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")
        sale_order_line_obj = self.env['sale.order.line']
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        sale_order_obj = self.env['sale.order']
        amazon_product_obj = self.env['amazon.product.ept']
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        reader = csv.DictReader(imp_file, delimiter='\t')
        move_obj = self.env['stock.move']
        seller = self.seller_id
        return_picking_dict = {}
        remaning_move_qty = {}
        fulfillment_warehouse = {}
        job_log_vals = {
            'skip_process': True,
            'application': 'sales_return',
            'operation_type': 'import',
            'message': 'Sales Return report Processed %s' % (self.name)
        }
        job = amazon_log_book_obj.create(job_log_vals)

        for line in reader:
            status = line.get('status')
            if not self.seller_id.reimbursed_warehouse_id:
                if status != 'Unit returned to inventory':
                    continue
            return_date = line.get('return-date', time.strftime('%Y-%m-%d %H:%M:%S'))
            amazon_order_id = line.get('order-id', '')
            sku = line.get('sku')
            returned_qty = float(line.get('quantity', 0.0))
            disposition = line.get('detailed-disposition')
            reason = line.get('reason')
            fulfillment_center_id = line.get('fulfillment-center-id', '')
            amazon_orders = sale_order_obj.search([('amazon_reference', '=', amazon_order_id)])
            if not amazon_orders or not amazon_order_id:
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order_id,
                    'message': 'Order %s Is Skipped due to not found in ERP' % (amazon_order_id),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue
            instance_ids = [amazon_order.amz_instance_id.id for amazon_order in amazon_orders]
            amazon_products = amazon_product_obj.search(
                [('seller_sku', '=', sku), ('instance_id', 'in', instance_ids)])
            if not amazon_products:
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order_id,
                    'message': 'Order %s Is Skipped due to Product %s not found in ERP' % (
                    amazon_order_id, sku),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue
            domain = [('order_id', 'in', amazon_orders.ids),
                      ('amazon_product_id', 'in', amazon_products.ids)]
            amazon_order_lines = sale_order_line_obj.search(domain, order="id")
            if not amazon_order_lines:
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order_id,
                    'message': 'Order line %s Is Skipped due to not found in ERP' % (sku),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue
            if fulfillment_center_id not in fulfillment_warehouse:
                warehouse = self.get_warehouse(fulfillment_center_id, seller, amazon_orders[0])
                fulfillment_warehouse.update({fulfillment_center_id: warehouse})
            warehouse = fulfillment_warehouse.get(fulfillment_center_id)
            if not warehouse:
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order_id,
                    'message': 'Order %s Is Skipped due warehouse not found in ERP || Fulfillment center %s ' % (
                    amazon_order_id, fulfillment_center_id),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue
            date_done = datetime.strftime(parser.parse(return_date), '%Y-%m-%d')
            product = amazon_order_lines[0].product_id
            incoming_picking_ids = []
            outgoing_picking_ids = []
            for amazon_order in amazon_orders:
                for picking in amazon_order.picking_ids:
                    if picking.picking_type_id.code == 'incoming':
                        incoming_picking_ids.append(picking.id)
                    if picking.picking_type_id.code == 'outgoing':
                        outgoing_picking_ids.append(picking.id)

            domain = [('picking_id', 'in', incoming_picking_ids),
                      ('product_id', '=', product.id),
                      ('state', '=', 'done')]
            move_lines = move_obj.search(domain)
            if not move_lines:
                domain = [('picking_id', 'in', incoming_picking_ids),
                          ('sale_line_id.product_id', '=', product.id),
                          ('state', '=', 'done')]
                move_lines = move_obj.search(domain)
            already_processed = False
            for move_line in move_lines:
                fba_returned_date = move_line.fba_returned_date
                if fba_returned_date:
                    fba_returned_date = datetime.strftime(parser.parse(str(fba_returned_date)),
                                                          '%Y-%m-%d')
                    if date_done == fba_returned_date:
                        already_processed = True
                        break
            if already_processed:
                continue
            exclude_move_ids = []
            for move_id, qty in remaning_move_qty.items():
                if qty <= 0.0:
                    exclude_move_ids.append(move_id)
            domain = [('picking_id', 'in', outgoing_picking_ids),
                      ('product_id', '=', product.id),
                      ('state', '=', 'done'), ('id', 'not in', exclude_move_ids)]
            move_lines = move_obj.search(domain, order='product_qty desc')
            if not move_lines:
                domain = [('picking_id', 'in', outgoing_picking_ids),
                          ('sale_line_id.product_id', '=', product.id), ('state', '=', 'done'),
                          ('id', 'not in', exclude_move_ids)]
                move_lines = move_obj.search(domain, order='product_qty desc')
                if move_lines:
                    return_picking_dict, remaning_move_qty = self.process_kit_type_product(
                        move_lines, product, amazon_orders[0], job, returned_qty, warehouse,
                        return_date, sku, disposition, reason, return_picking_dict, status,
                        fulfillment_center_id, remaning_move_qty)
                    continue
            if not move_lines:
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order_id,
                    'message': 'Order %s Is Skipped due to delivery move not found either move '
                               'have already returned or move missing in the ERP ' % (
                    amazon_order_id),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue
            move = move_lines[0]
            picking = move.picking_id
            if picking.state != 'done':
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order_id,
                    'message': 'Order %s Is Skipped due to delivery picking  found in %s state ' % (
                    picking.state),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue
            qty = move.product_qty - sum(move.move_dest_ids.filtered(
                lambda m: m.state in ['partially_available', 'assigned', 'done']). \
                                         mapped('move_line_ids').mapped('product_qty'))
            if round(qty, 2) <= 0:
                log_line_vals = self.get_log_vals()
                log_line_vals.update({
                    'amazon_order_reference': amazon_order_id,
                    'message': 'Order %s Is Skipped due to not found quant qty from quant history ' % (
                    amazon_order_id),
                    'job_id': job.id
                })
                amazon_transaction_obj.create(log_line_vals)
                continue
            if move.id in remaning_move_qty:
                get_remain_qty = remaning_move_qty.get(move.id)
            else:
                get_remain_qty = move.product_qty
            remaning_move_qty.update({move.id: get_remain_qty - returned_qty})
            key = (
            move, warehouse, return_date, sku, disposition, reason, status, fulfillment_center_id)
            if picking not in return_picking_dict:
                return_picking_dict.update({picking: {key: returned_qty}})
            else:
                qty = return_picking_dict.get(picking, {}).get(key, 0.0)
                return_picking_dict[picking][key] = qty + returned_qty

        self._create_fba_returns(return_picking_dict)
        self.write({'state': 'processed'})
        return True

    @api.model
    def _create_fba_returns(self, return_picking_dict):
        move_obj = self.env['stock.move']
        return_reason_obj = self.env['amazon.return.reason.ept']
        return_config_obj = self.env['order.return.config']
        stock_immediate_transfer_obj = self.env['stock.immediate.transfer']
        for picking, key_qty in return_picking_dict.items():
            for return_move in picking.move_lines:
                return_move.move_dest_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

            default_pick_type_id = picking.picking_type_id.return_picking_type_id and \
                                   picking.picking_type_id.return_picking_type_id.id or \
                                   picking.picking_type_id.id
            location_wise_moves = {}
            for key, qty in key_qty.items():
                move, warehouse, return_date, sku, disposition, reason, status, fulfillment_center_id = key
                move_dest_ids = [move_dest_id for move_dest_id in
                                 move.origin_returned_move_id.move_dest_ids if
                                 move_dest_id.state != 'cancel']
                location_dest_id = False
                if self.seller_id.reimbursed_warehouse_id:
                    location_dest_id = self.seller_id.reimbursed_warehouse_id.lot_stock_id

                if not location_dest_id and disposition == 'SELLABLE':
                    pick_type = warehouse.in_type_id.id
                    location_dest_id = warehouse.lot_stock_id
                else:
                    pick_type = default_pick_type_id
                    location_dest_id = warehouse.unsellable_location_id
                    # instance=picking.amazon_instance_id
                    # return_config_record = return_config_obj.search([('instance_id','=',instance.id),('condition','=',disposition)])
                    # location_dest_id = return_config_record.location_id or warehouse.lot_stock_id
                reason_record = return_reason_obj.search([('name', '=', reason)], limit=1)
                if not reason_record:
                    reason_record = return_reason_obj.create({'name': reason})
                fulfillment_center = self.env['amazon.fulfillment.center'].search(
                    [('center_code', '=', fulfillment_center_id),
                     ('seller_id', '=', self.seller_id.id)])
                new_move = move.copy(default={
                    'product_id': move.product_id.id,
                    'product_uom_qty': qty,
                    'state': 'draft',
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': location_dest_id.id,
                    'picking_type_id': pick_type,
                    'warehouse_id': warehouse and warehouse.id or
                                    picking.picking_type_id.warehouse_id.id,
                    'origin_returned_move_id': move.id,
                    'procure_method': 'make_to_stock',
                    'move_dest_ids': move_dest_ids or False,
                    'date': return_date,
                    'return_reason_id': reason_record.id,
                    'fba_returned_date': return_date,
                    'detailed_disposition': disposition,
                    'status': status,
                    'fulfillment_center_id': fulfillment_center.id or False
                })
                if location_dest_id in location_wise_moves:
                    location_wise_moves[location_dest_id].append(new_move.id)
                else:
                    location_wise_moves.update({location_dest_id: [new_move.id]})

            for location_dest_id, move_ids in location_wise_moves.items():
                moves = move_obj.browse(move_ids)
                new_picking = picking.copy(default={
                    'move_lines': [],
                    'picking_type_id': moves[0].picking_type_id.id,
                    'state': 'draft',
                    'origin': picking.name,
                    'is_amazon_fba_return_delivery_order': True,
                    'return_report_id': self.id,
                    'location_id': moves[0].location_id.id,
                    'location_dest_id': moves[0].location_dest_id.id,
                    'date': moves[0].date,
                    'seller_id': self.seller_id and self.seller_id.id or False,
                    'global_channel_id': self.seller_id.global_channel_id and
                                         self.seller_id.global_channel_id.id or False
                })
                moves.write({'picking_id': new_picking.id})
                stock_immediate_transfer_obj.create({'pick_ids': [(4, new_picking.id)]}).process()
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
        
        kwargs = {'merchant_id':seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token':seller.auth_token and str(seller.auth_token) or False,
                  'app_name':'amazon_ept',
                  'account_token':account.account_token,
                  'emipro_api':'shipping_request_report',
                  'dbuuid':dbuuid,
                  'amazon_marketplace_code':seller.country_id.amazon_marketplace_code or
                                seller.country_id.code,
                  'proxies':proxy_data,
                  'marketplaceids': marketplaceids,
                  'report_type': report_type,
                  'start_date': start_date,
                  'end_date': end_date,}

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
