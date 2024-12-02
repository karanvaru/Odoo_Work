from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_price = fields.Float('Product Price', help="Product Price for Eway Bill if discount is added in sale orderline than pice should be calculated with discount if not than without discount")
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    cess_non_advol = fields.Selection([('0', '0'), ('400', '400'), ('2076', '2076'),
                                       ('2747', '2747'), ('3668', '3668'), ('4006', '4006'),
                                       ('4170', '4170')], string='CESS Non Advol Amount')
    discount = fields.Float('Discount%')
    sub_total = fields.Float('SubTotal')


    @api.model
    def create(self, vals):
        print(vals, 'vals stock move')
        if 'sale_line_id' in vals:
            line_id = self.env['sale.order.line'].browse(vals.get('sale_line_id'))
            vals['tax_id'] = [(6, 0, line_id.tax_id.ids)]
            vals['product_price'] = line_id.price_unit
            vals['discount'] = line_id.discount
            vals['sub_total'] = line_id.price_total
            print('deepak yadav order_id', line_id.order_id.amount_untaxed)
        return super(StockMove, self).create(vals)

    @api.multi
    def write(self, vals):
        print(vals, 'move write******')
        res = super(StockMove, self).write(vals)
        if 'state' in vals:
            for data in self:
                if data.sale_line_id:
                    data.tax_id = [(6, 0, data.sale_line_id.tax_id.ids)]
                    data.product_price = data.sale_line_id.price_unit
                    data.discount = data.sale_line_id.discount
                    data.sub_total = data.sale_line_id.price_total
                    print('order_id', data.sale_line_id.order_id.amount_untaxed)
        return res
