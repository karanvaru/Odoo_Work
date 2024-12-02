##############################################################################

from odoo import fields, models, api, _


class SaleEstimateInherit(models.Model):
    _inherit = 'sale.estimate'

    category_type = fields.Selection(
        selection=[
            ('rental', 'Rental'),
            ('service', 'Service'),
            ('parts', 'Parts'),
            ('sale', 'Sales')
        ],
        string='Category Type',
    )
    tax_totals = fields.Binary(
        compute='_compute_tax_totals'
    )
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True,
                                   # compute='_compute_amounts',
                                   tracking=4)

    @api.depends('estimate_ids.price_subtotal', 'estimate_ids.price_tax', 'estimate_ids.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order_lines = order.estimate_ids.filtered(lambda x: not x.display_type)

            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(order_lines.mapped('price_subtotal'))
                amount_tax = sum(order_lines.mapped('price_tax'))

            order.total = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.total + order.amount_tax


    @api.depends_context('lang')
    @api.depends('estimate_ids.tax_id', 'estimate_ids.price_unit', 'amount_total', 'total', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            estimate_id = order.estimate_ids.filtered(lambda x: not x.display_type)
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in estimate_id],
                order.currency_id or order.company_id.currency_id,
            )



    def estimate_to_quotation(self):
        quo_obj = self.env['sale.order']
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            vals = {
                'partner_id': rec.partner_id.id,
                'origin': rec.number,
                'category_type': rec.category_type
            }
            quotation = quo_obj.create(vals)
            rec._prepare_quotation_line(quotation)
            rec.quotation_id = quotation.id
        rec.state = 'quotesend'
        action = self.env['ir.actions.act_window']._for_xml_id('sale.action_quotations_with_onboarding')
        action['domain'] = [('id', '=', rec.quotation_id.id)]
        return action

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        sequence = False
        if 'category_type' in vals:
            sequence = self.env['quote.sequence.mapping'].search([('category_type', '=', vals['category_type'])],
                                                                 limit=1)
        if sequence and sequence.estimate_sequence_id:
            vals['number'] = sequence.estimate_sequence_id.next_by_id()
        elif vals.get('number', _("New")) == _("New"):
            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(
                vals.get('estimate_date'))) if 'estimate_date' in vals else None
            vals['number'] = self.env['ir.sequence'].next_by_code('product.estimate.seq', sequence_date=seq_date) or _("New")

        return super(models.Model, self).create(vals)
        SaleEstimate = models.getModel('sale.estimate')
        SaleEstimate.create = create
