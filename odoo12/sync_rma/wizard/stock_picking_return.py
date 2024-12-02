# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    serial_id = fields.Many2one('stock.production.lot', string="Serial No.")


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        """
            Override method for set default values
        """
        if self.env.context.get('return_line'):
            if len(self.env.context.get('active_ids', list())) > 1:
                raise ValidationError("You may only return one picking at a time!")
            res = super(ReturnPicking, self).default_get(fields)
            Quant = self.env['stock.quant']
            move_dest_exists = False
            product_return_moves = []
            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            if picking:
                res['picking_id'] = picking.id
                if picking.state != 'done':
                    raise UserError(_("You may only return Done pickings"))
                for move in picking.move_lines:
                    for return_product in self.env['rma.issue.line'].browse(self.env.context.get('return_line')):
                        if move.product_id.id == return_product.product_id.id:
                            if move.scrapped:
                                continue
                            if move.move_dest_ids:
                                move_dest_exists = True
                            quantity = return_product.to_return
                            product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity, 'move_id': move.id, 'serial_id': return_product.serial_id.id}))
                if 'product_return_moves' in fields:
                    res.update({'product_return_moves': product_return_moves})
                if 'move_dest_exists' in fields:
                    res.update({'move_dest_exists': move_dest_exists})
                if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
                    res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
                if 'original_location_id' in fields:
                    res.update({'original_location_id': picking.location_id.id})
                if 'location_id' in fields:
                    location_id = picking.location_id.id
                    if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                        location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
                    res['location_id'] = location_id
            return res
        else:
            return super(ReturnPicking, self).default_get(fields)

    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        new_picking = self.picking_id.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Return of %s") % self.picking_id.name,
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values(return_line, new_picking)
                r = return_line.move_id.copy(vals)
                vals = {'serial_id': return_line.serial_id.id}

                # +--------------------------------------------------------------------------------------------------------+
                # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                # |              | returned_move_ids              ↑                                  | returned_move_ids
                # |              ↓                                | return_line.move_id              ↓
                # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                # +--------------------------------------------------------------------------------------------------------+
                move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.move_id]
                vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        new_picking.action_confirm
        new_picking.action_assign()

        if self.env.context.get('return_rma_issue_id'):
            for line in new_picking.move_line_ids:
                if line.product_id and line.product_id.tracking == 'serial' and line.move_id.serial_id:
                    line.lot_id = line.move_id.serial_id.id
        new_picking.return_rma_issue_id = self.env.context.get('return_rma_issue_id')
        if self.picking_id and not self.env.context.get('return_rma_issue_id'):
            new_picking.rma_issue_id = self.picking_id.rma_issue_id and self.picking_id.rma_issue_id.id or False
        return new_picking.id, picking_type_id
