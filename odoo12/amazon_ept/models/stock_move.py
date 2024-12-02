from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class stock_move(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"
    _description = "Stock Move"

    updated_in_amazon = fields.Boolean("Update Status in Amazon", default=False,
                                       help="Use only for phantom products")

    # added by Dhruvi
    seller_id = fields.Many2one("amazon.seller.ept", "Seller")
    
    
    # added by twinkal to merge with FBA
    shipment_line_id = fields.Many2one('inbound.shipment.plan.line', string="Shiment Plan Line")
    shipment_item_id = fields.Char(size=120, string='Amazon Shipment Item ID', default=False,
                                   help="Shipment Item ID provided by Amazon when we integrate "
                                        "shipment report from Amazon")
    return_created = fields.Boolean(string='FBA Return Created', default=False, copy=False)
    fba_returned_date = fields.Datetime("Return Date")
    return_reason_id = fields.Many2one("amazon.return.reason.ept", string="Return Reason")
    detailed_disposition = fields.Selection([('SELLABLE', 'SELLABLE'), ('DAMAGED', 'DAMAGED'),
                                             ('CUSTOMER_DAMAGED', 'CUSTOMER DAMAGED'),
                                             ('DEFECTIVE', 'DEFECTIVE'),
                                             ('CARRIER_DAMAGED', 'CARRIER DAMAGED'),
                                             ('EXPIRED', 'EXPIRED'),
                                             ('CARRIER_DAMAGED', 'CARRIER DAMAGED'),
                                             ('CUSTOMER DAMAGED', 'CUSTOMER DAMAGED')],
                                            string='Detailed Disposition')
    fulfillment_center_id = fields.Many2one("amazon.fulfillment.center",
                                            stirng='fulfillment center')
    status = fields.Char(string='State')    
    
    adjusted_date=fields.Datetime("Adjsutment Time",copy=False)
    transaction_item_id=fields.Char("Transaction Item",copy=False)
    fulfillment_center_id = fields.Many2one('amazon.fulfillment.center',string='Fulfillment Center',copy=False)                
    code_id=fields.Many2one('amazon.adjustment.reason.code',string='FBA Stock Adjustment Code',copy=False)
    code_description=fields.Char("FBA Stock Adjustment Description")    

    # Added categ_id and related function by Uday on 18-05-2024

    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        related='product_id.product_tmpl_id.categ_id',
        readonly=True, store=True, help="Product category from the product form view")
    
    
    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        res = super(stock_move, self)._create_account_move_line(credit_account_id, debit_account_id,
                                                                journal_id)
        for move in self.account_move_ids:
            if not move.seller_id:
                move.seller_id = self.picking_id.seller_id and self.picking_id.seller_id.id or False
            if not move.amazon_instance_id:
                move.amazon_instance_id = self.picking_id.amazon_instance_id and \
                                          self.picking_id.amazon_instance_id.id or False

        return res

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        res = super(stock_move, self)._prepare_account_move_line(qty, cost, credit_account_id,
                                                                 debit_account_id)
        for row in res:
            row[2].update(
                {'seller_id': self.picking_id.seller_id and self.picking_id.seller_id.id or False,
                 'amazon_instance_id': self.picking_id.amazon_instance_id and
                                       self.picking_id.amazon_instance_id.id or False})
        return res
    
    # added by twinkal to merge removal order module
    @api.model
    def _prepare_picking_assign(self,move):
        """ Prepares a new picking for this move as it could not be assigned to
        another picking. This method is designed to be inherited.
        """
        values = super(stock_move,self)._prepare_picking_assign(move)
        proc_group = move.group_id
        if proc_group and proc_group.removal_order_id:
            values.update({
                        'partner_id' : proc_group.removal_order_id.ship_address_id and proc_group.removal_order_id.ship_address_id.id,
                        'removal_order_id':proc_group.removal_order_id.id 
                        })
        return values    

    @api.multi
    def write(self, vals):
        res = super(stock_move, self).write(vals)
        if vals.get('state', False) and vals.get('state', '') == 'done':
            product_instance_dict = {}
            location_obj = self.env['stock.location']
            amazon_product_obj = self.env['amazon.product.ept']
            cur_usr = self.env['res.users'].browse(self._uid)
            if cur_usr.has_group('amazon_ept.group_amazon_user_ept'):
                for instance in self.env['amazon.instance.ept'].search(
                        [('update_stock_on_fly', '=', True)]):
                    for move in self:
                        if move.state != 'done' or not move.product_id:
                            continue
                        amazon_location_id = instance.warehouse_id.lot_stock_id.id or False
                        amazon_location_ids = location_obj.search(
                            [('child_ids', 'child_of', [amazon_location_id])])
                        if move.location_id.id in amazon_location_ids.ids or move.location_dest_id.id in amazon_location_ids.ids:
                            ctx = self.env.context.copy()
                            ctx.update({'location': amazon_location_id})
                            product_obj = move.product_id.with_context(ctx)
                            amazon_product = amazon_product_obj.search(
                                [('product_id', '=', product_obj.id),
                                 ('exported_to_amazon', '=', True),
                                 ('instance_id', '=', instance.id), ('fulfillment_by', '=', 'MFN')])
                            if not amazon_product:
                                continue
                            if hasattr(product_obj, instance.stock_field.name):
                                product_qty_available = getattr(product_obj,
                                                                instance.stock_field.name)
                            else:
                                product_qty_available = product_obj.qty_available
                            sku = amazon_product.seller_sku or product_obj.default_code
                            if instance in product_instance_dict:
                                product_instance_dict[instance].update({sku: product_qty_available})
                            else:
                                product_instance_dict.update(
                                    {instance: {sku: product_qty_available}})
            if product_instance_dict:
                self.export_stock_to_amazon(product_instance_dict)
        return res

    @api.multi
    def export_stock_to_amazon(self, product_instance_dict):
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        
        for instance in product_instance_dict:
            message_information = ''
            message_id = 1
            merchant_string = "<MerchantIdentifier>%s</MerchantIdentifier>" % (instance.merchant_id)
            for sku, qty in product_instance_dict[instance].items():
                message_information += """<Message><MessageID>%s</MessageID><OperationType>Update</OperationType><Inventory><SKU>%s</SKU><Quantity>%d</Quantity></Inventory></Message>""" % (
                message_id, sku, int(qty))
                message_id = message_id + 1
            if message_information:
                data = """<?xml version="1.0" encoding="utf-8"?><AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd"><Header><DocumentVersion>1.01</DocumentVersion>""" + merchant_string + """</Header><MessageType>Inventory</MessageType>""" + message_information + """</AmazonEnvelope>"""
                proxy_data = instance.seller_id.get_proxy_server()

                kwargs = {'merchant_id':instance.merchant_id and str(instance.merchant_id) or False,
                          'auth_token':instance.auth_token and str(instance.auth_token) or False,
                          'app_name':'amazon_ept',
                          'account_token':account.account_token,
                          'emipro_api':'export_stock_levels',
                          'dbuuid':dbuuid,
                          'amazon_marketplace_code':instance.country_id.amazon_marketplace_code or
                                        instance.country_id.code,
                          'proxies':proxy_data,
                          'marketplaceids': [instance.market_place_id],
                          'instance_id':instance.id,
                          'data': data,}
                
                response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
                if response.get('reason'):                
                    raise Warning(response.get('reason'))

        return True

    def _get_new_picking_values(self):
        """We need this method to set Amazon Instance in Stock Picking"""
        res = super(stock_move, self)._get_new_picking_values()
        order_id = self.sale_line_id.order_id
        if order_id.amazon_reference != False:
            order_id and res.update({'amazon_instance_id': order_id.amz_instance_id.id,
                                     'is_amazon_delivery_order': True,
                                     'seller_id': order_id.seller_id.id,
                                     # 'global_channel_id':order_id.global_channel_id.id
                                     })
            
        proc_group = self.group_id
        if proc_group and proc_group.odoo_shipment_id:
            res.update({
                'partner_id': proc_group.odoo_shipment_id.address_id and
                              proc_group.odoo_shipment_id.address_id.id,
                'ship_plan_id': proc_group.odoo_shipment_id.shipment_plan_id and
                                proc_group.odoo_shipment_id.shipment_plan_id.id,
                'amazon_shipment_id': proc_group.odoo_shipment_id.shipment_id,
                'ship_label_preference': proc_group.odoo_shipment_id.label_prep_type,
                'fulfill_center': proc_group.odoo_shipment_id.fulfill_center_id,
                'odoo_shipment_id': proc_group.odoo_shipment_id.id,
                'seller_id': proc_group.odoo_shipment_id and
                             proc_group.odoo_shipment_id.shipment_plan_id and
                             proc_group.odoo_shipment_id.shipment_plan_id.instance_id.seller_id and
                             proc_group.odoo_shipment_id.shipment_plan_id.instance_id.seller_id.id or
                             False,
                'global_channel_id': proc_group.odoo_shipment_id and
                                     proc_group.odoo_shipment_id.shipment_plan_id and
                                     proc_group.odoo_shipment_id.shipment_plan_id.instance_id.seller_id and
                                     proc_group.odoo_shipment_id.shipment_plan_id.instance_id.seller_id.global_channel_id and
                                     proc_group.odoo_shipment_id.shipment_plan_id.instance_id.seller_id.global_channel_id.id or False
            })
        if self.sale_line_id and self.sale_line_id.order_id:
            sale_order = self.sale_line_id.order_id
            if sale_order.amazon_reference != False:
                res.update({'fulfillment_by': sale_order.amz_fulfillment_by})
        return res
    
    
