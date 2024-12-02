from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ready_to_pack = fields.Boolean(string="READY TO PACK")
    products_availability = fields.Char(store=True, compute_sudo=False)

    show_mark_as_in = fields.Boolean(compute='_compute_show_mark_as_in')
    show_validate_in = fields.Boolean(compute='_compute_show_validate_in')
    show_check_availability_in = fields.Boolean(compute='_compute_show_check_availability_in')

    @api.depends('immediate_transfer', 'state')
    def _compute_show_check_availability_in(self):
        """ According to `picking.show_check_availability`, the "check availability" button will be
        displayed in the form view of a picking.
        """
        for picking in self:
            picking.show_check_availability_in = False
            if picking.picking_type_code != 'outgoing':     #ADD NEW LINE
                if picking.immediate_transfer or picking.state not in ('confirmed', 'waiting', 'assigned'):
                    picking.show_check_availability_in = False
                    continue
                picking.show_check_availability_in = any(
                    move.state in ('waiting', 'confirmed', 'partially_available')
                )

    @api.depends('immediate_transfer', 'state')
    def _compute_show_check_availability(self):
        """ According to `picking.show_check_availability`, the "check availability" button will be
        displayed in the form view of a picking.
        """
        for picking in self:
            picking.show_check_availability = False
            if picking.picking_type_code == 'outgoing':  #ADD NEW LINE
                if picking.immediate_transfer or picking.state not in ('confirmed', 'waiting', 'assigned'):
                    picking.show_check_availability = False
                else:
                    picking.show_check_availability = True


    # This Method Will be use Button Invisible
    @api.depends('state')
    def _compute_show_validate_in(self):
        for picking in self:
            picking.show_validate_in = False
            if picking.picking_type_code != 'outgoing':
                if not (picking.immediate_transfer) and picking.state == 'draft':
                    picking.show_validate_in = False
                elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned'):
                    picking.show_validate_in = False
                else:
                    picking.show_validate_in = True

    # This Method Will be use Button Invisible
    @api.depends('state')
    def _compute_show_mark_as_in(self):
        for picking in self:
            picking.show_mark_as_in = False
            if picking.picking_type_code != 'outgoing':
                if not picking.package_level_ids:
                    picking.show_mark_as_in = False
                elif not picking.immediate_transfer and picking.state == 'draft':
                    picking.show_mark_as_in = True
                elif picking.state != 'draft' or not picking.id:
                    picking.show_mark_as_in = False
                else:
                    picking.show_mark_as_in = True

    # This Method Will be use Button Invisible
    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            picking.show_validate = False
            if picking.picking_type_code == 'outgoing':
                if not (picking.immediate_transfer) and picking.state == 'draft':
                    picking.show_validate = False
                elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned'):
                    picking.show_validate = False
                else:
                    picking.show_validate = True

    # This Method Will be use Button Invisible
    @api.depends('state')
    def _compute_show_mark_as_todo(self):
        for picking in self:
            picking.show_mark_as_todo = False
            if picking.picking_type_code == 'outgoing':
                if not picking.package_level_ids:
                    picking.show_mark_as_todo = False
                elif not picking.immediate_transfer and picking.state == 'draft':
                    picking.show_mark_as_todo = True
                elif picking.state != 'draft' or not picking.id:
                    picking.show_mark_as_todo = False
                else:
                    picking.show_mark_as_todo = True

    def _default_move_type(self):
        settings_partner = self.env['ir.config_parameter'].sudo().get_param('mt_order_delivery_manual.move_type')
        self.move_type = str(settings_partner)
        return settings_partner

    move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')], 'Shipping Policy',
        default=_default_move_type, required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="It specifies goods to be deliver partially or all at once")

    def action_ready_to_pack(self):
        self.ready_to_pack = True

    def ready_to_ship(self):
        for res in self:
            if res.picking_type_code == 'outgoing':
                res.action_ready_to_pack()
                for rec in res.move_ids_without_package:
                    if not rec.quantity_done:
                        raise UserError(_('Shipment missing some products tobe packed!'))
                self.write({'state': 'assigned'})

    # def action_confirm(self):
    #     # print("picking_type_code+__________________________________________", self.picking_type_code)
    #     # ADD NEW LINE
    #     if not self.picking_type_code == 'outgoing':
    #         # print("UNDERRRRRRRRRRRRRRRRRRRRRRRRRRRr")
    #         return super(StockPicking, self).action_confirm()
    #     #
    #     self._check_company()
    #     self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
    #     self.write({'state': 'confirmed'})
    #     return True

    def action_draft_to_waiting(self):
        for rec in self:
            if rec.state == 'draft':
                rec.action_confirm()
            else:
                raise UserError(_('Select records not draft!'))

    def action_waiting_to_ready(self):
        for rec in self:
            rec.move_ids_without_package.pick_qty()
            if rec.state == 'confirmed':
                rec.ready_to_ship()
            else:
                raise UserError(_('Select records not Waiting!'))

    def action_ready_to_done(self):
        for rec in self:
            if rec.state == 'assigned':
                rec.button_validate()
            else:
                raise UserError(_('Select records not ready!'))

    def action_confirm_new(self):
        return self.action_confirm()

    def button_validate_new(self):
        return self.button_validate()

    def action_assign_new(self):
        return self.action_assign()



class StockMove(models.Model):
    _inherit = "stock.move"

    qty_on_hand = fields.Float(string="On Hand", compute='_compute_qty_on_hand', store=True)

    def pick_qty(self):
        for rec in self:
            if rec.qty_on_hand < rec.product_uom_qty:
                raise UserError(_('Not enough Stock to fulfill demand!'))
            else:
                rec.quantity_done = rec.product_uom_qty

    @api.depends('picking_id.location_id', 'product_id')
    def _compute_qty_on_hand(self):
        for rec in self:
            quant_obj = self.env['stock.quant']
            if rec.product_id and rec.picking_id.location_id:
                qty_available = quant_obj._get_available_quantity(rec.product_id, rec.picking_id.location_id)
                rec.qty_on_hand = qty_available
