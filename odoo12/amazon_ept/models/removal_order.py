from odoo import models, fields, api, _
from tempfile import NamedTemporaryFile
from odoo.exceptions import Warning
import odoo.addons.decimal_precision as dp
import base64
import time
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class removal_order(models.Model):
    _name = "amazon.removal.order.ept"
    _description = "Removal Order"
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.multi
    def write(self, vals):
        if 'removal_disposition' in vals:
            if vals.get('removal_disposition') == 'Disposal':
                self.removal_order_lines_ids.write({'removal_disposition': 'Disposal', 'sellable_quantity': 0.0})
            else:
                self.removal_order_lines_ids.write({'removal_disposition': 'Return'})
        return super(removal_order, self).write(vals)

    @api.multi
    def import_product_for_removal_order(self):
        """
            Open wizard to import product through csv file.
            File contains only product sku and quantity.
        """
        import_obj = self.env['import.product.removal.order.wizard'].create({'removal_order_id': self.id})

        ctx = self._context.copy()
        ctx.update({'removal_order_id': self.id, 'update_existing': False, })
        return import_obj.with_context(ctx).wizard_view()

    @api.multi
    def removal_count_records(self):
        for record in self:
            record.removal_count = len(record.removal_order_picking_ids.ids)

    @api.multi
    def get_unsellable_products(self):
        removal_order_line_obj = self.env['removal.orders.lines.ept']
        products = self.env['amazon.product.ept'].search(
            ['|', ('product_id.company_id', '=', False), ('product_id.company_id', '=', self.env.user.company_id.id),
             ('instance_id', '=', self.instance_id.id), ('fulfillment_by', '=', 'AFN')])
        for product in products:
            unsellable_stock = product.product_id.with_context(
                {'location': self.instance_id.fba_warehouse_id.unsellable_location_id.id}).qty_available
            if unsellable_stock > 0.0:
                line = removal_order_line_obj.search(
                    [('amazon_product_id', '=', product.id), ('removal_order_id', '=', self.id)])
                if line:
                    line.write({'unsellable_quantity': unsellable_stock, 'sellable_quantity': 0.0,
                                'removal_disposition': self.removal_disposition})
                else:
                    removal_order_line_obj.create({
                        'amazon_product_id': product.id,
                        'unsellable_quantity': unsellable_stock,
                        'removal_order_id': self.id,
                        'removal_disposition': self.removal_disposition
                    })
        return True

    name = fields.Char("Name")  # ,copy=False
    removal_disposition = fields.Selection([('Return', 'Return'), ('Disposal', 'Disposal')], default='Return',
                                           required=True)
    ship_address_id = fields.Many2one('res.partner', string='Ship Address', readonly=True,
                                      states={'draft': [('readonly', False)]})
    shipping_notes = fields.Text("Notes")
    instance_id = fields.Many2one('amazon.instance.ept', string='Instance', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one("stock.warehouse",
                                   string="Destination Warehouse")  # related=instance_id.removal_warehouse_id
    disposition_location_id = fields.Many2one("stock.location",
                                              related="instance_id.fba_warehouse_id.unsellable_location_id",
                                              readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, )
    state = fields.Selection([('draft', 'Draft'),
                              ('plan_approved', 'Removal Plan Approved'),
                              ('Cancelled', 'Cancelled'),
                              ('In Process', 'In Process'),
                              ('Completed', 'Completed')
                              ], default='draft',
                             string='State')
    removal_order_lines_ids = fields.One2many("removal.orders.lines.ept", 'removal_order_id',
                                              string="Removal Orders Lines")
    last_feed_submission_id = fields.Char("Feed Submission Id")
    removal_order_picking_ids = fields.One2many("stock.picking", 'removal_order_id', string="Removal Pickings")
    removal_count = fields.Integer("Removal Order Pickings", compute="removal_count_records")

    @api.onchange('instance_id', 'warehouse_id')
    def onchange_instance_id(self):
        if self.instance_id:
            warehouse = self.instance_id.removal_warehouse_id
            if not warehouse:
                warehouse = self.instance_id.warehouse_id
            if warehouse:
                self.warehouse_id = warehouse.id
                self.ship_address_id = warehouse.partner_id and warehouse.partner_id.id or False
            self.company_id = self.instance_id.company_id.id

    @api.multi
    def list_of_transfer_removal_pickings(self):
        action = {
            'domain': "[('id', 'in', " + str(self.removal_order_picking_ids.ids) + " )]",
            'name': 'Removal Order Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.multi
    def check_validate_fields(self):
        address = self.ship_address_id
        if self.removal_disposition == 'Return':
            message = "One of address required fields are not set like street,city,country,state,zip,phone"
        else:
            message = "One of address required fields are not set like street,city,country,state,zip"

        if not (
                address.street or address.street2) or not address.city or not address.country_id or not address.state_id or not address.zip or \
                (self.removal_disposition == 'Return' and not (address.phone or address.mobile)):
            raise Warning(message)
        if not self.removal_order_lines_ids:
            raise Warning("Invalid lines found for request")
        lines = self.env['removal.orders.lines.ept'].search(
            [('sellable_quantity', '<=', 0.0), ('unsellable_quantity', '<=', 0.0),
             ('id', 'in', self.removal_order_lines_ids.ids)])
        seller_skus = [x.seller_sku for x in list(lines)]
        if seller_skus:
            raise Warning("Invalid Lines found for request %s" % (','.join(seller_skus)))
        if self.removal_disposition == 'Disposal' and not self.instance_id.fba_warehouse_id.unsellable_location_id:
            raise Warning("Unsellable Location not found in FBA warehouse")
        if not self.instance_id.removal_order_config_ids:
            raise Warning("Removal order configuration missing in seller")
        config = self.env['removal.order.config.ept'].search(
            [('id', 'in', self.instance_id.removal_order_config_ids.ids),
             ('removal_disposition', '=', self.removal_disposition)])
        if not config:
            raise Warning("Removal Order configuration missing for disposition %s" % (self.removal_disposition))
        if self.removal_disposition == 'Return':
            if not config.unsellable_route_id or not config.sellable_route_id:
                raise Warning("Route Configuration is missing in seller")
        if self.removal_disposition == 'Disposal':
            if not config.picking_type_id or not config.location_id:
                raise Warning("Location or picking type configuration is missing in seller")
        if self.removal_order_picking_ids.filtered(lambda picking: picking.state != 'cancel'):
            raise Warning("Pickings already exist for removal order first you should cancel all pickings")
        return True

    @api.multi
    def create_pickings(self):
        if self.removal_disposition == 'Return':
            self.removal_order_procurements()
        elif self.removal_disposition == 'Disposal':
            self.disposal_order_pickings()
        return True

    @api.multi
    def create_removal_order(self):
        self.ensure_one()
        instance = self.instance_id
        self.check_validate_fields()
        address = self.ship_address_id
        address_field_one = address.street or address.street2
        address_field_two = address.street and address.street2 or ''
        file_order_ship = NamedTemporaryFile(delete=False, mode='w')
        file_order_ship.write("MerchantRemovalOrderID\t%s\n" % (self.name))
        file_order_ship.write("RemovalDisposition\t%s\n" % (self.removal_disposition))
        file_order_ship.write("AddressName\t%s\n" % (address.name))
        file_order_ship.write("AddressFieldOne\t%s\n" % (address_field_one))
        file_order_ship.write("AddressFieldTwo\t%s\n" % (address_field_two))
        file_order_ship.write("AddressCity\t%s\n" % (address.city))
        file_order_ship.write("AddressCountryCode\t%s\n" % (address.country_id.code))
        file_order_ship.write("AddressStateOrRegion\t%s\n" % (address.state_id.code))
        file_order_ship.write("AddressPostalCode\t%s\n" % (address.zip))
        file_order_ship.write("ContactPhoneNumber\t%s\n" % (address.phone or address.mobile))
        file_order_ship.write("ShippingNotes\t%s\n" % (self.shipping_notes or ''))
        file_order_ship.write("\n")
        file_order_ship.write("MerchantSKU\tSellableQuantity\tUnsellableQuantity\n")
        for removal_line in self.removal_order_lines_ids:
            sellable_quantity = 0.0 if removal_line.sellable_quantity < 0.0 else removal_line.sellable_quantity
            unsellable_quantity = 0.0 if removal_line.unsellable_quantity < 0.0 else removal_line.unsellable_quantity
            file_order_ship.write(
                "%s\t%s\t%s\n" % (removal_line.seller_sku, int(sellable_quantity), int(unsellable_quantity)))
        file_order_ship.close()
        fl = open(file_order_ship.name, 'rb')
        data = fl.read()
        file_name = "removal_request_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id': instance.merchant_id and str(instance.merchant_id) or False,
                  'auth_token': instance.auth_token and str(instance.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'send_cancel_request_to_amazon',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': instance.country_id.amazon_marketplace_code or
                                             instance.country_id.code,
                  'marketplaceids': [instance.market_place_id],
                  'instance_id': instance.id,
                  'data': data}

        file_order_ship.delete
        if self.removal_disposition == 'Return':
            self.removal_order_procurements()
        elif self.removal_disposition == 'Disposal':
            self.disposal_order_pickings()

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))

        self.write({'state': 'plan_approved'})
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': base64.encodestring(data),
            'datas_fname': file_name,
            'res_model': 'mail.compose.message',
            'type': 'binary'
        })
        self.message_post(body=_("<b>Removal Request Created</b>"), attachment_ids=attachment.ids)
        return True

    @api.multi
    def disposal_order_pickings(self):
        picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        config = self.env['removal.order.config.ept'].search(
            [('id', 'in', self.instance_id.removal_order_config_ids.ids),
             ('removal_disposition', '=', self.removal_disposition)])
        picking_type_id = config.picking_type_id.id
        dest_location_id = config.location_id.id
        unsellable_source_location_id = self.disposition_location_id.id
        sellable_source_location_id = self.instance_id.fba_warehouse_id.lot_stock_id.id
        sellable_picking = False
        unsellable_picking = False
        for removal_line in self.removal_order_lines_ids:
            vals = {}
            amazon_product = removal_line.amazon_product_id
            sellable_quantity = 0.0 if removal_line.sellable_quantity < 0.0 else removal_line.sellable_quantity
            unsellable_quantity = 0.0 if removal_line.unsellable_quantity < 0.0 else removal_line.unsellable_quantity
            if sellable_quantity > 0.0:
                if not sellable_picking:
                    vals = self.create_picking_vals(picking_type_id, sellable_source_location_id, dest_location_id)
                    sellable_picking = picking_obj.create(vals)
                vals = self.create_move_vals(sellable_source_location_id, dest_location_id, amazon_product.product_id,
                                             sellable_quantity, sellable_picking.id)
                stock_move_obj.create(vals)
            if unsellable_quantity > 0.0:
                if not unsellable_picking:
                    vals1 = self.create_picking_vals(picking_type_id, unsellable_source_location_id, dest_location_id)
                    unsellable_picking = picking_obj.create(vals1)
                vals = self.create_move_vals(unsellable_source_location_id, dest_location_id, amazon_product.product_id,
                                             unsellable_quantity, unsellable_picking.id)
                stock_move_obj.create(vals)
        sellable_picking and sellable_picking.action_confirm()
        sellable_picking and sellable_picking.action_assign()

        unsellable_picking and unsellable_picking.action_confirm()
        unsellable_picking and unsellable_picking.action_assign()
        return True

    @api.multi
    def create_move_vals(self, location_id, location_dest_id, product_id, qty, picking_id):
        vals = {
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'product_uom_qty': qty,
            'name': product_id.name,
            'product_id': product_id.id,
            'state': 'draft',
            'picking_id': picking_id,
            'product_uom': product_id.uom_id.id,
            'company_id': self.instance_id.company_id.id
        }
        return vals

    @api.multi
    def create_picking_vals(self, picking_type_id, source_location_id, dest_location_id):
        return {
            'picking_type_id': picking_type_id,
            'partner_id': self.ship_address_id.id,
            'removal_order_id': self.id,
            'origin': self.name,
            'company_id': self.instance_id.company_id.id,
            'location_id': source_location_id,
            'location_dest_id': dest_location_id,
            'seller_id': self.instance_id and self.instance_id.seller_id and self.instance_id.seller_id.id or False,
            'global_channel_id': self.instance_id and self.instance_id.seller_id and self.instance_id.seller_id.global_channel_id and self.instance_id.seller_id.global_channel_id.id or False
        }

    @api.multi
    def removal_order_procurements(self):
        proc_group_obj = self.env['procurement.group']
        picking_obj = self.env['stock.picking']
        pull_obj = self.env['stock.rule']
        sell_proc_group = proc_group_obj.create({'removal_order_id': self.id})
        unsell_proc_group = proc_group_obj.create({'removal_order_id': self.id})
        config = self.env['removal.order.config.ept'].search(
            [('id', 'in', self.instance_id.removal_order_config_ids.ids),
             ('removal_disposition', '=', self.removal_disposition)])

        if len(config.unsellable_route_id.rule_ids.ids) > 1:
            rule = pull_obj.search([('route_id', '=', config.unsellable_route_id.id),
                                    ('location_src_id', '!=', self.disposition_location_id.id)], limit=1)
        else:
            rule = config.unsellable_route_id.pull_ids[1]

        qty = 0.0
        for removal_line in self.removal_order_lines_ids:
            amazon_product = removal_line.amazon_product_id
            sellable_quantity = 0.0 if removal_line.sellable_quantity < 0.0 else removal_line.sellable_quantity
            unsellable_quantity = 0.0 if removal_line.unsellable_quantity < 0.0 else removal_line.unsellable_quantity
            datas = {'company_id': self.instance_id.company_id.id,
                     'warehouse_id': self.warehouse_id,
                     'priority': '1'
                     }

            if unsellable_quantity > 0.0:
                datas.update({
                    'group_id': unsell_proc_group,
                    'route_ids': config.unsellable_route_id,  # [(6,0,config.unsellable_route_id.ids)]
                })
                qty = removal_line.unsellable_quantity
                proc_group_obj.run(amazon_product.product_id, qty, amazon_product.uom_id, rule.location_id,
                                   amazon_product.name, self.name, datas)

            if sellable_quantity > 0.0:
                datas.update({
                    'group_id': sell_proc_group,
                    'route_ids': config.sellable_route_id,  # [(6,0,config.sellable_route_id.ids)]
                })
                qty = removal_line.sellable_quantity
                proc_group_obj.run(amazon_product.product_id, qty, amazon_product.uom_id,
                                   self.warehouse_id.lot_stock_id, amazon_product.name, self.name, datas)

        pickings = picking_obj.search([('group_id', 'in', [sell_proc_group.id, unsell_proc_group.id]),
                                       ('state', 'in', ['confirmed', 'partially_available', 'assigned'])])
        pickings.write({'is_fba_wh_picking': True, 'removal_order_id': self.id})
        pickings = picking_obj.search(
            [('group_id', 'in', [sell_proc_group.id, unsell_proc_group.id]), ('state', 'in', ['waiting'])])
        pickings.write({'is_fba_wh_picking': False, 'removal_order_id': self.id})
        pickings = picking_obj.search([('group_id', 'in', [sell_proc_group.id, unsell_proc_group.id])])
        return pickings

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            try:
                sequence = self.env.ref('amazon_ept.seq_removal_order_plan')
                if sequence:
                    name = sequence.next_by_id()
                else:
                    name = '/'
            except:
                name = '/'
            vals.update({'name': name})
        return super(removal_order, self).create(vals)


