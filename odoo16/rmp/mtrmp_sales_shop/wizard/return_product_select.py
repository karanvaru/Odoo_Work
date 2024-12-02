from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReturnProduct(models.TransientModel):
    _name = "return.product.wizard"
    _description = "Return Product Wizard"

    select_product_ids = fields.One2many('select.product.wizard', 'return_product_id')

    @api.model
    def default_get(self, fields):
        rec = super(ReturnProduct, self).default_get(fields)
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        if active_model == 'shop.order.ticket':
            ticket_id = self.env['shop.order.ticket'].browse(active_id)
            lines = []
            for res in ticket_id.order_id.order_line.filtered(lambda l: l.qty_delivered):
                lines.append((0, 0, {
                    'product_id': res.product_id.id,
                    'qty_delivered': res.qty_delivered
                }))
            rec.update({
                'select_product_ids': lines,
            })
        elif active_model == 'sale.order':
            sale_id = self.env['sale.order'].browse(active_id)
            lines = []
            for res in sale_id.order_line.filtered(lambda l: l.qty_delivered):
                lines.append((0, 0, {
                    'product_id': res.product_id.id,
                    'qty_delivered': res.qty_delivered
                }))
            rec.update({
                'select_product_ids': lines,
            })
        return rec

    def return_records(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        if active_model == 'shop.order.ticket':
            ticket_record = self.env['shop.order.ticket'].browse(active_id)
            order_line_obj = self.env['stock.return.picking']
            lines = []
            vals = {}
            pro_qty = {}
            for rec in self.select_product_ids.filtered(lambda l: l.qty_returned):
                lines.append((0, 0, {
                    'product_id': rec.product_id.id,
                }))
                pro_qty[rec.product_id] = rec.qty_returned
            vals.update({
                'product_return_moves': lines,
                'picking_id': ticket_record.order_id.picking_ids[0].id
            })
            order_line_new = order_line_obj.new(vals)
            order_line_new._onchange_picking_id()
            for record in order_line_new.product_return_moves:
                if record.product_id in pro_qty:
                    record.quantity = pro_qty[record.product_id]
            order_line_values = order_line_new._convert_to_write(order_line_new._cache)
            return_id = order_line_obj.create(order_line_values)
            return_res_id = return_id.create_returns()
            ticket_record.update({
                'state': 'confirm',
                'in_picking': return_res_id['res_id']
            })
        elif active_model == 'sale.order':
            sale_id = self.env['sale.order'].browse(active_id)
            order_line_obj = self.env['stock.return.picking']
            lines = []
            vals = {}
            pro_qty = {}

            for rec in self.select_product_ids.filtered(lambda l: l.qty_returned):
                lines.append((0, 0, {
                    'product_id': rec.product_id.id,
                }))
                pro_qty[rec.product_id] = rec.qty_returned
            vals.update({
                'product_return_moves': lines,
                'picking_id': sale_id.picking_ids[0].id
            })
            order_line_new = order_line_obj.new(vals)
            order_line_new._onchange_picking_id()
            for record in order_line_new.product_return_moves:
                if record.product_id in pro_qty:
                    record.quantity = pro_qty[record.product_id]
            order_line_values = order_line_new._convert_to_write(order_line_new._cache)
            return_id = order_line_obj.create(order_line_values)
            return_res_id = return_id.create_returns()
            ticket_vals = {
                'order_id': sale_id.id,
                'type': sale_id.type,
                'state': 'confirm',
                'in_picking': return_res_id['res_id']
            }
            ge_ticket_id = self.env['shop.order.ticket'].create(ticket_vals)
            sale_id.update({
                'request_id': ge_ticket_id.id,
            })


class SelectProductWizard(models.TransientModel):
    _name = "select.product.wizard"
    _description = "select Product Wizard"

    return_product_id = fields.Many2one('return.product.wizard')
    product_id = fields.Many2one('product.product', string="Product")
    qty_delivered = fields.Float(string="Delivered Quantity")
    qty_returned = fields.Float(string="Returned Quantity")

    @api.constrains('qty_returned')
    def default_qty_returned(self):
        for rec in self:
            if rec.qty_delivered < rec.qty_returned:
                raise UserError(_('Returned Quantity Should Be Less  To Delivered Quantity'))
