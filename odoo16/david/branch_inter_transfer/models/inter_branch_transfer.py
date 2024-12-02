from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError


class InterBranchTransfer(models.Model):
    _name = "inter.branch.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Name',
        copy=False,
        default="New"
    )

    user_id = fields.Many2one(
        'res.users',
        string="User",
        default=lambda self: self.env.user,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        string="Company",
        tracking=True,
    )
    date = fields.Date(
        "Date",
        default=fields.Date.today(),
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('transfer', 'Transfer'),
        ('cancel', 'Cancel'),
    ],
        default='draft',
        tracking=True,
    )

    source_branch_id = fields.Many2one(
        "res.branch",
        string="Source Branch",
        required=True,
        tracking=True,
    )
    destination_branch_id = fields.Many2one(
        "res.branch",
        string="Destination Branch",
        required=True,
        tracking=True,
    )

    source_location_id = fields.Many2one(
        "stock.location",
        string="Source Location",
        required=True,
        tracking=True,
        domain="[('branch_id', '!=', False), ('branch_id', '=', source_branch_id)]"
    )

    destination_location_id = fields.Many2one(
        "stock.location",
        string="Destination Location",
        required=True,
        tracking=True,
        domain="[('branch_id', '!=', False), ('branch_id', '=', destination_branch_id)]"

    )

    inter_branch_transfer_line_ids = fields.One2many(
        'inter.branch.transfer.line',
        'inter_branch_transfer_id',
        string="Lines"
    )
    stock_move_count = fields.Integer(
        string='Count',
        compute='_compute_stock_move'
    )

    def action_submit(self):
        name = self.env['ir.sequence'].next_by_code('branch.reference.code')
        self.update({
            'state': 'submit',
            'name': name
        })

    def action_cancel(self):
        self.update({
            'state': 'cancel'
        })

    def action_reset_draft(self):
        self.update({
            'state': 'draft'
        })

    @api.constrains('source_branch_id', 'destination_branch_id')
    def _check_transfer_branch_id(self):
        if self.source_branch_id == self.destination_branch_id:
            raise ValidationError(
                _("Source Branch And Destination Branch Must Be Unique.")
            )

    @api.constrains('source_location_id', 'destination_location_id')
    def _check_transfer_location_id(self):
        if self.source_location_id == self.destination_location_id:
            raise ValidationError(
                _("Source Location And Destination Location Must Be Unique.")
            )

    @api.onchange('source_branch_id', 'destination_branch_id')
    def onchange_branch_id(self):
        location = self.env['stock.location']
        if self.source_branch_id:
            source_location = location.search(
                [('usage', '=', 'internal'), ('branch_id', '=', self.source_branch_id.id)],
                limit=1)
            self.source_location_id = source_location.id
        if self.destination_branch_id:
            destination_location = location.search(
                [('usage', '=', 'internal'), ('branch_id', '=', self.destination_branch_id.id)],
                limit=1)
            self.destination_location_id = destination_location.id

    def action_show_stock_move(self):
        moves = self.env['stock.move'].sudo().search([('inter_branch_transfer_id', '=', self.id)])
        return {
            'name': _('Task'),
            'res_model': 'stock.move',
            'view_mode': 'list,form',
            'domain': [('id', '=', moves.ids)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    def _compute_stock_move(self):
        for transfer in self:
            moves = self.env['stock.move'].sudo().search([('inter_branch_transfer_id', '=', self.id)])
            transfer.stock_move_count = len(moves.ids)

    def action_transfer(self):
        for rec in self.inter_branch_transfer_line_ids:
            moves = self._prepare_stock_move_vals(rec)
            move_id = self.env['stock.move'].create(moves)
            move_id._action_confirm()
            move_id._action_assign()
            move_id.move_line_ids.write({'qty_done': rec.qty})
            move_id._action_done()
            move_id.inter_branch_transfer_id = self.id
            self.update({
                'state': 'transfer'
            })

    def _prepare_stock_move_vals(self, lines):
        picking_type_id = self._get_picking_type(self.company_id)
        move_dict = {
            'state': 'draft',
            'picking_type_id': picking_type_id.id,
            'product_id': lines.product_id.id,
            'name': lines.product_id.display_name,
            'product_uom_qty': lines.qty,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.destination_location_id.id,
        }
        return move_dict

    @api.model
    def _get_picking_type(self, company_id):
        picking_type_object = self.env['stock.picking.type']
        picking_type_object = picking_type_object.search(
            [('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id.id)])
        if not picking_type_object:
            picking_type_object = picking_type_object.search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
        return picking_type_object[:1]

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft"):
            raise UserError(_("Only requests on draft state can be unlinked"))
        return super(InterBranchTransfer, self).unlink()


class InterBranchTransferLine(models.Model):
    _name = "inter.branch.transfer.line"

    product_id = fields.Many2one(
        'product.product',
        string="Product",
    )

    price_unit = fields.Float(
        string='Unit Price',
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='UOM',
    )
    inter_branch_transfer_id = fields.Many2one(
        'inter.branch.transfer',
    )

    @api.onchange('product_id')
    def onchnage_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.price_unit = self.product_id.list_price
