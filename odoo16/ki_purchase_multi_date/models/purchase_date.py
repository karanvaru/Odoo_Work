from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class Multidatepicking(models.Model):
    _inherit = "purchase.order"

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                line_dict = {}
                for line in self.order_line.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                    if line.date_planned not in line_dict:
                        line_dict[line.date_planned] = line
                    else:
                        line_dict[line.date_planned] += line
                for line.date_planned in line_dict:
                    res = order._prepare_picking_custome(line.company_id.id)
                    picking = StockPicking.sudo().create(res)
                    moves = line_dict[line.date_planned].with_context({'date': line.date_planned})._create_stock_moves(
                        picking)
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0

                    for move in sorted(moves, key=lambda move: move.date):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
        return True

    @api.model
    def _get_picking_type_custom(self, company_id):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    def _prepare_picking_custome(self, date):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
        picking_type_id = self._get_picking_type_custom(date)
        return {
            'picking_type_id': picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,

        }


class Multidate(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        self._check_orderpoint_picking_type()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        description_picking = product._get_description(self.order_id.picking_type_id)
        if self.product_description_variants:
            description_picking += "\n" + self.product_description_variants
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': picking.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': picking.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'sequence': self.sequence,
        }
