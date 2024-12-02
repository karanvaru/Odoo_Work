# -*- coding: utf-8 -*-
from odoo import fields, models, api

from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    foc_qty = fields.Float(string="FOC Qty")

    # @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    # def _get_to_invoice_qty(self):
    #     res = super(SaleOrderLine, self)._get_to_invoice_qty()
    #     for line in self:
    #         if line.foc_qty:
    #             if line.qty_to_invoice > 0 and not line.product_id.invoice_policy == 'order':
    #                 line.qty_to_invoice -= line.foc_qty
    #     return res

    # @api.multi
    # def _prepare_invoice_line(self, qty):
    #     res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
    #     res.update({'foc_qty': self.foc_qty})
    #     return res

    # @api.multi
    # def _action_launch_stock_rule(self):
    #     """
    #     Launch procurement group run method with required/custom fields genrated by a
    #     sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
    #     depending on the sale order line product rule.
    #     """
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     errors = []
    #     for line in self:
    #         if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
    #             continue
    #         qty = line._get_qty_procurement()
    #         if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
    #             continue

    #         group_id = line.order_id.procurement_group_id
    #         if not group_id:
    #             group_id = self.env['procurement.group'].create({
    #                 'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
    #                 'sale_id': line.order_id.id,
    #                 'partner_id': line.order_id.partner_shipping_id.id,
    #             })
    #             line.order_id.procurement_group_id = group_id
    #         else:
    #             # In case the procurement group is already created and the order was
    #             # cancelled, we need to update certain values of the group.
    #             updated_vals = {}
    #             if group_id.partner_id != line.order_id.partner_shipping_id:
    #                 updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
    #             if group_id.move_type != line.order_id.picking_policy:
    #                 updated_vals.update({'move_type': line.order_id.picking_policy})
    #             if updated_vals:
    #                 group_id.write(updated_vals)

    #         values = line._prepare_procurement_values(group_id=group_id)
    #         product_qty = line.product_uom_qty - qty
    #         product_qty += line.foc_qty
    #         procurement_uom = line.product_uom
    #         quant_uom = line.product_id.uom_id
    #         get_param = self.env['ir.config_parameter'].sudo().get_param
    #         if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
    #             product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
    #             procurement_uom = quant_uom

    #         try:
    #             self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
    #                                               line.order_id.partner_shipping_id.property_stock_customer, line.name,
    #                                               line.order_id.name, values)
    #         except UserError as error:
    #             errors.append(error.name)
    #     if errors:
    #         raise UserError('\n'.join(errors))
    #     return True

    # @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    # def _get_invoice_qty(self):
    #     """
    #     Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
    #     that this is the case only if the refund is generated from the SO and that is intentional: if
    #     a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
    #     it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
    #     """
    #     for line in self:
    #         qty_invoiced = 0.0
    #         for invoice_line in line.invoice_lines:
    #             if invoice_line.invoice_id.state != 'cancel':
    #                 if invoice_line.invoice_id.type == 'out_invoice':
    #                     qty_invoiced += invoice_line.uom_id._compute_quantity(invoice_line.quantity + line.foc_qty, line.product_uom)
    #                 elif invoice_line.invoice_id.type == 'out_refund':
    #                     qty_invoiced -= invoice_line.uom_id._compute_quantity(invoice_line.quantity + line.foc_qty, line.product_uom)
    #         line.qty_invoiced = qty_invoiced
