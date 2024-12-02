import base64
import time
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    amazon_instance_id = fields.Many2one("amazon.instance.ept", "Instances")

    is_amazon_delivery_order = fields.Boolean("Amazon Delivery Order", default=False, copy=False)
    updated_in_amazon = fields.Boolean("Updated In Amazon", default=False, copy=False)

    seller_id = fields.Many2one("amazon.seller.ept", "Seller")

    shipment_status_help = """ 
        InboundShipmentHeader is used with the CreateInboundShipment operation: 
            *.WORKING - The shipment was created by the seller, but has not yet shipped.
            *.SHIPPED - The shipment was picked up by the carrier. 
        
        The following is an additional ShipmentStatus value when InboundShipmentHeader is used with 
        the UpdateInboundShipment operation
            *.CANCELLED - The shipment was cancelled by the seller after the shipment was 
            sent to the Amazon fulfillment center.
    
    """

    label_preference_help = """     
        SELLER_LABEL - Seller labels the items in the inbound shipment when labels are required.
        AMAZON_LABEL_ONLY - Amazon attempts to label the items in the inbound shipment when 
                            labels are required. If Amazon determines that it does not have the 
                            information required to successfully label an item, that item is not 
                            included in the inbound shipment plan
        AMAZON_LABEL_PREFERRED - Amazon attempts to label the items in the inbound shipment when 
                                labels are required. If Amazon determines that it does not have the 
                                information required to successfully label an item, that item is 
                                included in the inbound shipment plan and the seller must label it.                    
    """

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        amazon_order = picking.sale_id
        if amazon_order.amazon_reference != 'False':
            # amazon_order = self.env['sale.order'].search([('sale_order_id','=',picking.sale_id.id),
            # ('amazon_reference','!=',False)])
            # amazon_order and vals.update({'fulfillment_by':amazon_order.amz_fulfillment_by})
            vals.update({'fulfillment_by': amazon_order.amz_fulfillment_by})
        return super(stock_picking, self)._create_invoice_from_picking(picking, vals)

    @api.multi
    def _get_total_received_qty(self):
        for picking in self:
            total_shipped_qty = 0.0
            total_received_qty = 0.0
            for move in picking.move_lines:
                if move.state == 'done':
                    total_received_qty += move.product_qty
                    total_shipped_qty += move.product_qty
                if move.state not in ['draft', 'cancel']:
                    #                     for quant in move.reserved_quant_ids:
                    #                         total_shipped_qty+=quant.qty
                    total_shipped_qty += move.reserved_availability

            picking.total_received_qty = total_received_qty
            picking.total_shipped_qty = total_shipped_qty

            # Added by twinkal to merge with FBA

    is_amazon_fba_return_delivery_order = fields.Boolean("Amazon FBA Return Delivery Order",
                                                         default=False, copy=False)
    fiscal_position = fields.Many2one('account.fiscal.position', 'Fiscal Position')
    ship_plan_id = fields.Many2one('inbound.shipment.plan.ept', readonly=True, default=False,
                                   copy=True, string="Shiment Plan")
    odoo_shipment_id = fields.Many2one('amazon.inbound.shipment.ept', string='Shipment', copy=True)
    return_report_id = fields.Many2one('sale.order.return.report', string="Return Report",
                                       copy=False)
    amazon_outbound_shipment_id = fields.Char(size=120, string='Amazon Outbound Shipment ID',
                                              readonly=True, default=False,
                                              help="Shipment ID provided by Amazon In Get "
                                                   "Fulfillment Order Reference")
    amazon_shipment_id = fields.Char(size=120, string='Amazon Shipment ID', default=False,
                                     help="Shipment Item ID provided by Amazon when we integrate "
                                          "shipment report from Amazon")
    fulfill_center = fields.Char(size=120, string='Amazon Fulfillment Center ID', readonly=True,
                                 default=False, copy=True,
                                 help="Fulfillment Center ID provided by Amazon when we send "
                                      "shipment Plan to Amazon")
    ship_label_preference = fields.Selection(
        [('NO_LABEL', 'NO_LABEL'), ('SELLER_LABEL', 'SELLER_LABEL'),
         ('AMAZON_LABEL_ONLY', 'AMAZON_LABEL_ONLY'),
         ('AMAZON_LABEL_PREFERRED', 'AMAZON_LABEL_PREFERRED'), ], default='SELLER_LABEL',
        string='LabelPrepType', help=label_preference_help)
    inbound_ship_created = fields.Boolean('Inbound Shipment Created', default=False)
    inbound_ship_updated = fields.Boolean('Inbound Shipment Updated', default=False)

    inbound_ship_data_created = fields.Boolean('Inbound Shipment Data Created', default=False)
    are_cases_required = fields.Boolean("AreCasesRequired", default=False,
                                        help="Indicates whether or not an inbound shipment contains "
                                             "case-packed boxes. A shipment must either contain all "
                                             "case-packed boxes or all individually packed boxes")
    shipment_status = fields.Selection(
        [('WORKING', 'WORKING'), ('SHIPPED', 'SHIPPED'), ('CANCELLED', 'CANCELLED')],
        string="Shipment Status", help=shipment_status_help)
    fulfillment_by = fields.Selection(
        [('MFN', 'Manufacturer Fulfillment Network'), ('AFN', 'Amazon Fulfillment Network')],
        string="Fulfillment By")
    is_fba_wh_picking = fields.Boolean("Is FBA Warehouse Picking", default=False, copy=True)

    total_received_qty = fields.Float(compute=_get_total_received_qty, string="Total Received Qty")
    total_shipped_qty = fields.Float(compute=_get_total_received_qty, string="Total Shipped Qty")
    amazon_shipment_date = fields.Datetime("Shipment Date")
    amazon_purchase_date = fields.Datetime("Purchase Date")
    estimated_arrival_date = fields.Datetime("Estimate Arrival Date")
    stock_adjustment_report_id = fields.Many2one('amazon.stock.adjustment.report.history',
                                                 string="Stock Adjustment Report")

    removal_order_report_id = fields.Many2one('amazon.removal.order.report.history', string="Report")
    removal_order_id = fields.Many2one("amazon.removal.order.ept", string="Removal Order")

    @api.model
    def check_qty_difference_and_create_return_picking(self, amazon_shipment_id, odoo_shipment_id,
                                                       instance):
        pickings = self.search([('state', '=', 'done'),
                                ('odoo_shipment_id', '=', odoo_shipment_id),
                                ('amazon_shipment_id', '=', amazon_shipment_id),
                                ('is_fba_wh_picking', '=', True)], order="id")
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        stock_move_line_obj = self.env['stock.move.line']
        amazon_product_obj = self.env['amazon.product.ept']
        location_id = pickings[0].location_id.id
        location_dest_id = pickings[0].location_dest_id.id
        move_obj = self.env['stock.move']
        return_picking = False
        attachment_ids = []
        proxy_data = instance.seller_id.get_proxy_server()

        kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token': instance.auth_token and str(instance.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'check_amazon_shipment_status',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                             instance.country_id.code,
                  'proxies': proxy_data,
                  'amazon_shipment_id': amazon_shipment_id, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            items = response.get('items')
            datas = response.get('datas')

        for data in datas:
            file_name = 'inbound_shipment_report_%s.xml' % (amazon_shipment_id)
            if data.get('next_tone'):
                file_name = 'inbound_shipment_report_%s_%s.xml' % (amazon_shipment_id, str(data.get('next_token')))

            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'datas': base64.b64encode((data.get('origin')).encode('utf-8')),
                'datas_fname': file_name,
                'res_model': 'mail.compose.message',
            })
            attachment_ids.append(attachment.id)

        for item in items:
            sku = item.get('SellerSKU', {}).get('value', '')
            asin = item.get('FulfillmentNetworkSKU', {}).get('value')
            received_qty = float(item.get('QuantityReceived', {}).get('value', 0.0))
            amazon_product = amazon_product_obj.search_amazon_product(instance.id, sku, 'AFN')
            if not amazon_product:
                amazon_product = amazon_product_obj.search(
                    [('product_asin', '=', asin), ('instance_id', '=', instance.id),
                     ('fulfillment_by', '=', 'AFN')], limit=1)
            if not amazon_product:
                continue
            done_moves = move_obj.search([('picking_id.is_fba_wh_picking', '=', True),
                                          (
                                              'picking_id.amazon_shipment_id', '=', amazon_shipment_id),
                                          ('product_id', '=', amazon_product.product_id.id),
                                          ('state', '=', 'done'),
                                          ('location_id', '=', location_id),
                                          ('location_dest_id', '=', location_dest_id)])
            if received_qty <= 0.0:
                if not done_moves:
                    continue
            for done_move in done_moves:
                received_qty = received_qty - done_move.product_qty
            if received_qty < 0.0:
                return_moves = move_obj.search([('picking_id.is_fba_wh_picking', '=', True),
                                                ('picking_id.amazon_shipment_id', '=',
                                                 amazon_shipment_id),
                                                ('product_id', '=', amazon_product.product_id.id),
                                                ('state', '=', 'done'),
                                                ('location_id', '=', location_dest_id),
                                                ('location_dest_id', '=', location_id)])
                for return_move in return_moves:
                    received_qty = received_qty + return_move.product_qty
                if received_qty >= 0.0:
                    continue
                if not return_picking:
                    pick_type_id = pickings[0].picking_type_id.return_picking_type_id and pickings[
                        0].picking_type_id.return_picking_type_id.id or pickings[
                                       0].picking_type_id.id
                    return_picking = pickings[0].copy({
                        'move_lines': [],
                        'picking_type_id': pick_type_id,
                        'state': 'draft',
                        'origin': amazon_shipment_id,
                        'location_id': done_moves[0].location_dest_id.id,
                        'location_dest_id': done_moves[0].location_id.id,
                    })
                    return_picking.message_post(
                        body=_("<b> Inbound Shipment Report Downloaded </b>"),
                        attachment_ids=attachment_ids)
                received_qty = abs(received_qty)
                for move in done_moves:
                    if move.product_qty <= received_qty:
                        return_qty = move.product_qty
                    else:
                        return_qty = received_qty
                    move.copy({
                        'product_id': move.product_id.id,
                        'product_uom_qty': abs(received_qty),
                        'picking_id': return_picking.id,
                        'state': 'draft',
                        'location_id': move.location_dest_id.id,
                        'location_dest_id': move.location_id.id,
                        'picking_type_id': pick_type_id,
                        'warehouse_id': pickings[0].picking_type_id.warehouse_id.id,
                        'origin_returned_move_id': move.id,
                        'procure_method': 'make_to_stock',
                        'move_dest_id': False,
                    })
                    received_qty = received_qty - return_qty
                    if received_qty <= 0.0:
                        break
        if return_picking:
            return_picking.action_confirm()
            return_picking.action_assign()
            for move in return_picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
                move_line_remaning_qty = (move.product_uom_qty) - (
                    sum(move.move_line_ids.mapped('qty_done')))
                if move_line_remaning_qty > 0.0:
                    stock_move_line_obj.create(
                        {
                            'product_id': move.product_id.id,
                            'product_uom_id': move.product_id.uom_id.id,
                            'picking_id': return_picking.id,
                            'qty_done': float(move_line_remaning_qty) or 0,
                            'ordered_qty': float(move_line_remaning_qty) or 0,
                            'result_package_id': False,
                            'location_id': return_picking.location_id.id,
                            'location_dest_id': return_picking.location_dest_id.id,
                            'move_id': move.id,
                        })
            return_picking.with_context(
                {'auto_processed_orders_ept': True}).action_done()

        else:
            attachments = self.env['ir.attachment'].browse(attachment_ids)
            attachments.unlink()
        return True

    def _amz_stock_picking_put_in_pack_ept(self, operation):
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
        return True

    @api.multi
    def check_amazon_shipment_status(self):
        if self.ids:
            pickings = self
        else:
            pickings = self.search([('state', 'in', ['partially_available', 'assigned']),
                                    ('odoo_shipment_id', '!=', False),
                                    ('amazon_shipment_id', '!=', False),
                                    ('is_fba_wh_picking', '=', True)])

        move_obj = self.env['stock.move']
        amazon_product_obj = self.env['amazon.product.ept']
        stock_move_line_obj = self.env['stock.move.line']
        inbound_shipment_plan_line_obj = self.env['inbound.shipment.plan.line']

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        amazon_shipment_ids = []
        for picking in pickings:
            odoo_shipment_id = picking.odoo_shipment_id and picking.odoo_shipment_id.id
            amazon_shipment_ids.append(odoo_shipment_id)
            instance = picking.odoo_shipment_id.get_instance(picking.odoo_shipment_id)
            proxy_data = instance.seller_id.get_proxy_server()

            kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                      'auth_token': instance.auth_token and str(instance.auth_token) or False,
                      'app_name': 'amazon_ept',
                      'account_token': account.account_token,
                      'emipro_api': 'check_amazon_shipment_status',
                      'dbuuid': dbuuid,
                      'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                                 instance.country_id.code,
                      'proxies': proxy_data,
                      'amazon_shipment_id': picking.amazon_shipment_id, }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
            if response.get('reason'):
                raise Warning(response.get('reason'))
            else:
                items = response.get('items')
                datas = response.get('datas')

            for data in datas:
                file_name = 'inbound_shipment_report_%s.xml' % (picking.id)
                if data.get('next_tone'):
                    file_name = 'inbound_shipment_report_%s_%s.xml' % (picking.id, str(data.get('next_token')))

                attachment = self.env['ir.attachment'].create({
                    'name': file_name,
                    'datas': base64.b64encode((data.get('origin')).encode('utf-8')),
                    'datas_fname': file_name,
                    'res_model': 'mail.compose.message',
                })
                picking.message_post(body=_("<b> Inbound Shipment Report Downloaded </b>"),
                                     attachment_ids=attachment.ids)

            process_picking = False
            for item in items:
                sku = item.get('SellerSKU', {}).get('value', '')
                asin = item.get('FulfillmentNetworkSKU', {}).get('value', '')
                shipped_qty = item.get('QuantityShipped', {}).get('value')
                received_qty = float(item.get('QuantityReceived', {}).get('value', 0.0))
                if received_qty <= 0.0:
                    continue
                amazon_product = amazon_product_obj.search_amazon_product(instance.id, sku, 'AFN')
                if not amazon_product:
                    amazon_product = amazon_product_obj.search(
                        [('product_asin', '=', asin), ('instance_id', '=', instance.id),
                         ('fulfillment_by', '=', 'AFN')], limit=1)
                if not amazon_product:
                    picking.message_post(body=_("""Product not found in ERP ||| 
                                                FulfillmentNetworkSKU : %s
                                                SellerSKU : %s  
                                                Shipped Qty : %s
                                                Received Qty : %s                          
                                             """ % (asin, sku, shipped_qty, received_qty)))
                    continue

                inbound_shipment_plan_line_id = inbound_shipment_plan_line_obj.search(
                    [('odoo_shipment_id', '=', odoo_shipment_id),
                     ('amazon_product_id', '=', amazon_product.id)], limit=1)
                if inbound_shipment_plan_line_id:
                    inbound_shipment_plan_line_id.received_qty = received_qty or 0.0
                else:
                    vals = {
                        'amazon_product_id': amazon_product.id,
                        'quantity': shipped_qty or 0.0,
                        'odoo_shipment_id': odoo_shipment_id,
                        'fn_sku': asin,
                        'received_qty': received_qty,
                        'is_extra_line': True
                    }
                    inbound_shipment_plan_line_obj.create(vals)

                odoo_product_id = amazon_product and amazon_product.product_id.id or False
                done_moves = move_obj.search([('picking_id.is_fba_wh_picking', '=', True), (
                    'picking_id.amazon_shipment_id', '=', picking.amazon_shipment_id),
                                              ('product_id', '=', odoo_product_id),
                                              ('state', '=', 'done')], order="id")
                source_location_id = done_moves and done_moves[0].location_id.id
                for done_move in done_moves:
                    if done_move.location_dest_id.id != source_location_id:
                        received_qty = received_qty - done_move.product_qty
                    else:
                        received_qty = received_qty + done_move.product_qty
                if received_qty <= 0.0:
                    continue
                move_lines = move_obj.search(
                    [('picking_id', '=', picking.id), ('product_id', '=', odoo_product_id),
                     ('state', 'not in', ('draft', 'done', 'cancel', 'waiting'))])
                if not move_lines:
                    move_lines = move_obj.search(
                        [('picking_id', '=', picking.id), ('product_id', '=', odoo_product_id),
                         ('state', 'not in', ('draft', 'done', 'cancel'))])
                for move_line in move_lines:
                    if move_line.state == 'waiting':
                        move_line.write({'state': 'assigned'})
                        # force availability
                if not move_lines and instance.allow_process_unshipped_products:
                    process_picking = True
                    move = picking.move_lines[0]
                    odoo_product = amazon_product.product_id
                    new_move = move_obj.create({
                        'name': _('New Move:') + odoo_product.display_name,
                        'product_id': odoo_product.id,
                        'product_uom_qty': received_qty,
                        'product_uom': odoo_product.uom_id.id,
                        'location_id': picking.location_id.id,
                        'location_dest_id': picking.location_dest_id.id,
                        'picking_id': picking.id,
                    })
                    stock_move_line_obj.create(
                        {
                            'product_id': move.product_id.id,
                            'product_uom_id': move.product_id.uom_id.id,
                            'picking_id': picking.id,
                            'qty_done': float(received_qty) or 0,
                            'ordered_qty': float(received_qty) or 0,
                            'location_id': picking.location_id.id,
                            'location_dest_id': picking.location_dest_id.id,
                            'move_id': new_move.id,
                        })
                elif not move_lines and not instance.allow_process_unshipped_products:
                    picking.message_post(body=_("""Line skipped due to move not found in ERP ||| 
                                                FulfillmentNetworkSKU : %s
                                                SellerSKU : %s  
                                                Shipped Qty : %s
                                                Received Qty : %s                          
                                             """ % (asin, sku, shipped_qty, received_qty)))
                qty_left = received_qty
                for move in move_lines:
                    process_picking = True
                    if qty_left <= 0.0:
                        break
                    move_line_remaning_qty = (move.product_uom_qty) - (
                        sum(move.move_line_ids.mapped('qty_done')))
                    operations = move.move_line_ids.filtered(lambda o: o.qty_done <= 0)
                    for operation in operations:
                        if operation.product_uom_qty <= qty_left:
                            op_qty = operation.product_uom_qty
                        else:
                            op_qty = qty_left
                        operation.write({'qty_done': op_qty})
                        self._amz_stock_picking_put_in_pack_ept(operation)
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
                                'result_package_id': False,
                                'location_id': picking.location_id.id,
                                'location_dest_id': picking.location_dest_id.id,
                                'move_id': move.id,
                            })
                        qty_left = float_round(qty_left - op_qty,
                                               precision_rounding=move.product_id.uom_id.rounding,
                                               rounding_method='UP')
                        if qty_left <= 0.0:
                            break
                if qty_left > 0.0 and move_lines:
                    stock_move_line_obj.create(
                        {
                            'product_id': move_lines[0].product_id.id,
                            'product_uom_id': move_lines[0].product_id.uom_id.id,
                            'picking_id': picking.id,
                            'ordered_qty': float(qty_left) or 0,
                            'qty_done': float(qty_left) or 0,
                            'result_package_id': False,
                            'location_id': picking.location_id.id,
                            'location_dest_id': picking.location_dest_id.id,
                            'move_id': move_lines[0].id,
                        })

            process_picking and picking.with_context(
                {'auto_processed_orders_ept': True}).action_done()
        return True

    @api.multi
    def update_shipment_quantity(self):
        amazon_product_obj = self.env['amazon.product.ept']
        plan_line_obj = self.env['inbound.shipment.plan.line']

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        for picking in self:
            odoo_shipment = picking.odoo_shipment_id
            ship_plan = picking.ship_plan_id
            instance = ship_plan.instance_id
            address = picking.partner_id or ship_plan.ship_from_address_id
            name, add1, add2, city, postcode = address.name, address.street or '', address.street2 or '', address.city or '', address.zip or ''
            country = address.country_id and address.country_id.code or ''
            state = address.state_id and address.state_id.code or ''
            shipment_status = 'WORKING'
            amazon_product_obj = self.env['amazon.product.ept']
            if not odoo_shipment.shipment_id or not odoo_shipment.fulfill_center_id:
                raise Warning('You must have to first create Inbound Shipment Plan.')
            proxy_data = instance.seller_id.get_proxy_server()

            for x in range(0, len(picking.move_lines), 20):
                move_lines = picking.move_lines[x:x + 20]
                sku_qty_dict = {}
                for move in move_lines:
                    amazon_product = amazon_product_obj.search(
                        [('product_id', '=', move.product_id.id), ('instance_id', '=', instance.id),
                         ('fulfillment_by', '=', 'AFN')], limit=1)
                    if not amazon_product:
                        raise Warning("Amazon Product is not available for this %s product code" % (
                            move.product_id.default_code))
                    line = plan_line_obj.search([('odoo_shipment_id', '=', odoo_shipment.id),
                                                 ('amazon_product_id', 'in', amazon_product.ids)])
                    sku_qty_dict.update({str(
                        line and line.seller_sku or amazon_product[0].seller_sku): str(
                        int(move.reserved_availability))})

                    kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                              'auth_token': instance.auth_token and str(instance.auth_token) or False,
                              'app_name': 'amazon_ept',
                              'account_token': account.account_token,
                              'emipro_api': 'update_shipment_in_amazon',
                              'dbuuid': dbuuid,
                              'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                                         instance.country_id.code,
                              'proxies': proxy_data,
                              'shipment_name': odoo_shipment.name,
                              'shipment_id': odoo_shipment.shipment_id,
                              'fulfill_center_id': odoo_shipment.fulfill_center_id,
                              'address_name': name,
                              'add1': add1,
                              'add2': add2,
                              'city': city,
                              'state': state,
                              'postcode': postcode,
                              'country': country,
                              'labelpreppreference': odoo_shipment.label_prep_type,
                              'shipment_status': shipment_status,
                              'inbound_box_content_status': odoo_shipment.intended_boxcontents_source,
                              'sku_qty_dict': sku_qty_dict,
                              }
                    response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                    if response.get('reason'):
                        raise Warning(response.get('reason'))

            picking.write({'inbound_ship_updated': True})
        return True

    @api.model
    def transfer_picking(self):
        self.do_transfer()
        return True

    @api.multi
    def create_shipment(self, order, result_wrapper):
        amazon_product_obj = self.env['amazon.product.ept']
        quant_package_obj = self.env["stock.quant.package"]
        move_obj = self.env['stock.move']
        stock_pack_operation = self.env['stock.move.line']
        order_status = result_wrapper.get('FulfillmentOrder', {}).get(
            'FulfillmentOrderStatus', {}).get('value')
        order.write({'amz_fulfullment_order_status': order_status})
        for picking in order.picking_ids:
            if picking.state in ['draft', 'cancel', 'done']:
                continue
            if picking.state in ['confirmed', 'partially_available']:
                picking.action_assign()
            pack_op_ods = []
            package_ids = []
            for member in result_wrapper.get('FulfillmentShipment', {}):
                fulfillment_shipment_status = member.get('FulfillmentShipmentStatus', {}).get(
                    'value', False)
                if fulfillment_shipment_status != 'SHIPPED':
                    continue
                shipment_date_time = member.get('ShippingDateTime')
                shipment_id = member.get('AmazonShipmentId')

                if picking.amazon_outbound_shipment_id == shipment_id:
                    continue
                for item in member.get('FulfillmentShipmentItem', {}):
                    seller_sku = item.get('SellerSKU', {}).get('value', False)
                    seller_fulfillment_item_id = item.get('SellerFulfillmentOrderItemId', {}).get(
                        'value', False)
                    quantity = item.get('Quantity', {}).get('value', 0.0)
                    package_number = item.get('PackageNumber', {}).get('value', False)
                    amazon_product = amazon_product_obj.search_amazon_product(
                        order.amz_instance_id.id, seller_sku, 'AFN')
                    odoo_product_id = amazon_product and amazon_product.product_id.id or False
                    move_lines = move_obj.search(
                        [('picking_id', '=', picking.id), ('product_id', '=', odoo_product_id),
                         ('state', 'in', ('confirmed', 'assigned'))])
                    if len(move_lines) == 0:
                        continue

                    package = quant_package_obj.create({'amazon_package_no': package_number,
                                                        'instance_id': order.amz_instance_id.id})
                    pack_op = stock_pack_operation.create(
                        {
                            'date': time.strftime('%Y-%m-%d'),
                            'location_id': move_lines[0].location_id and move_lines[
                                0].location_id.id or False,
                            'location_dest_id': move_lines[0].location_dest_id and move_lines[
                                0].location_dest_id.id or False,
                            'product_id': move_lines[0].product_id and move_lines[
                                0].product_id.id or False,
                            'product_uom_id': move_lines[0].product_id and move_lines[
                                0].product_id.uom_id and move_lines[
                                                  0].product_id.uom_id.id or False,
                            'processed': 'true',
                            'qty_done': quantity or 0,
                            'picking_id': picking.id,
                            'result_package_id': package.id,
                        })
                    pack_op_ods.append(pack_op.id)
                    package_ids.append(package.id)
                for item in result_wrapper.get('FulfillmentShipmentPackage', {}):
                    package_no = item.get('PackageNumber', {}).get('value', {})
                    tracking_no = item.get('TrackingNumber', {}).get('value', {})
                    carrier_code = item.get('CarrierCode', {}).get('value', {})
                    carrier = self.env['delivery.carrier'].search([('name', '=', carrier_code)])
                    carrier and picking.write({'carrier_id', '=', carrier.id})
                    package = quant_package_obj.search(
                        [('id', 'in', package_ids), ('amazon_package_no', '=', package_no)])
            exists_pack_ops = stock_pack_operation.search(
                [('picking_id', 'in', picking.ids), ('id', 'not in', pack_op_ods)])
            exists_pack_ops and exists_pack_ops.unlink()
            picking.do_transfer()
            picking.write({'amazon_outbound_shipment_id': shipment_id})
            back_order = picking.backorder_id

        if order_status in ['CANCELLED', 'COMPLETE', 'COMPLETE_PARTIALLED', 'UNFULFILLABLE']:
            for picking in order.picking_ids:
                if picking.state in ['done', 'cancel']:
                    continue
                for member in result_wrapper.get('FulfillmentOrderItem', {}):
                    seller_sku = member.get('SellerSKU', {}).get('value')
                    amazon_product = amazon_product_obj.search_amazon_product(
                        order.amz_instance_id.id, seller_sku, 'AFN')
                    odoo_product_id = amazon_product and amazon_product.product_id.id or False
                    quantity = member.get('CancelledQuantity', 0.0)

                    move_lines = move_obj.search(
                        [('picking_id', '=', back_order.id), ('product_id', '=', odoo_product_id),
                         ('state', 'in', ('confirmed', 'assigned'))])
                    if len(move_lines) == 0:
                        continue
                    total_quantity = 0.0
                    for move in move_lines:
                        total_quantity = total_quantity + move.product_qty
                    if round(total_quantity, 2) == round(quantity, 2):
                        move_lines.action_cancel()
                    else:
                        remain_qty = quantity
                        for move_line in move_lines:
                            if round(quantity, 2) <= round(move_line.product_qty, 2):
                                move_line.action_cancel()
                                remain_qty = remain_qty - move.product_qty
                            elif round(quantity, 2) >= round(move_line.product_qty, 2):
                                new_move_ids = move_line.split(qty=quantity)
                                new_moves = self.env['stock.move'].browse(new_move_ids)
                                new_moves.action_cancel()
                                remain_qty = remain_qty - quantity
                            if round(remain_qty, 2) <= 0.0:
                                break
                            quantity = remain_qty
            return True

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        vals = super(stock_picking, self)._get_invoice_vals(key, inv_type, journal_id, move)
        fiscal_position = move.picking_id.fiscal_position
        if fiscal_position:
            vals.update({
                'fiscal_position': fiscal_position.id
            })
        return vals

    @api.multi
    def mark_sent_amazon(self):
        for picking in self:
            picking.write({'updated_in_amazon': False})
        return True

    @api.multi
    def mark_not_sent_amazon(self):
        for picking in self:
            picking.write({'updated_in_amazon': True})
        return True

    @api.multi
    def send_to_shipper(self):
        context = dict(self._context)
        if context.get('auto_processed_orders_ept', False):
            return True
        else:
            return super(stock_picking, self).send_to_shipper()
