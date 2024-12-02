from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo import api, fields, models
from datetime import datetime


class ReddotPurchaseOrder(models.Model):
    _inherit = "purchase.order.line"
    _description = 'Reddot Purchase Order'

    rebate_per_unit = fields.Float('Rebate', help='The expected price support from the supplier')
    rebate_id = fields.Many2one('product.rebate', string='Product Rebate',
                                help='The expected price support from the supplier')

    selling_price = fields.Float('Selling Price', help='')
    rebate_subtotal = fields.Monetary(
        string='Rebate Subtotal',
        compute='_compute_rebate_totals', store=True,
        currency_field='currency_id')
    total_selling_price = fields.Monetary(
        string='Subtotal Selling',
        compute='_compute_selling_totals', store=True,
        currency_field='currency_id', readonly=True)
    margin = fields.Float('Margin %', compute='_compute_margin_percentage',
                          help='The resultant margin percentage resulting from the difference between the '
                               'selling price and the current price/buying price from the supplier.')

    @api.depends('product_qty', 'selling_price')
    def _compute_rebate_totals(self):
        for line in self:
            if line.rebate_id:
                rebate_sub_total = line.product_qty * line.rebate_id.rebate
                (line.update({
                    'rebate_subtotal': rebate_sub_total,
                    'margin': (line.selling_price - line.price_unit) / 100
                }))

    # @api.depends('price_unit', 'selling_price')
    # def _compute_profit_margin(self):
    #     for line in self:
    #         (line.update({
    #             'margin': (line.selling_price - line.price_unit) / 100
    #         }))

    @api.depends('product_qty', 'selling_price')
    def _compute_selling_totals(self):
        for line in self:
            line.update({
                'total_selling_price': line.product_qty * line.selling_price
            })

    @api.depends('price_unit', 'selling_price')
    def _compute_margin_percentage(self):
        for record in self:
            if record.selling_price != 0 and record.price_subtotal != 0:
                record.margin = ((record.total_selling_price - record.price_subtotal) / record.price_subtotal) * 100
            else:
                record.margin = 0

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'rebate_per_unit')
    def _compute_amount(self):
        reb = 0.0
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            # Uncommenting rebate table which does not work now
            # current_date = datetime.now()
            # if line.rebate_id.start_date and line.rebate_id.end_date and line.rebate_id.rebate:
            #     if line.rebate_id.start_date <= current_date <= line.rebate_id.end_date:
            #         reb = line.rebate_id.rebate * line.product_qty
            #     else:
            #         reb = 0.0
            reb = line.rebate_per_unit * line.product_qty

            line.update({
                'price_subtotal': amount_untaxed - reb,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax - reb,
            })

    @api.onchange('product_id', 'product_template_id')
    def get_product_rebate_domain(self):
        today_date = fields.Date.today()
        if self.product_id:
            return {'domain': {'rebate_id': [
                ('product_id', '=', self.product_id.id),
                '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False),
                '|', ('start_date', '=', False), ('start_date', '<=', today_date),
                '|', ('end_date', '=', False), ('end_date', '>=', today_date)
            ]}}
        else:
            return {'domain': {'rebate_id': [
                '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False),
                '|', ('start_date', '=', False), ('start_date', '<=', today_date),
                '|', ('end_date', '=', False), ('end_date', '>=', today_date)
            ]}}


class InheritPartnersRdd(models.Model):
    _inherit = 'res.partner'
    _description = 'RDD Partners'

    freight_forwarder = fields.Boolean(string="Is a forwarding agent", default=False, tracking=True)
