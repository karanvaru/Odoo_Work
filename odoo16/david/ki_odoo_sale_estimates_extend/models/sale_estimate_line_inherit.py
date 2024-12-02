from odoo import fields, models, api, _


class SaleEstimateLineInherit(models.Model):
    _inherit = 'sale.estimate.line'

    item_code = fields.Char(
        string="Item Code",
    )
    display_type = fields.Selection(
        [('line_section', 'Section'),
         ('line_note', 'Note')],
        string="Display Type",
    )

    name = fields.Text(
        string="Name",
        precompute=True
    )
    price_total = fields.Monetary(
        string="Total",
        compute='_compute_amount',
        store=True,
        precompute=True
    )
    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount',

        store=True, precompute=True)


    currency_id = fields.Many2one(
        related='estimate_id.currency_id',
        depends=['estimate_id.currency_id'],
        store=True, precompute=True)

    @api.depends('product_uom_qty','price_unit','product_uom_qty','discount','tax_id')
    def _compute_amount(self):
        for rec in self:
            tax_results = self.env['account.tax']._compute_taxes([rec._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            amount_tax = totals['amount_tax']
            amount_untaxed = totals['amount_untaxed']

            if rec.discount:
                disc_amount = (rec.price_unit * rec.product_uom_qty) * rec.discount / 100
                rec.price_subtotal = (rec.price_unit * rec.product_uom_qty) - disc_amount
            else:
                rec.price_subtotal = rec.price_unit * rec.product_uom_qty
            rec.update({
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
                'price_subtotal': rec.price_unit * rec.product_uom_qty,
            })

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.estimate_id.partner_id,
            currency=self.estimate_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty,
            discount=self.discount,
            price_subtotal=self.price_subtotal,
        )

    @api.onchange('item_code')
    def onchange_item_code(self):
        if self.item_code:
            product = self.env['product.product'].sudo().search([('default_code', '=', self.item_code)])
            if product:
                self.product_id = product.id
            else:
                self.product_id = None

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.product_description = self.name

    @api.onchange('product_id')
    def onchange_product_id(self):
        for line in self:
            line.name = line.product_id.display_name
            if line.product_id.description_sale:
                line.name += '\n' + line.product_id.description_sale
            if line.product_id.default_code:
                self.item_code = line.product_id.default_code
