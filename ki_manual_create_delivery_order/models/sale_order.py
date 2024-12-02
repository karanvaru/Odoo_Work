from odoo import api, fields, models, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # delivery_order_count = fields.Integer(string='Transfer Delivery Orders', compute='_compute_delivery_orders')

    def action_view_delivery(self):
        stock = self.env['stock.move'].search([('sale_line_id', 'in', self.order_line.ids)])
        if stock:
            picking_ids = stock.mapped('picking_id')
            act = self.env.ref('stock.action_picking_tree_all').sudo().read([])[0]
            act['domain'] = [('id', 'in', picking_ids.ids)]
            return act
        return True

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for rec in self:
            stock = self.env['stock.move'].search([('sale_line_id', 'in', rec.order_line.ids)])
            picking_ids = stock.mapped('picking_id')
            rec.delivery_count = len(picking_ids)

    # def _compute_delivery_orders(self):
    #     for rec in self:
    #         stock = self.env['stock.move'].search([('sale_line_id', 'in', rec.order_line.ids)])
    #         picking_ids = stock.mapped('picking_id')
    #         rec.delivery_order_count = len(picking_ids)
    #
    # def action_delivery_order(self):
    #     stock = self.env['stock.move'].search([('sale_line_id', 'in', self.order_line.ids)])
    #     if stock:
    #         picking_ids = stock.mapped('picking_id')
    #         act = self.env.ref('stock.action_picking_tree_all').sudo().read([])[0]
    #         act['domain'] = [('id', 'in', picking_ids.ids)]
    #         return act
    #     return True


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        create_delivery = self._context.get('create_delivery')
        if create_delivery:
            res = super(SaleOrderLineInherit, self)._action_launch_stock_rule(previous_product_uom_qty)
            return res
        return True
