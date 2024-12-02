# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_generate_valuations(self):
        for picking in self:
            if picking.state != 'done':
                raise UserError(_('You can generate only for Done pickings!'))
            res = picking.move_ids_without_package
            for move in res:
                # Apply restrictions on the stock move to be able to make
                # consistent accounting entries
                if move._is_in() and move._is_out():
                    raise UserError(
                        _("The move lines are not in a consistent state: some are entering and other are leaving the company."))
                company_src = move.mapped('move_line_ids.location_id.company_id')
                company_dst = move.mapped('move_line_ids.location_dest_id.company_id')
                try:
                    if company_src:
                        company_src.ensure_one()
                    if company_dst:
                        company_dst.ensure_one()
                except ValueError:
                    raise UserError(
                        _("The move lines are not in a consistent states: they do not share the same origin or destination company."))

                if company_src and company_dst and company_src.id != company_dst.id:
                    raise UserError(
                        _("The move lines are not in a consistent states: they are doing an intercompany in a single step while they should go through the intercompany transit location."))
                move._run_valuation()
            for move in res.filtered(lambda m: m.product_id.valuation == 'real_time' and (
                    m._is_in() or m._is_out() or m._is_dropshipped() or m._is_dropshipped_returned())):
                # check here if valuation not generate then call account_entry_move
                if not move.account_move_ids:
                    force_period_date = picking.scheduled_date.date()
                    if picking.date_done:
                        force_period_date = picking.date_done.date()
                    move.with_context(force_period_date=force_period_date)._account_entry_move()


class Production(models.Model):
    _inherit = 'mrp.production'

    def action_generate_valuations(self):
        for mrp in self:
            if mrp.state != 'done':
                raise UserError(_('You can generate only for Done pickings!'))
            res = mrp.move_raw_ids + mrp.move_finished_ids
            for move in res:
                # Apply restrictions on the stock move to be able to make
                # consistent accounting entries
                if move._is_in() and move._is_out():
                    raise UserError(
                        _("The move lines are not in a consistent state: some are entering and other are leaving the company."))
                company_src = move.mapped('move_line_ids.location_id.company_id')
                company_dst = move.mapped('move_line_ids.location_dest_id.company_id')
                try:
                    if company_src:
                        company_src.ensure_one()
                    if company_dst:
                        company_dst.ensure_one()
                except ValueError:
                    raise UserError(
                        _("The move lines are not in a consistent states: they do not share the same origin or destination company."))

                if company_src and company_dst and company_src.id != company_dst.id:
                    raise UserError(
                        _("The move lines are not in a consistent states: they are doing an intercompany in a single step while they should go through the intercompany transit location."))
                if move.product_qty:
                    move._run_valuation()
            for move in res.filtered(lambda m: m.product_id.valuation == 'real_time' and (
                    m._is_in() or m._is_out() or m._is_dropshipped() or m._is_dropshipped_returned())):
                # check here if valuation not generate then call account_entry_move
                if not move.account_move_ids:
                    force_period_date = move.date.date()
                    move.with_context(force_period_date=force_period_date)._account_entry_move()

    def _cal_price_extend(self, consumed_moves, finished_move):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        work_center_cost = 0
        #         finished_move = self#.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                time_lines = work_order.time_ids.filtered(lambda x: x.date_end and not x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))
                time_lines.write({'cost_already_recorded': True})
                work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour
            if finished_move.product_id.cost_method in ('fifo', 'average'):
                qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done,
                                                                       finished_move.product_id.uom_id)
                finished_move.price_unit = (sum([-m.value for m in consumed_moves]) + work_center_cost) / qty_done
                finished_move.value = sum([-m.value for m in consumed_moves]) + work_center_cost
                finished_move.remaining_value = finished_move.value