class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    def _free_reservation_ept(self, product_id, location_id, quantity, lot_id=None, package_id=None,
                              owner_id=None, ml_to_ignore=None):

        """ When editing a done move line or validating one with some forced quantities, it is
        possible to impact quants that were not reserved. It is therefore necessary to edit or
        unlink the move lines that reserved a quantity now unavailable.
        """
        self.ensure_one()

        if ml_to_ignore is None:
            ml_to_ignore = self.env['stock.move.line']
        ml_to_ignore |= self

        # Check the available quantity, with the `strict` kw set to `True`. If the available
        # quantity is greather than the quantity now unavailable, there is nothing to do.
        available_quantity = self.env['stock.quant']._get_available_quantity(
            product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
            strict=True
        )
        if quantity > available_quantity:
            # We now have to find the move lines that reserved our now unavailable quantity. We
            # take care to exclude ourselves and the move lines were work had already been done.
            oudated_move_lines_domain = [
                ('move_id.state', 'not in', ['done', 'cancel']),
                ('product_id', '=', product_id.id),
                ('lot_id', '=', lot_id.id if lot_id else False),
                ('location_id', '=', location_id.id),
                ('owner_id', '=', owner_id.id if owner_id else False),
                ('package_id', '=', package_id.id if package_id else False),
                ('product_qty', '>', 0.0),
                ('id', 'not in', self.move_id.move_line_ids.ids),
            ]
            oudated_candidates = self.env['stock.move.line'].search(oudated_move_lines_domain)

            # As the move's state is not computed over the move lines, we'll have to manually
            # recompute the moves which we adapted their lines.
            move_to_recompute_state = self.env['stock.move']

            rounding = self.product_uom_id.rounding
            for candidate in oudated_candidates:
                if float_compare(candidate.product_qty, quantity, precision_rounding=rounding) <= 0:
                    quantity -= candidate.product_qty
                    move_to_recompute_state |= candidate.move_id
                    if candidate.qty_done:
                        candidate.product_uom_qty = 0.0
                    else:
                        candidate.unlink()
                else:
                    # split this move line and assign the new part to our extra move
                    quantity_split = float_round(
                        candidate.product_qty - quantity,
                        precision_rounding=self.product_uom_id.rounding,
                        rounding_method='UP')
                    candidate.product_uom_qty = self.product_id.uom_id._compute_quantity(
                        quantity_split, self.product_uom_id, rounding_method='HALF-UP')
                    quantity -= quantity_split
                    move_to_recompute_state |= candidate.move_id
                if quantity <= 0.0:
                    break
            move_to_recompute_state._recompute_state()
    
