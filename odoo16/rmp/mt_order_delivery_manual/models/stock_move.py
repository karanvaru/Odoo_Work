from odoo import _, api, fields, models
from odoo.tools.misc import clean_context, OrderedSet
from collections import defaultdict
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    # def _action_confirm(self, merge=True, merge_into=False):
    #     """ Confirms stock move or put it in waiting if it's linked to another move.
    #     :param: merge: According to this boolean, a newly confirmed move will be merged
    #     in another move of the same picking sharing its characteristics.
    #     """
    #     # print("CALL========================================", self._context)
    #     if not self._context.get('from_action_confirm', False):
    #         return super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)
    #     # Use OrderedSet of id (instead of recordset + |= ) for performance
    #     move_create_proc, move_to_confirm, move_waiting = OrderedSet(), OrderedSet(), OrderedSet()
    #     to_assign = defaultdict(OrderedSet)
    #     for move in self:
    #         if move.state != 'draft':
    #             continue
    #         # if the move is preceded, then it's waiting (if preceding move is done, then action_assign has been called already and its state is already available)
    #         if move.move_orig_ids:
    #             move_waiting.add(move.id)
    #         else:
    #             if move.procure_method == 'make_to_order':
    #                 move_create_proc.add(move.id)
    #             else:
    #                 move_to_confirm.add(move.id)
    #         if move._should_be_assigned():
    #             key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
    #             to_assign[key].add(move.id)
    #
    #     move_create_proc, move_to_confirm, move_waiting = self.browse(move_create_proc), self.browse(
    #         move_to_confirm), self.browse(move_waiting)
    #
    #     # create procurements for make to order moves
    #     procurement_requests = []
    #     for move in move_create_proc:
    #         values = move._prepare_procurement_values()
    #         origin = move._prepare_procurement_origin()
    #         procurement_requests.append(self.env['procurement.group'].Procurement(
    #             move.product_id, move.product_uom_qty, move.product_uom,
    #             move.location_id, move.rule_id and move.rule_id.name or "/",
    #             origin, move.company_id, values))
    #     self.env['procurement.group'].run(procurement_requests,
    #                                       raise_user_error=not self.env.context.get('from_orderpoint'))
    #     # print("move_to_confirm", move_to_confirm)
    #     # print("CODE_____________", move_to_confirm.picking_code)
    #     # print("CODE_____________", move_to_confirm.picking_id)
    #     # move_to_confirm.write({'state': 'confirmed'})
    #     (move_waiting | move_create_proc).write({'state': 'waiting'})
    #     # procure_method sometimes changes with certain workflows so just in case, apply to all moves
    #     (move_to_confirm | move_waiting | move_create_proc).filtered(
    #         lambda m: m.picking_type_id.reservation_method == 'at_confirm') \
    #         .write({'reservation_date': fields.Date.today()})
    #
    #     # assign picking in batch for all confirmed move that share the same details
    #     for moves_ids in to_assign.values():
    #         self.browse(moves_ids).with_context(clean_context(self.env.context))._assign_picking()
    #     new_push_moves = self.filtered(lambda m: not m.picking_id.immediate_transfer)._push_apply()
    #     self._check_company()
    #     moves = self
    #     if merge:
    #         moves = self._merge_moves(merge_into=merge_into)
    #
    #     # Transform remaining move in return in case of negative initial demand
    #     neg_r_moves = moves.filtered(lambda move: float_compare(
    #         move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding) < 0)
    #     for move in neg_r_moves:
    #         move.location_id, move.location_dest_id = move.location_dest_id, move.location_id
    #         move.product_uom_qty *= -1
    #         if move.picking_type_id.return_picking_type_id:
    #             move.picking_type_id = move.picking_type_id.return_picking_type_id
    #     # detach their picking as we inverted the location and potentially picking type
    #     neg_r_moves.picking_id = False
    #     neg_r_moves._assign_picking()
    #
    #     # call `_action_assign` on every confirmed move which location_id bypasses the reservation + those expected to be auto-assigned
    #     moves.filtered(lambda move: not move.picking_id.immediate_transfer
    #                                 and move.state in ('confirmed', 'partially_available')
    #                                 and (move._should_bypass_reservation()
    #                                      or move.picking_type_id.reservation_method == 'at_confirm'
    #                                      or (move.reservation_date and move.reservation_date <= fields.Date.today()))) \
    #         ._action_assign()
    #     if new_push_moves:
    #         new_push_moves._action_confirm()
    #     return moves
