from datetime import datetime
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class InOutRegister(models.Model):
    _name = "product.in.out.register"
    _description = "Product InOut Register"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

    @api.model
    def _default_out_picking_type(self):
        return self._get_out_picking_type(self.env.context.get('company_id') or self.env.company.id)

    @api.model
    def _get_service_engineer_domain(self):
        res = self.env['res.users'].search([])
        lis = []
        for re in res:
            if re.has_group('ki_contract_menu.group_smart_printer_service_engineer'):
                lis.append(re.id)
        return [('id', 'in', lis)]

    picking_type_id = fields.Many2one(
        'stock.picking.type',
        required=True,
        default=_default_picking_type
    )
    out_picking_type_id = fields.Many2one(
        'stock.picking.type',
        required=True,
        default=_default_out_picking_type
    )
    date = fields.Date(
        required=True,
        string='Date',
        default=lambda self: fields.Date.today()
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        string='Company',
        default=lambda self: self.env.company.id
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_process', 'In Process'),
            ('done', 'Done'),
        ],
        default='draft',
        string='Status',
    )
    line_ids = fields.One2many(
        'product.in.out.register.lines',
        'register_id',
        string='Product Register Line',
    )
    quantity_income = fields.Integer(
        string='Incoming Quantity',
        compute='_quantity_all'
    )
    quantity_outcome = fields.Integer(
        string='Outgoing Quantity',
        compute='_quantity_all'
    )
    name = fields.Char(
        required=False
    )
    picking_ids = fields.Many2many(
        'stock.picking',
        string='Picking'
    )
    transfer_count = fields.Integer(
        string='Transfer Count',
        compute='_compute_transfer_count'
    )
    assign_user = fields.Many2one(
        'res.users',
        string='Assigned User',
        store=True,
        domain=_get_service_engineer_domain
    )

    @api.model
    def create(self, vals):
        res = super(InOutRegister, self).create(vals)
        sequence = self.env['ir.sequence'].next_by_code('product.in.out.register', sequence_date=res.date)
        res.update({'name': sequence})
        return res

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_("Delete is possible only in draft state"))
        else:
            result = super(InOutRegister, self).unlink()
            return result

    @api.depends('line_ids.operation_type')
    def _quantity_all(self):
        for quantity in self:
            quantity_income = quantity_outcome = 0.0
            for line in quantity.line_ids:
                if line.operation_type == 'in':
                    quantity_income = quantity_income + line.quantity
                elif line.operation_type == 'out':
                    quantity_outcome = quantity_outcome + line.quantity
            quantity.update({
                'quantity_income': quantity_income,
                'quantity_outcome': quantity_outcome,
            })

    def action_confirm(self):
        for rec in self:
            rec.state = 'in_process'

    def action_done(self):
        for rec in self:
            self._create_picking()
            rec.state = 'done'
        act = self.env.ref('stock.action_picking_tree_all').read([])[0]
        act['domain'] = [('id', 'in', self.picking_ids.ids)]
        return act

    def action_cancel(self):
        for rec in self:
            rec.state = 'draft'

    def action_open_all_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', 'in', self.picking_ids.ids)]
        return action

    @api.depends('picking_ids')
    def _compute_transfer_count(self):
        for transfer in self:
            transfer.transfer_count = len(transfer.picking_ids)

    def _prepare_picking(self, partner_id, type=None):
        if not partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", partner_id.name))
        if type == 'in':
            return {
                'picking_type_id': self.picking_type_id.id,
                'partner_id': partner_id.id,
                'user_id': False,
                'date': self.date,
                'origin': self.name,
                'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                'location_id': partner_id.property_stock_supplier.id,
                'company_id': self.company_id.id,
            }
        elif type == 'out':
            return {
                'picking_type_id': self.out_picking_type_id.id,
                'partner_id': partner_id.id,
                'user_id': False,
                'date': self.date,
                'origin': self.name,
                'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                'location_id': partner_id.property_stock_supplier.id,
                'company_id': self.company_id.id,
            }

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any(product.type in ['product', 'consu'] for product in order.line_ids.product_id):
                order = order.with_company(order.company_id)
                partner_val = {}
                partner_val['in'] = {}
                partner_val['out'] = {}
                for r in self.line_ids:
                    if r.operation_type == 'in':

                        if r.partner_id not in partner_val.get('in'):
                            partner_val['in'][r.partner_id] = {
                                'in_lines': []
                            }
                        partner_val['in'][r.partner_id]['in_lines'].append(r)
                    elif r.operation_type == 'out':
                        if r.partner_id not in partner_val.get('out'):
                            partner_val['out'][r.partner_id] = {
                                'out_lines': []
                            }
                        partner_val['out'][r.partner_id]['out_lines'].append(r)
                for type in partner_val:
                    if type == 'in':
                        for partner in partner_val[type]:
                            picking = order._prepare_picking(partner, type='in')
                            picking_create = StockPicking.with_user(SUPERUSER_ID).create(picking)
                            order.picking_ids = [(4, picking_create.id)]
                            for line in partner_val['in'][partner]['in_lines']:
                                moves = line._create_stock_moves(picking_create)
                                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    elif type == 'out':
                        for partner in partner_val[type]:
                            picking = order._prepare_picking(partner, type='out')
                            picking_create = StockPicking.with_user(SUPERUSER_ID).create(picking)
                            order.picking_ids = [(4, picking_create.id)]
                            for line in partner_val['out'][partner]['out_lines']:
                                moves = line._create_stock_moves(picking_create)
                                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking_create.message_post_with_view('mail.message_origin_link',
                                                      values={'self': picking_create, 'origin': order},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
                # picking_create.action_set_quantities_to_reservation()
                # picking_create.button_validate()
                for rec in self.picking_ids:
                    rec.action_set_quantities_to_reservation()
                    rec.button_validate()
        return True

    @api.model
    def _get_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    @api.model
    def _get_out_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        return picking_type[:1]


class ProductRegisterLines(models.Model):
    _name = "product.in.out.register.lines"
    _description = "Product InOut Line"

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    name = fields.Text(
        string='Description',
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1,
    )
    comment = fields.Text(
        string='Comment',
    )
    operation_type = fields.Selection(
        [
            ('in', 'In'),
            ('out', 'Out'),
        ],
        required=True,
        string='Operation Type',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    register_id = fields.Many2one(
        'product.in.out.register',
    )
    date = fields.Date(
        string='Date',
        related='register_id.date',
        store=True
    )
    reference = fields.Char(
        string='name',
        related='register_id.name',
        store=True
    )
    ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Ticket',
    )
    state = fields.Selection(
        [
            ('with_user', 'With User'),
            ('with_customer', 'With Customer'),
            ('with_office', 'With Office')
        ],
        string='State',
    )
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        else:
            self.name = self.product_id.name
            self.uom_id = self.product_id.uom_id.id

    # @api.onchange('ticket_id')
    # def _onchange_sales_team_id(self):
    #     lead_ids = self.env['crm.lead'].sudo().search(
    #         [('team_id', '=', self.sales_team_id.id)])
    #     return {'domain': {'lead_id': [('id', 'in', lead_ids.ids)]}}

    def _prepare_stock_moves(self, picking_create):
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = self.quantity
        res.append(self._prepare_stock_move_vals(picking_create, qty))
        return res

    def _create_stock_moves(self, picking_create):
        values = []
        for line in self:
            for val in line._prepare_stock_moves(picking_create):
                values.append(val)
        return self.env['stock.move'].create(values)

    def _prepare_stock_move_vals(self, picking_create, qty):
        self.ensure_one()
        return {
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': self.register_id.date,
            # 'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
            'location_id': self.partner_id.property_stock_supplier.id,
            'location_dest_id': self.register_id.picking_type_id.default_location_dest_id.id,
            'picking_id': picking_create.id,
            'partner_id': self.partner_id.id,
            # 'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            # 'purchase_line_id': self.id,
            'company_id': self.register_id.company_id.id,
            # 'price_unit': price_unit,
            'picking_type_id': self.register_id.picking_type_id.id,
            # 'group_id': self.order_id.group_id.id,
            'origin': self.register_id.name,
            # 'description_picking': description_picking,
            # 'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.register_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': qty,
            'product_uom': self.uom_id.id,
        }
