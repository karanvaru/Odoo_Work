from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import qrcode
import base64
from io import BytesIO


class CartridgePartsAdd(models.Model):
    _name = 'cartridge.part.line'
    _description = "Cartridge Part Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # @api.model
    # def _default_picking_type(self):
    #     return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

    product_template_id = fields.Many2one(
        'product.template',
        string='Parts'
    )
    product_part_id = fields.Many2one(
        'product.product',
        string='Parts'
    )
    name = fields.Char(
        string='Description',
        required=True,
        # related='product_part_id.display_name'
    )
    note = fields.Text(
        string='Comment'
    )
    product_qty = fields.Float(
        string='Quantity',
        default=0
    )
    # picking_type_id = fields.Many2one(
    #     'stock.picking.type',
    #     'Deliver To',
    #
    # )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    user_id = fields.Many2one(
        'res.users',
        required=True,
        string="User",
        default=lambda self: self.env.user,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
        ], string='State',
        tracking=1,
        default="draft"
    )
    # picking_id = fields.Many2one(
    #     'stock.picking'
    # )
    date = fields.Date(
        string='Date',
    )

    @api.onchange('product_part_id')
    def name_onchange(self):
        if self.product_part_id:
            self.name = self.product_part_id.name

    # @api.model
    # def _get_picking_type(self, company_id):
    #     picking_type = self.env['stock.picking.type'].search(
    #         [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)])
    #     if not picking_type:
    #         picking_type = self.env['stock.picking.type'].search(
    #             [('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
    #     return picking_type[:1]
    #
    # def _prepare_picking(self):
    #     # if self.partner_id:
    #     #     if not self.partner_id.property_stock_supplier.id:
    #     #         raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
    #     # elif self.laboratory_id:
    #     #     if not self.laboratory_id.property_stock_supplier.id:
    #     #         raise UserError(_("You must set a Vendor Location for this partner %s", self.laboratory_id.name))
    #     vals = {
    #         'picking_type_id': self.picking_type_id.id,
    #         'partner_id': self.user_id.partner_id.id,
    #         'user_id': False,
    #         'date': self.date,
    #         'origin': self.product_id.name,
    #         'location_dest_id': self.user_id.partner_id.property_stock_customer.id,
    #         'location_id': self.picking_type_id.default_location_src_id.id,
    #         'company_id': self.company_id.id,
    #     }
    #     # print('aaaaaaaaaaaaaaaaaaaaaaa', vals)
    #     return vals
    #
    # def _create_picking(self):
    #     StockPicking = self.env['stock.picking']
    #     for order in self:
    #         if any(product.type in ['product', 'consu'] for product in order.product_part_id):
    #             order = order.with_company(order.company_id)
    #             res = order._prepare_picking()
    #             picking = StockPicking.sudo().create(res)
    #             order.picking_id = picking.id
    #             # order.picking_ids = [(4, picking.id)]
    #             moves = order._create_stock_moves(picking)
    #             # moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
    #             seq = 0
    #             for move in sorted(moves, key=lambda move: move.date):
    #                 seq += 5
    #                 move.sequence = seq
    #             moves._action_assign()
    #             picking.message_post_with_view('mail.message_origin_link',
    #                                            values={'self': picking, 'origin': order},
    #                                            subtype_id=self.env.ref('mail.mt_note').id)
    #
    #             picking.action_set_quantities_to_reservation()
    #             picking.button_validate()
    #
    #     return True
    #
    # def _prepare_stock_move_vals(self, picking, product_uom_qty, product_uom):
    #     self.ensure_one()
    #     # product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
    #     # date_planned = self.date_planned or self.order_id.date_planned
    #     return {
    #         'name': self.name,
    #         'product_id': self.product_part_id.id,
    #         'date': self.date,
    #         'location_id': self.picking_type_id.default_location_src_id.id,
    #         'location_dest_id': self.user_id.partner_id.property_stock_customer.id,
    #         'picking_id': picking.id,
    #         'partner_id': self.user_id.partner_id.id,
    #         'state': 'draft',
    #         'company_id': self.company_id.id,
    #         # 'price_unit': price_unit,
    #         'picking_type_id': self.picking_type_id.id,
    #         'origin': self.product_id.name,
    #         'warehouse_id': self.picking_type_id.warehouse_id.id,
    #         "product_uom_qty": self.product_qty,
    #         "product_uom": self.product_part_id.uom_id.id,
    #         # 'product_packaging_id': self.product_packaging_id.id,
    #     }
    #
    # def _prepare_stock_moves(self, picking):
    #     """ Prepare the stock moves data for one order line. This function returns a list of
    #     dictionary ready to be used in stock.move's create()
    #     """
    #     self.ensure_one()
    #     res = []
    #     if self.product_part_id.type not in ['product', 'consu']:
    #         return res
    #     qty = self.product_qty
    #     product_uom_qty, product_uom = self.product_part_id.uom_id._adjust_uom_quantities(qty,
    #                                                                                       self.product_part_id.uom_id)
    #     res.append(self._prepare_stock_move_vals(picking, product_uom_qty, product_uom))
    #     return res
    #
    # def _create_stock_moves(self, picking):
    #     values = []
    #     for line in self:
    #         for val in line._prepare_stock_moves(picking):
    #             values.append(val)
    #     return self.env['stock.move'].create(values)
    #
    # def action_validate_stock(self):
    #     for rec in self:
    #         rec._create_picking()
    #         # rec.product_id = picking.id
    #         rec.state = 'submit'
    #         act = rec.env.ref('stock.action_picking_tree_ready').sudo().read([])[0]
    #         act['domain'] = [('id', '=', rec.picking_id.id)]
    #         return act
    #
