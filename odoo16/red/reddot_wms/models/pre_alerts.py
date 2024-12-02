from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class WizardPlanShipment(models.TransientModel):
    _name = "wizard.pre.alert"
    _description = "Plan shipment"

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Transfers to plan", domain=[('carrier_tracking_ref', '=', False)])

    move_line_ids = fields.Many2many(
        comodel_name="stock.move.line",
        string="Detailed Operations")
    move_ids = fields.Many2many(comodel_name="stock.move",
                                string="Moves to plan",
                                compute='_compute_move_ids', store=True)
    warning = fields.Char(readonly=True)
    shipper_id = fields.Many2one('res.partner', 'Shipper', required=True,
                                 help="Shipper's Details")
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], "Transport",
                                      help='Type of transportation',
                                      required=True)
    loading_port_id = fields.Many2one('freight.port', string="Loading Port",
                                      required=True,
                                      help="Loading port of the freight order")
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port",
                                          required=True,
                                          help="Discharging port of freight order")
    agent_id = fields.Many2one('res.partner', 'Agent', required=True,
                               help="Details of agent")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    type = fields.Selection([('import', 'Import'), ('export', 'Export')],
                            'Import/Export', required=True,
                            help="Type of freight operation")
    delivery_method = fields.Many2one('account.incoterms', string='Delivery Method', help="The shipment’s delivery "
                                                                                          "method such as DDU, FOB, "
                                                                                          "ExWorks as defined in the "
                                                                                          "delivery methods "
                                                                                          "configuration")
    forwarding_agent = fields.Many2one('res.partner', string='Forwarding Agent', help='The name of the forwarding agent')

    detailed_operations = fields.One2many('custom.clear.wizard', 'wizard_id', string='Detailed Operations')

    def action_show_detailed_operations(self):
        detailed_operations = []
        for picking in self.picking_ids:
            for move in picking.move_ids:
                detailed_operations.append((0, 0, {
                    'product_id': move.product_id.id,
                    'demand_quantity': move.product_uom_qty,
                    'done_quantity': move.quantity_done,
                }))
        self.detailed_operations = detailed_operations

    def open_clearance_wizard(self):
        return {
            'name': _('Custom Clearance'),
            'type': 'ir.actions.act_window',
            'res_model': 'custom.clearance.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'model': 'stock.picking'}
        }

    @api.depends('picking_ids')
    def _compute_move_line_ids(self):
        for wizard in self:
            move_lines = wizard.picking_ids.mapped('move_line_ids')
            wizard.move_line_ids = move_lines

    @api.onchange('picking_ids')
    def _onchange_picking_ids(self):
        move_lines = self.picking_ids.mapped('move_line_ids')
        self.move_line_ids = [(5, 0, 0)]  # Clear existing move lines
        self.move_line_ids = [(0, 0, {
            'product_id': move_line.product_id.id,
            'product_uom_id': move_line.product_uom_id.id,
            'company_id': move_line.company_id.id,
            'qty_done': move_line.qty_done,
            'product_uom_qty': self.env['stock.move'].search([('id', '=', move_line.move_id.id)]).product_uom_qty
        }) for move_line in move_lines]

    @api.depends('picking_ids')
    def _compute_move_ids(self):
        for wizard in self:
            move_lines = wizard.picking_ids.mapped('move_ids')
            wizard.move_ids = move_lines

    @api.model
    def default_get(self, fields_list):
        """'default_get' method overloaded."""
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids")
        if not active_ids:
            raise UserError(
                _("Please select at least one record to plan in a shipment.")
            )
        if active_model == "stock.picking" and active_ids:
            res = self._default_get_from_stock_picking(res, active_ids)
        if active_model == "stock.move" and active_ids:
            res = self._default_get_from_stock_move(res, active_ids)
        return res

    @api.model
    def _default_get_from_stock_picking(self, res, ids):
        pickings = self.env["stock.picking"].browse(ids)
        # We keep only deliveries and receptions not canceled/done
        pickings_to_keep = pickings.filtered_domain(
            [
                ("state", "not in", ["cancel", "done"]),
                ("picking_type_code", "in", ["incoming", "outgoing"]),
            ]
        )
        res["picking_ids"] = [(6, False, pickings_to_keep.ids)]
        if not pickings_to_keep:
            res["warning"] = _(
                "No transfer to plan among selected ones (already done or "
                "not qualified as deliveries/receptions)."
            )
        elif pickings != pickings_to_keep:
            res["warning"] = _(
                "Transfers to include have been updated, keeping only those "
                "still in progress and qualified as delivery/reception."
            )
        return res

    @api.model
    def _default_get_from_stock_move(self, res, ids):
        moves = self.env["stock.move"].browse(ids)
        # We keep only deliveries and receptions not canceled/done
        # and not linked to a package level itself linked to other moves
        # (we want to plan the package as a whole, not a part of it)
        moves_to_keep = self.env["stock.move"]
        for move in moves:
            other_moves = (
                                  move.move_line_ids.package_level_id.move_line_ids.move_id
                                  + move.package_level_id.move_ids
                          ) - moves
            if other_moves:
                continue
            moves_to_keep |= move
        moves_to_keep = moves_to_keep.filtered_domain([
            ("state", "not in", ["cancel", "done"]),
            ("picking_type_id.code", "in", ["incoming", "outgoing"]),
        ])
        res["move_ids"] = [(6, False, moves_to_keep.ids)]
        if not moves_to_keep:
            res["warning"] = _(
                "No move to plan among selected ones (already done, "
                "linked to other moves through a package, or not related "
                "to a delivery/reception)."
            )
        elif moves != moves_to_keep:
            res["warning"] = _(
                "Moves to include have been updated, keeping only those "
                "still in progress and related to a delivery/reception.")
        return res

    def action_plan(self):
        """Plan the selected records in the selected pre-alert."""
        # Ensure all selected pickings have the same partner_id
        partner_ids = self.mapped('picking_ids')
        if len(partner_ids) > 1:
            raise UserError(_("You cannot select pickings with different Suppliers"))

        self.ensure_one()
        show_pickings_with_tracking_references = False
        if self.picking_ids:
            pickings_with_tracking = []
            tracking_set = set()  # Initialize an empty set to store unique tracking references
            populate_freights = self.env['freight.order'].create({
                'shipper_id': self.shipper_id.id,
                'transport_type': self.transport_type,
                'loading_port_id': self.loading_port_id.id,
                'discharging_port_id': self.discharging_port_id.id,
                'delivery_method': self.delivery_method.id,
                'forwarding_agent': self.forwarding_agent.id,
                'agent_id': self.agent_id.id,
                'type': self.type,
                'consignee_id': self.company_id.partner_id.id,
                'supplier': self.move_ids.purchase_line_id.partner_id.id,
            })
            new_quantity = 0
            for pick in self.picking_ids:
                if not pick.carrier_tracking_ref:
                    for ref in self.move_ids:
                        if ref.picking_id.carrier_tracking_ref:
                            tracking_ref = ref.picking_id.carrier_tracking_ref
                            if tracking_ref not in tracking_set:  # Check if the tracking reference is not already in the set
                                pickings_with_tracking.append(tracking_ref)  # Append the tracking reference to the list
                                tracking_set.add(
                                    tracking_ref)  # Add the tracking reference to the set to mark it as seen

                    if populate_freights:
                        if len(pickings_with_tracking) > 1:
                            msg = _('During the automatic creation of this freight, Some pickings selected already '
                                    'had been scheduled '
                                    'for clearance, their reference(s) are: %s' % (
                                        str(pickings_with_tracking)))
                            populate_freights.message_post(body=msg, message_type='notification',
                                                           author_id=self.env.user.id)

                        for move in pick.move_ids:
                            # if not self.env['freight.bill.entry'].search([('product_id', '=', move.product_id.id),
                            #                                               ('order_id', '=', populate_freights.id)]):
                            freight_lines = self.env['freight.bill.entry'].create({
                                'order_id': populate_freights.id,
                                'product_id': move.product_id.id,
                                'cif_foreign_value': move.price_unit,
                                'unit_price': move.price_unit,
                                'purchase_order': move.purchase_line_id.order_id.id,
                                'quantity': move.pre_alert_qty,
                                'location_dest_id': move.location_dest_id.id,
                                'weight': move.weight
                            })
                            new_quantity += move.quantity_done
                        populate_freights.write({
                            'quantity': new_quantity,
                        })
                        pick.write({
                            'carrier_tracking_ref': populate_freights.name,
                        })
                else:
                    show_pickings_with_tracking_references = True
                if show_pickings_with_tracking_references:
                    raise UserError(_('All pickings selected already have been scheduled for shipment, please check '
                                      'the freight management module'))
            view_form = self.env.ref("ob_freight_management_system.freight_order_form_view")
            action_xmlid = "ob_freight_management_system.action_freight_order"
            action = self.env["ir.actions.act_window"]._for_xml_id(action_xmlid)
            del action["views"]
            action["res_id"] = populate_freights.id
            action["view_id"] = view_form.id
            action["view_mode"] = "form"
            return action

        else:
            reference = []
            for ref in self.move_ids:
                reference.append(ref.picking_id.carrier_tracking_ref)
            raise UserError(_('Some pickings selected already have been scheduled for shipment/clearance, please check '
                              'the freight management module for this(these) tracking reference(s): %s' % reference))


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_done = fields.Float(string='Quantity Done')


