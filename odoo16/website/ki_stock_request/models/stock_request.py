from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockRequest(models.Model):
    _name = "partner.stock.request"
    _description = "Stock Request"

    name = fields.Char(
        copy=False,
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        readonly=True,
        tracking=True,
        default=lambda self: self.env.user,
        string='Responsible'
    )
    company_id = fields.Many2one(
        "res.company",
        states={"draft": [("readonly", False)]},
        readonly=True,
        default=lambda self: self.env.company
    )
    date = fields.Date(
        index=True,
        readonly=True,
        default=fields.Date.today()
    )
    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        string="Channel Partner",
        copy=False
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("cancelled", "Cancelled"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        copy=False,
        default="draft",
        readonly=True,
        tracking=True,
    )

    line_ids = fields.One2many(
        'partner.stock.request.line',
        'request_id',
        string = "Lines",
    )

    sale_counts = fields.Integer(
        compute='_compute_sale_data',
        string="Number of Costing"
    )
    sale_ids = fields.One2many(
        'sale.order',
        'stock_request_id',
        string='Sale Orders'
    )

    description = fields.Text(
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        copy=False,
    )

    total = fields.Float(
        required=True,
        readonly=True,
        string='Total',
        compute='_compute_amount',
    )
    tax_totals = fields.Binary(
        compute='_compute_tax_totals',
        exportable=False
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        compute='_amount_all',
        tracking=5
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        store=True,
        compute='_amount_all'
    )
    amount_total = fields.Monetary(
        string="Total",
        store=True,
        compute='_amount_all',
        tracking=4
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )

    @api.depends('line_ids.subtotal')
    def _amount_all(self):
        for order in self:
            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in self.line_ids
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.company_id.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.company_id.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(self.line_ids.mapped('subtotal_without_tax'))
                amount_tax = sum(self.line_ids.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.amount_untaxed + order.amount_tax

    @api.depends(
        'line_ids.tax_ids',
        'line_ids.price_unit',
        'amount_total',
        'amount_untaxed',
        'currency_id'
    )
    def _compute_tax_totals(self):
        for order in self:
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in self.line_ids],
                order.currency_id or order.company_id.currency_id,
            )

    @api.depends(
        'line_ids',
                 )
    def _compute_amount(self):
        for rec in self:
            total = 0
            for mline in rec.line_ids:
                total += mline.subtotal
            rec.update({
                'total': total
            })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.request') or 'New'
        result = super(StockRequest, self).create(vals)
        return result

    def action_draft(self):
        self.write({"state": "draft"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True

    def action_submitted(self):
        self.write({"state": "submitted"})
        return True

    def action_approved(self):
        self.write({"state": "approved"})
        return True

    def action_rejected(self):
        self.write({
            "state": "rejected"
        })
        return True

    @api.depends(
        'sale_ids'
    )
    def _compute_sale_data(self):
        for lead in self:
            lead.sale_counts = len(lead.sale_ids.filtered_domain(self._get_lead_request_domain()))

    def _get_lead_request_domain(self):
        return [(
            'state', 'in', ('draft'))
        ]

    def action_view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('stock_request_id', '=', self.id)]
        return action

    def prepare_sale_order(self):
        vals = {
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'stock_request_id': self.id,
            'customer_id': self.customer_id.id,
        }
        return vals

    def action_sale_new(self):
        docs = self.env['sale.order']
        for order in self:
            res = order.prepare_sale_order()
            sale = docs.sudo().create(res)
            sale.order_line = [(5, 0, 0)]
            values = []
            for lines in order.line_ids:
                values.append((0, 0, {
                    'product_id': lines.product_id.id,
                    'product_uom_qty': lines.quantity,
                    'product_uom': lines.product_uom_id.id,
                    'tax_id': lines.tax_ids,
                }))

            sale.order_line = values
            action = self.env["ir.actions.actions"]._for_xml_id(
                "sale.action_quotations_with_onboarding"
            )
            action['domain'] = [
                ('id', '=', sale.id)
            ]
            action['views'] = [(self.env.ref(
                'sale.view_order_form'
            ).id, 'form')]
            action['res_id'] = sale.id
        return action

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft"):
            raise UserError(_("Only requests on draft state can be unlinked"))
        return super(StockRequest, self).unlink()


class StockRequestLine(models.Model):
    _name = "partner.stock.request.line"
    _description = "Stock Request Line"

    product_id = fields.Many2one(
        "product.product",
        required=True
    )
    request_id = fields.Many2one(
        "partner.stock.request"
    )
    name = fields.Text(
        string="Description",
        required=True
    )
    quantity = fields.Float(
        store=True,
        string="Quantity"
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Product Unit of Measure'
    )
    price_unit = fields.Float(
        required=False,
        string='Price'
    )
    price_tax = fields.Float(
        readonly=True,
    )
    tax_ids = fields.Many2many(
        'account.tax',
    )
    subtotal = fields.Float(
        required=False,
        compute='_compute_total'
    )
    subtotal_without_tax = fields.Float(
        required=False,
        compute='_compute_total',
        readonly=True,
        string='Subtotal'
    )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.product_uom_id = self.product_id.uom_id
            self.name = self.product_id.display_name
        else:
            self.product_id = ''
            self.product_uom_id = ''

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.request_id.partner_id,
            product=self.product_id,
            taxes=self.tax_ids,
            currency=self.request_id.company_id.currency_id,
            price_unit=self.price_unit,
            quantity=self.quantity,
            price_subtotal=self.subtotal_without_tax,
        )

    @api.depends(
        'tax_ids',
        'product_id',
        'price_unit',
        'quantity'
    )
    def _compute_total(self):
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes(
                [line._convert_to_tax_base_line_dict()]
            )
            totals = tax_results['totals']
            amount_untaxed = totals.get(self.request_id.company_id.currency_id, {}).get('amount_untaxed', 0.0)
            amount_tax = totals.get(self.request_id.company_id.currency_id, {}).get('amount_tax', 0.0)
            line.update({
                'subtotal_without_tax': amount_untaxed,
                'price_tax': amount_tax,
                'subtotal': amount_untaxed + amount_tax,
            })