class removal_order_lines(models.Model):
    _name = "removal.orders.lines.ept"
    _description = "removal.orders.lines.ept"

    @api.multi
    def get_stock(self):
        for line in self:
            line.sellable_stock = line.amazon_product_id.product_id.with_context(
                {'location': line.removal_order_id.instance_id.warehouse_id.lot_stock_id.id}).qty_available
            line.unsellable_stock = line.amazon_product_id.product_id.with_context({
                                                                                       'location': line.removal_order_id.instance_id.fba_warehouse_id.unsellable_location_id.id}).qty_available

    @api.multi
    def product_id_change(self, removal_disposition):
        vals = {'removal_disposition': removal_disposition}
        if removal_disposition == 'Disposal':
            vals.update({'sellable_quantity': 0.0})
        return {'value': vals}

    amazon_product_id = fields.Many2one('amazon.product.ept', string='Product', domain=[('fulfillment_by', '=', 'AFN')])
    seller_sku = fields.Char(size=120, string='Seller SKU', related="amazon_product_id.seller_sku", readonly=True)
    sellable_quantity = fields.Float("Sellable Quantity", digits=dp.get_precision("Product UoS"))
    unsellable_quantity = fields.Float("Unsellable Quantity", digits=dp.get_precision("Product UoS"))
    sellable_stock = fields.Float("Sellable Stock", digits=dp.get_precision("Product UoS"), compute="get_stock",
                                  multi="get_multi_stock", readonly=True)
    unsellable_stock = fields.Float("Unsellable Stock", digits=dp.get_precision("Product UoS"), compute="get_stock",
                                    multi="get_multi_stock", readonly=True)
    removal_order_id = fields.Many2one("amazon.removal.order.ept", string="Removal Order")
    removal_disposition = fields.Selection([('Return', 'Return'), ('Disposal', 'Disposal')])
