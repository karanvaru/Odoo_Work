from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class amazon_inbound_shipment_wizard(models.TransientModel):
    _name = "amazon.inbound.shipment.wizard"
    _description = "Amazon Inbound Shipment Wizard"
    update_shipment_status = fields.Selection([('WORKING', 'WORKING'), ('CANCELLED', 'CANCELLED')],
                                              string="Shipment Status", default='WORKING')
    choose_inbound_shipment_file = fields.Binary(string="Choose File", filters="*.csv",
                                                 help="Select amazon inbound shipment file.")
    file_name = fields.Char("Filename", help="File Name")

    @api.multi
    def update_inbound_shipment(self):
        plan_line_obj = self.env['inbound.shipment.plan.line']
        active_id = self._context.get('active_id')
        stock_picking_obj = self.env['stock.picking']
        active_model = self._context.get('active_model', '')
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        if active_model != 'stock.picking':
            raise Warning(
                'You cannot update Shipment, because there is no any related Amazon shipment'
                'with this record.')
        picking = stock_picking_obj.browse(active_id)

        odoo_shipment = picking.odoo_shipment_id
        ship_plan = picking.ship_plan_id
        instance = ship_plan.instance_id
        address = picking.partner_id or ship_plan.ship_from_address_id
        name, add1, add2, city, postcode = address.name, address.street or '', address.street2 or '', address.city or '', address.zip or ''
        country = address.country_id and address.country_id.code or ''
        state = address.state_id and address.state_id.code or ''
        shipment_status = self.update_shipment_status or 'WORKING'
        amazon_product_obj = self.env['amazon.product.ept']
        if not odoo_shipment.shipment_id or not odoo_shipment.fulfill_center_id:
            raise Warning('You must have to first create Inbound Shipment Plan.')

        for x in range(0, len(picking.move_lines), 20):
            move_lines = picking.move_lines[x:x + 20]
            sku_qty_dict = {}
            for move in move_lines:
                amazon_product = amazon_product_obj.search(
                    [('product_id', '=', move.product_id.id), ('instance_id', '=', instance.id),
                     ('fulfillment_by', '=', 'AFN')])
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

        picking.write(
            {'inbound_ship_updated': True, 'shipment_status': self.update_shipment_status})

        if self.update_shipment_status == 'CANCELLED':
            picking.action_cancel()
            odoo_shipment.write({'state': 'CANCELLED'})
        return True

    @api.multi
    def import_inbound_shipment_report(self):
        return True