class StockMoves(models.Model):
    _inherit = 'stock.move'

    # @api.model
    # def _run_fifo(self, move, quantity=None):
    #     """ Value `move` according to the FIFO rule, meaning we consume the
    #     oldest receipt first. Candidates receipts are marked consumed or free
    #     thanks to their `remaining_qty` and `remaining_value` fields.
    #     By definition, `move` should be an outgoing stock move.
    #
    #     :param quantity: quantity to value instead of `move.product_qty`
    #     :returns: valued amount in absolute
    #     """
    #     move.ensure_one()
    #
    #     # Deal with possible move lines that do not impact the valuation.
    #     valued_move_lines = move.move_line_ids.filtered(lambda
    #                                                         ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
    #     valued_quantity = 0
    #     for valued_move_line in valued_move_lines:
    #         valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
    #                                                                              move.product_id.uom_id)
    #
    #     # Find back incoming stock moves (called candidates here) to value this move.
    #     qty_to_take_on_candidates = quantity or valued_quantity
    #     candidates = move.product_id._get_fifo_candidates_in_move_with_company(move.company_id.id)
    #     new_standard_price = 0
    #     tmp_value = 0  # to accumulate the value taken on the candidates
    #     for candidate in candidates:
    #         new_standard_price = candidate.price_unit
    #         if candidate.remaining_qty <= qty_to_take_on_candidates:
    #             qty_taken_on_candidate = candidate.remaining_qty
    #         else:
    #             qty_taken_on_candidate = qty_to_take_on_candidates
    #
    #         # As applying a landed cost do not update the unit price, naivelly doing
    #         # something like qty_taken_on_candidate * candidate.price_unit won't make
    #         # the additional value brought by the landed cost go away.
    #         candidate_price_unit = candidate.remaining_value / candidate.remaining_qty
    #         value_taken_on_candidate = qty_taken_on_candidate * candidate_price_unit
    #         candidate_vals = {
    #             'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
    #             'remaining_value': candidate.remaining_value - value_taken_on_candidate,
    #         }
    #         candidate.write(candidate_vals)
    #
    #         qty_to_take_on_candidates -= qty_taken_on_candidate
    #         tmp_value += value_taken_on_candidate
    #
    #         if qty_to_take_on_candidates == 0:
    #             break
    #
    #     # Update the standard price with the price of the last used candidate, if any.
    #     if new_standard_price and move.product_id.cost_method == 'fifo':
    #         move.product_id.sudo().with_context(force_company=move.company_id.id) \
    #             .standard_price = new_standard_price
    #
    #     # If there's still quantity to value but we're out of candidates, we fall in the
    #     # negative stock use case. We chose to value the out move at the price of the
    #     # last out and a correction entry will be made once `_fifo_vacuum` is called.
    #     if quantity:
    #         if qty_to_take_on_candidates == 0:
    #             move.write({
    #                 'value': -tmp_value if not quantity else move.value or -tmp_value,
    #                 # outgoing move are valued negatively
    #                 'price_unit': -tmp_value / (move.product_qty or quantity),
    #             })
    #     elif qty_to_take_on_candidates > 0:
    #         last_fifo_price = new_standard_price or move.product_id.standard_price
    #         negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
    #         tmp_value += abs(negative_stock_value)
    #         vals = {
    #             'remaining_qty': move.remaining_qty + -qty_to_take_on_candidates,
    #             'remaining_value': move.remaining_value + negative_stock_value,
    #             'value': -tmp_value,
    #             'price_unit': -1 * last_fifo_price,
    #         }
    #         move.write(vals)
    #     return tmp_value

    # @api.model
    # def _run_fifo(self, move, quantity=None):
    #     if not self._context.get('regenerate_valuation', False):
    #         return super(StockMoves, self)._run_fifo(move, quantity)
    #     """ Value `move` according to the FIFO rule, meaning we consume the
    #     oldest receipt first. Candidates receipts are marked consumed or free
    #     thanks to their `remaining_qty` and `remaining_value` fields.
    #     By definition, `move` should be an outgoing stock move.
    #
    #     :param quantity: quantity to value instead of `move.product_qty`
    #     :returns: valued amount in absolute
    #     """
    #     move.ensure_one()
    #
    #     # Deal with possible move lines that do not impact the valuation.
    #     valued_move_lines = move.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
    #     valued_quantity = 0
    #     for valued_move_line in valued_move_lines:
    #         valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
    #
    #     # Find back incoming stock moves (called candidates here) to value this move.
    #     qty_to_take_on_candidates = quantity or valued_quantity
    #     candidates = move.product_id._get_fifo_candidates_in_move_with_company(move.company_id.id)
    #     new_standard_price = 0
    #     tmp_qty = 0
    #     tmp_value = 0  # to accumulate the value taken on the candidates
    #     for candidate in candidates:
    #
    #         new_standard_price = candidate.price_unit
    #         if candidate.remaining_qty <= qty_to_take_on_candidates:
    #             qty_taken_on_candidate = candidate.remaining_qty
    #         else:
    #             qty_taken_on_candidate = qty_to_take_on_candidates
    #
    #         # As applying a landed cost do not update the unit price, naivelly doing
    #         # something like qty_taken_on_candidate * candidate.price_unit won't make
    #         # the additional value brought by the landed cost go away.
    #         candidate_price_unit = candidate.remaining_value / candidate.remaining_qty
    #         if not candidate_price_unit:
    #             candidate_price_unit = candidate.price_unit
    #         value_taken_on_candidate = qty_taken_on_candidate * candidate_price_unit
    #         candidate_vals = {
    #             'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
    #             'remaining_value': candidate.remaining_value - value_taken_on_candidate,
    #         }
    #         candidate.write(candidate_vals)
    #
    #         qty_to_take_on_candidates -= qty_taken_on_candidate
    #         tmp_qty += qty_taken_on_candidate
    #         tmp_value += value_taken_on_candidate
    #         if qty_to_take_on_candidates == 0:
    #             break
    #
    #     # Update the standard price with the price of the last used candidate, if any.
    #     if new_standard_price and move.product_id.cost_method == 'fifo':
    #         move.product_id.sudo().with_context(force_company=move.company_id.id) \
    #             .standard_price = new_standard_price
    #     # If there's still quantity to value but we're out of candidates, we fall in the
    #     # negative stock use case. We chose to value the out move at the price of the
    #     # last out and a correction entry will be made once `_fifo_vacuum` is called.
    #     if qty_to_take_on_candidates == 0:
    #         # If the move is not valued yet we compute the price_unit based on the value taken on
    #         # the candidates.
    #         # If the move has already been valued, it means that we editing the qty_done on the
    #         # move. In this case, the price_unit computation should take into account the quantity
    #         # already valued and the new quantity taken.
    #         if not move.value:
    #             price_unit = -tmp_value / (move.product_qty or quantity)
    #         else:
    #             if (tmp_qty + move.product_qty) != 0:
    #                 price_unit = (-(tmp_value) + move.value) / (tmp_qty + move.product_qty)
    #             else:
    #                 price_unit = 0
    #         move.write({
    #             'value': -tmp_value if not quantity else move.value or -tmp_value,  # outgoing move are valued negatively
    #             'price_unit': price_unit,
    #         })
    #
    #     elif qty_to_take_on_candidates > 0:
    #         last_fifo_price = new_standard_price or move.product_id.standard_price
    #         negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
    #         tmp_value += abs(negative_stock_value)
    #
    #         vals = {
    #             'remaining_qty': move.remaining_qty + -qty_to_take_on_candidates,
    #             'remaining_value': move.remaining_value + negative_stock_value,
    #             'value': -tmp_value,
    #             'price_unit': -1 * last_fifo_price,
    #         }
    #         move.write(vals)
    #     return tmp_value

    def action_generate_valuations(self):
        self.product_price_update_before_done()
        for move in self:
            if move.state != 'done':
                raise UserError(_('You can generate only for Done moves!'))
                # Apply restrictions on the stock move to be able to make
                # consistent accounting entries
            #             correction_value = move._run_valuation(move.product_uom_qty)
            #             if not move.account_move_ids:
            #                 force_period_date = move.date.date()
            #                 if move.product_id.valuation == 'real_time' and (move._is_in() or move._is_out()):
            #                     move.with_context(
            #                         force_valuation_amount=correction_value,
            #                         force_period_date=force_period_date
            #                     )._account_entry_move()

            #                     move.with_context(force_period_date=force_period_date)._account_entry_move()

            if move._is_in() and move._is_out():
                _logger.info(
                    "=================================Error Record in or out======================================%s",
                    move.id)
                raise UserError(
                    _("The move lines are not in a consistent state: some are entering and other are leaving the company."))
            company_src = move.mapped('move_line_ids.location_id.company_id')
            company_dst = move.mapped('move_line_ids.location_dest_id.company_id')
            _logger.info("===============================company src=============%s", company_src)
            _logger.info("===============================company dst=============%s", company_dst)
            try:
                if company_src:
                    company_src.ensure_one()
                if company_dst:
                    company_dst.ensure_one()
            except ValueError:
                _logger.info(
                    "=================================Error Record in expect part======================================%s",
                    move.id)
                raise UserError(
                    _("The move lines are not in a consistent states: they do not share the same origin or destination company."))

            if company_src and company_dst and company_src.id != company_dst.id:
                _logger.info("=================================Error Record======================================%s",
                             move.id)
                raise UserError(
                    _("The move lines are not in a consistent states: they are doing an intercompany in a single step while they should go through the intercompany transit location."))
            if not move.account_move_ids:
                move.with_context(regenerate_valuation=True)._run_valuation(move.product_qty)

        for move in self.filtered(lambda m: m.product_id.valuation == 'real_time' and (
                m._is_in() or m._is_out() or m._is_dropshipped() or m._is_dropshipped_returned())):
            if move.production_id:
                order = move.production_id
                moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
                moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))

                moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
                order._cal_price_extend(order.move_raw_ids, move)

            # check here if valuation not generate then call account_entry_move
            if not move.account_move_ids:
                force_period_date = move.date.date()
                move.with_context(force_period_date=force_period_date)._account_entry_move()
        # if self._context.get('run_sale_sync', True):
        #     self.sale_margin_sync()

    def stock_move_syc_custom(self):
        for move in self:
            if not move.account_move_ids:
                if move.remaining_qty and move.remaining_value:
                    if not move.value and move.remaining_qty and move.remaining_value:
                        move.write({'remaining_value': 0,
                                    'remaining_qty': 0
                                    })

    def stock_mrp_move_syc_custom(self):
        for move in self:
            if not move.account_move_ids and move.production_id:
                if move.value == 0.0:
                    move.update({'remaining_qty': 0,
                                 'remaining_value': 0,
                                 })
