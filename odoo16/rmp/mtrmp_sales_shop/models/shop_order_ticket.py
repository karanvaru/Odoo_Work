from odoo import models, fields, api


class ShopOrderTicket(models.Model):
    _name = 'shop.order.ticket'
    _description = "Shop Order Ticket"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char(default="/")
    order_id = fields.Many2one('sale.order', string="Order #", required=True, tracking=True)
    type = fields.Selection([('return', 'Return'), ('reject', 'Rejected'), ('other', 'Other')], string="Type",
                            default='return', required=True, tracking=True)
    state = fields.Selection(
        [('new', 'New'), ('confirm', 'Confirmed'), ('goods_return', 'Goods Returned'), ('qa', 'QA'), ('issue', 'Issue'),
         ('in_settlement', 'In Settlement'), ('close', 'Closed'), ], string="State", default='new', tracking=True)
    qa_result = fields.Many2one('shop.order.ticket.quality', string='Quality Result')

    ecomm_panlulty_planned = fields.Float(string='Planned Panulty')
    ecomm_penulty_actual = fields.Float(string="Final Panulty")
    create_date = fields.Date()
    issue_date = fields.Date()
    days_remain = fields.Integer()

    quality_type = fields.Selection([('ok', 'OK'), ('not_ok', 'NotOk')], string="Quality Type",
                                    # required=True
                                    )
    comment = fields.Text(string="Description",
                          # required=True
                          )
    raise_comment = fields.Text(string="Issue Description",
                                # required=True
                                )
    in_picking = fields.Many2one('stock.picking', string="Return Picking")

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code("shop.order.ticket")
        return super(ShopOrderTicket, self).create(vals)

    def action_confirm(self):
        if self.type == 'return':
            return {
                'name': 'Return Product',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'return.product.wizard',
                'target': 'new',
            }
        elif self.type == 'reject':
            lines = []
            vals = {}
            order_line_obj = self.env['stock.return.picking']
            for res in self.order_id.order_line.filtered(lambda l: l.qty_delivered):
                lines.append((0, 0, {
                    'product_id': res.product_id.id,
                    'quantity': res.qty_delivered
                }))
            vals.update({
                'product_return_moves': lines,
                'picking_id': self.order_id.picking_ids[0].id
            })
            order_line_new = order_line_obj.new(vals)
            order_line_new._onchange_picking_id()
            order_line_values = order_line_new._convert_to_write(order_line_new._cache)
            return_id = order_line_obj.create(order_line_values)

            return_res_id = return_id.create_returns()
            self.write({'state': 'confirm', 'in_picking': return_res_id['res_id']})

    def goods_return(self):
        self.write({'state': 'goods_return'})

    def action_in_settlement(self):
        self.write({'state': 'in_settlement'})

    def action_close(self):
        self.write({'state': 'close'})