class DetailedOperationsLine(models.TransientModel):
    _name = 'detailed.operations.line'

    wizard_id = fields.Many2one('wizard.pre.alert', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product')
    demand_quantity = fields.Float(string='Demand Quantity')
    done_quantity = fields.Float(string='Done Quantity')


class CustomClearanceWiz(models.TransientModel):
    _name = 'custom.clear.wizard'
    _description = 'Clearance Wizard'

    wizard_id = fields.Many2one('wizard.pre.alert', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product')
    demand_quantity = fields.Float(string='Demand Quantity')
    done_quantity = fields.Float(string='Done Quantity')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    operation_ids = fields.One2many('stock.move', 'picking_id', string='Operations')

    @api.model
    def default_get(self, fields):
        # self.env['stock.move'].search([('id', '=', 28)]).action_show_details()
        res = super(CustomClearanceWiz, self).default_get(fields)
        if 'picking_id' in fields and 'default_picking_id' in self._context:
            picking_id = self._context['default_picking_id']
            picking = self.env['stock.picking'].browse(picking_id)
            res['picking_id'] = picking.id
            res['operation_ids'] = [(0, 0, {'product_id': move.product_id.id, 'demand_quantity': move.product_uom_qty,
                                            'done_quantity': move.quantity_done}) for move in picking.move_ids]
        return res

    def update_done_quantity(self):
        for operation in self.operation_ids:
            move = self.env['stock.move'].browse(operation.id)
            move.quantity_done = operation.quantity_done

    def action_show_detailed_operations(self):
        detailed_operations = []
        active_id = self.env.context.get('active_id')
        for picking in self.env['stock.picking'].search([('id', '=', active_id)]):
            for move in picking.move_ids:
                if move.quantity_done > 0:
                    to_clear = move.quantity_done
                else:
                    to_clear = move.product_uom_qty
                detailed_operations.append((0, 0, {
                    'product_id': move.product_id.id,
                    'product_uom_qty': to_clear,
                    # 'done_quantity': move.quantity_done,
                }))
        # self.detailed_operations = detailed_operations
