from datetime import datetime
import logging
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class RefillRequest(models.Model):
    _name = "refill.request"
    _description = "Refill Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

    product_id = fields.Many2one(
        'product.product',
        required=True,
        string='Product'
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
    )
    date = fields.Date(
        required=True,
        string='Date',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ],
        default='draft',
        string='Status',
    )
    ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Ticket',
    )
    product_register_id = fields.Many2one(
        'product.in.out.register',
        string='In/Out Register'
    )
    name = fields.Char(
        required=False
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        string='Company',
        default=lambda self: self.env.company.id
    )
    refill_ids = fields.One2many(
        'refill.request.line',
        'refill_part_id',
    )
    picking_id = fields.Many2one(
        'stock.picking'
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        'Deliver To',
        default=_default_picking_type
    )
    note = fields.Text(
        string='Comment'
    )

    @api.onchange('product_id')
    def product_part_id_onchange(self):
        self.refill_ids = [(5, 0, 0)]
        for i in self.product_id.part_product_line_ids:
            vals = {
                'product_part_id': i.product_part_id.id,
                'quantity': i.product_qty,
                'refill_part_id': self.id,
            }
            self.env['refill.request.line'].create(vals)

    @api.model
    def create(self, vals):
        res = super(RefillRequest, self).create(vals)
        sequence = self.env['ir.sequence'].next_by_code('refill.request', sequence_date=res.date)
        res.update({'name': sequence})

        return res

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_("Delete is possible only in draft state"))
        else:
            result = super(RefillRequest, self).unlink()
            return result

    def action_confirm(self):
        for rec in self:
            date_1 = fields.Date.today()
            product = self.env['refill.request'].search(
                [('product_id', '=', rec.product_id.id), ('date', '=', date_1), ('state', '=', 'done')])
            if product:
                raise ValidationError(_("Refill Request has already Created for %s Cartridge", product.product_id.name))
            for i in rec.refill_ids:
                _logger.info("quantity; %s Part quantity; %s,%s", i.quantity, i.product_part_id.qty_available,
                             i.product_part_id.name)
                if i.quantity > 0 and i.product_part_id.qty_available <= 0:
                    raise UserError(_("Quantity not available for %s", i.product_part_id.name))

            rec._create_picking()
            rec.state = 'done'
            if self.product_id:
                self.product_id.is_active = True
                if self.product_id.is_active == True:
                    self.product_id.product_status = 'active'
        display_msg = "Refill Request Confirmed"
        self.message_post(body=display_msg)

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    # def action_validate_product(self):
    #     for rec in self:

    @api.model
    def _get_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    def _prepare_picking(self):
        # if self.partner_id:
        #     if not self.partner_id.property_stock_supplier.id:
        #         raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
        # elif self.laboratory_id:
        #     if not self.laboratory_id.property_stock_supplier.id:
        #         raise UserError(_("You must set a Vendor Location for this partner %s", self.laboratory_id.name))
        vals = {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.user_id.partner_id.id,
            'user_id': False,
            'date': self.date,
            'origin': self.name,
            'location_dest_id': self.user_id.partner_id.property_stock_customer.id,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'company_id': self.company_id.id,
        }
        return vals

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any(product.type in ['product', 'consu'] for product in order.product_id):
                order = order.with_company(order.company_id)
                res = order._prepare_picking()
                picking = StockPicking.sudo().create(res)
                order.picking_id = picking.id
                # order.picking_ids = [(4, picking.id)]
                moves = order.refill_ids._create_stock_moves(picking)
                # moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                                               values={'self': picking, 'origin': order},
                                               subtype_id=self.env.ref('mail.mt_note').id)

                picking.action_set_quantities_to_reservation()
                picking.button_validate()

        return True


class Refillrequestline(models.Model):
    _name = "refill.request.line"
    _description = "Refill Request Line"

    product_part_id = fields.Many2one(
        'product.product',
        string="Part"
    )
    refill_part_id = fields.Many2one(
        'refill.request',
        string="Refill request"
    )
    quantity = fields.Integer(
        string='Quantity',
        default=0
    )
    comments = fields.Text(
        string='Comments'
    )
    line_date = fields.Date(
        string='Date',
        related='refill_part_id.date',
        store=True
    )
    parts_cartridge_id = fields.Many2one(
        'product.product',
        related='refill_part_id.product_id',
        store=True
    )


    # return {'domain': {'refill_part_id': [('product_id.part_product_line_ids.product_part_id', 'in', self.product_part_id.id)]}}

    def _prepare_stock_move_vals(self, picking, product_uom_qty, product_uom):
        self.ensure_one()
        # product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        # date_planned = self.date_planned or self.order_id.date_planned
        return {
            'name': self.product_part_id.name,
            'product_id': self.product_part_id.id,
            'date': self.refill_part_id.date,
            'location_id': self.refill_part_id.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.refill_part_id.user_id.partner_id.property_stock_customer.id,
            'picking_id': picking.id,
            'partner_id': self.refill_part_id.user_id.partner_id.id,
            'state': 'draft',
            'company_id': self.refill_part_id.company_id.id,
            # 'price_unit': price_unit,
            'picking_type_id': self.refill_part_id.picking_type_id.id,
            'origin': self.refill_part_id.product_id.display_name,
            'warehouse_id': self.refill_part_id.picking_type_id.warehouse_id.id,
            "product_uom_qty": self.quantity,
            "product_uom": self.product_part_id.uom_id.id,
            # 'product_packaging_id': self.product_packaging_id.id,
        }

    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_part_id.type not in ['product', 'consu']:
            return res
        qty = self.quantity
        product_uom_qty, product_uom = self.product_part_id.uom_id._adjust_uom_quantities(qty,
                                                                                          self.product_part_id.uom_id)
        res.append(self._prepare_stock_move_vals(picking, product_uom_qty, product_uom))
        return res

    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)
