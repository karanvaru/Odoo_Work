# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class AddSaleOrderLineWizard(models.TransientModel):
    _name = 'add.sale.order.line.wizard'

    @api.model
    def default_get(self, fields):
        rec = super(AddSaleOrderLineWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_browse_id = self.env['stock.picking'].browse(active_id)
        order_ids = self.env['sale.order'].search(
            [('partner_id', '=', active_browse_id.partner_id.id), ('state', '=', 'sale')])
        list = []
        for order in order_ids:
            # line_id = order.order_line.filtered(lambda line: line.product_uom_qty != line.qty_delivered)
            for line in order.order_line:
                if line.product_uom_qty != line.qty_delivered:
                    list.append(line.id)

            rec.update({
                'actual_order_line_ids': [(6, 0, list)]
            })
        return rec

    # @api.model
    # def _get_sale_order_line_domain(self):
    #     active_id = self._context.get('active_id')
    #     active_browse_id = self.env['stock.picking'].browse(active_id)
    #     order_ids = self.env['sale.order'].search(
    #         [('partner_id', '=', active_browse_id.partner_id.id), ('state', '=', 'sale')])
    #     list = []
    #     for order in order_ids:
    #         # line_id = order.order_line.filtered(lambda line: line.product_uom_qty != line.qty_delivered)
    #         for line in order.order_line:
    #             if line.product_uom_qty != line.qty_delivered:
    #                 list.append(line.id)
    #     return [('id', 'in', list)]

    order_line_ids = fields.Many2many(
        'sale.order.line',
        # domain=[('id', 'in', self.actual_order_line_ids.ids)]/
    )
    actual_order_line_ids = fields.Many2many(
        'sale.order.line',
        relation="sale_order_line_actual",
        column1="sale_order_line_wizard_id",
        column2="sale_order_new_id",
    )

    def action_confirm(self):
        active_id = self._context.get('active_id')
        active_browse_id = self.env['stock.picking'].browse(active_id)
        active_browse_id.immediate_transfer = False
        if self.order_line_ids:
            for stock in self.order_line_ids:
                stock_qty = stock.product_uom_qty - stock.qty_delivered
                vals = {
                    'picking_id': active_browse_id.id,
                    'product_id': stock.product_id.id,
                    'name': stock.name,
                    'product_uom_qty': stock_qty,
                    'date': active_browse_id.scheduled_date,
                    'location_id': active_browse_id.picking_type_id.default_location_src_id.id,
                    'location_dest_id': active_browse_id.location_dest_id.id,
                    'picking_type_id': active_browse_id.picking_type_id.id,
                    'warehouse_id': active_browse_id.picking_type_id.warehouse_id.id,
                    'partner_id': active_browse_id.partner_id.id,
                    "product_uom": stock.product_id.uom_id.id,
                    'sale_line_id': stock.id,
                }
                self.env['stock.move'].create(vals)
