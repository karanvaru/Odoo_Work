# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    value_price_unit = fields.Float(string="Value Price", readonly=True)



# class StockMove(models.Model):
#     _inherit = "stock.move"

#     def _run_valuation(self, quantity=None):
#         self.ensure_one()
#         if self._context.get('regenerate_valuation', False):
#             return super(StockMove, self)._run_valuation(quantity=quantity)

#         return_super = False

#         if self._is_dropshipped() or self._is_dropshipped_returned():
#             return_super = True
#         else:
#             if (not self.purchase_line_id) and (not self.sale_line_id) and (not self.production_id):
#                 return_super = True
#             elif self.sale_line_id.foc_qty < 0:
#                 return_super = True
#             elif self.purchase_line_id.foc_qty < 0:
#                 return_super = True

#         if return_super:
#             return super(StockMove, self)._run_valuation(quantity=quantity)

#         value_to_return = 0
#         if self._is_in():
#             valued_move_lines = self.move_line_ids.filtered(lambda ml: not ml.location_id._should_be_valued() and ml.location_dest_id._should_be_valued() and not ml.owner_id)
#             valued_quantity = 0
#             for valued_move_line in valued_move_lines:
#                 valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)

#             if self.purchase_line_id and self.purchase_line_id.foc_qty:
#                 if (self.purchase_line_id.qty_received + valued_quantity)>= (self.purchase_line_id.product_qty + self.purchase_line_id.foc_qty):
#                     valued_quantity = valued_quantity - self.purchase_line_id.foc_qty
#             elif self.sale_line_id and self.sale_line_id.foc_qty:
#                 if self.sale_line_id.qty_delivered >= (self.sale_line_id.product_uom_qty + self.sale_line_id.foc_qty):
#                     valued_quantity = valued_quantity - self.sale_line_id.foc_qty
 
#             # Note: we always compute the fifo `remaining_value` and `remaining_qty` fields no
#             # matter which cost method is set, to ease the switching of cost method.
#             vals = {}
#             price_unit = self._get_price_unit()
#             value = price_unit * (quantity or valued_quantity)
#             value_to_return = value if quantity is None or not self.value else self.value
#             vals = {
#                 'price_unit': price_unit,
#                 'value': value_to_return,
#                 'remaining_value': value if quantity is None else self.remaining_value + value,
#             }
#             vals['remaining_qty'] = valued_quantity if quantity is None else self.remaining_qty + quantity

#             if self.product_id.cost_method == 'standard':
#                 value = self.product_id.standard_price * (quantity or valued_quantity)
#                 value_to_return = value if quantity is None or not self.value else self.value
#                 vals.update({
#                     'price_unit': self.product_id.standard_price,
#                     'value': value_to_return,
#                 })

#             self.write(vals)

#             if self.production_id:
#                 for lot_id in self.move_line_ids.mapped('lot_id'):
#                     lot_id.value_price_unit = price_unit
#             if not self.production_id:
#                 max_len = 1
#                 for lot_id in self.move_line_ids.mapped('lot_id'):
#                     if max_len <= valued_quantity:
#                         lot_id.value_price_unit = price_unit
#                     else:
#                         lot_id.value_price_unit = 0
#                     max_len += 1
#             elif self.production_id:
#                 for lot_id in self.move_line_ids.mapped('lot_id'):
#                     lot_id.value_price_unit = price_unit

#         elif self._is_out():
#             valued_move_lines = self.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
#             valued_quantity = 0
#             for valued_move_line in valued_move_lines:
#                 valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)
 
#             if self.sale_line_id and self.sale_line_id.foc_qty:
#                 if self.sale_line_id.qty_delivered >= (self.sale_line_id.product_uom_qty + self.sale_line_id.foc_qty):
#                     valued_quantity = valued_quantity - self.sale_line_id.foc_qty
#             elif self.purchase_line_id and self.purchase_line_id.foc_qty:
#                 if (self.purchase_line_id.qty_received + valued_quantity)>= (self.purchase_line_id.product_qty + self.purchase_line_id.foc_qty):
#                     valued_quantity = valued_quantity - self.purchase_line_id.foc_qty

#             self.env['stock.move']._run_fifo(self, quantity=quantity)
#             if self.product_id.cost_method in ['standard', 'average', 'fifo']:
#                 curr_rounding = self.company_id.currency_id.rounding
#                 value = 0
#                 lot_ids = self.move_line_ids.mapped('lot_id')
#                 if lot_ids:
#                     for lot_id in lot_ids:
#                         value -= lot_id.value_price_unit
#                 else:
#                     value = -float_round(self.product_id.standard_price * (valued_quantity if quantity is None else quantity), precision_rounding=curr_rounding)
#                 value_to_return = value if quantity is None else self.value + value

#                 self.write({
#                     'value': value_to_return,
#                     'price_unit': value / valued_quantity,
#                 })
#         elif self._is_dropshipped() or self._is_dropshipped_returned():
#             curr_rounding = self.company_id.currency_id.rounding
#             if self.product_id.cost_method in ['fifo']:
#                 price_unit = self._get_price_unit()
#                 # see test_dropship_fifo_perpetual_anglosaxon_ordered
#                 self.product_id.standard_price = price_unit
#             else:
#                 price_unit = self.product_id.standard_price
#             value = float_round(self.product_qty * price_unit, precision_rounding=curr_rounding)
#             value_to_return = value if self._is_dropshipped() else -value
#             # In move have a positive value, out move have a negative value, let's arbitrary say
#             # dropship are positive.
#             self.write({
#                 'value': value_to_return,
#                 'price_unit': price_unit if self._is_dropshipped() else -price_unit,
#             })
#         return value_to_return
