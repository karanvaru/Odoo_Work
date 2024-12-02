# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class RmaLineWiz(models.TransientModel):
    _name = "rma.line.wiz"
    _description = "RmaLineWiz"

    @api.model
    def default_get(self, fields_list):
        """
            Override method for set default values
        """
        result = super(RmaLineWiz, self).default_get(fields_list)
        context = dict(self.env.context)
        active_id = context.get('active_id')
        rma_id = self.env['rma.issue'].browse(active_id)
        if rma_id and rma_id.associated_so:
            result.update({'sale_id': rma_id.associated_so.id})
        return result

    move_line_ids = fields.Many2many('stock.move.line', string="Move Lines")
    sale_id = fields.Many2one('sale.order', string="Sale Order")

    @api.onchange('move_line_ids')
    def onchange_move_line_ids(self):
        """
            Apply domain on move lines
        """
        res = {'domain': {'move_line_ids': []}}
        if self.sale_id:
            move_line_ids = self.sale_id.order_line.mapped('move_ids').mapped('move_line_ids').filtered(lambda l: l.move_id and l.move_id.picking_type_id.code in ['outgoing', 'internal'] and l.state == 'done' and l.qty_done > 0.0)
            res.update({'domain': {'move_line_ids': [('id', 'in', move_line_ids.ids)]}})
        return res

    @api.multi
    def generate_rma_lines(self):
        """
            Generate RMA lines depends on sales order lines
        """
        context = dict(self.env.context)
        active_id = context.get('active_id')
        rma_lines = []
        if active_id:
            issue_line_obj = self.env['rma.issue.line']
            for line in self.move_line_ids:
                issue_line_id = issue_line_obj.create({
                        'product_id': line.product_id.id,
                        'qty_delivered': line.qty_done,
                        'product_uom': line.product_uom_id.id,
                        'to_return': 1,
                        'serial_id': line.lot_id.id,
                        'reason_id': False,
                        'return_type_id': False,
                        'sale_line_id': line.move_id.sale_line_id.id,
                        'order_id': active_id
                    })
                rma_lines.append(issue_line_id.id)
        return rma_lines
