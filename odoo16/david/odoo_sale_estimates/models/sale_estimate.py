# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from collections import defaultdict



class SaleEstimate(models.Model):
    _name = "sale.estimate"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Sales Estimate"
    _rec_name = 'number'
    _order = 'id desc'
    
    number = fields.Char(
        'Number',
        copy=False,
    )
    estimate_date = fields.Date(
        'Date',
        copy=False,
        default = fields.date.today(),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.user.company_id,
        string='Company',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Estimate Sent'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('quotesend', 'Quotation Created'),
        ('cancel', 'Cancelled')],
        default='draft',
        tracking=True,
        copy='False',
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', 
        string='Pricelist', 
        required=True, 
        help="Pricelist for current sales estimate."
    )
    payment_term_id = fields.Many2one(
        'account.payment.term', 
        string='Payment Terms', 
        #oldname='payment_term'
    )
    description = fields.Text(
        string='Description of Work'
    )
    note = fields.Text(
        string='Note'
    )
    currency_id = fields.Many2one(
        "res.currency", 
        related='pricelist_id.currency_id', 
        string="Currency", 
        readonly=True, 
        #required=True,
        store=True,
    )
    estimate_ids = fields.One2many(
        'sale.estimate.line',
        'estimate_id',
        'Estimate Lines',
    )
    reference = fields.Char(
        string='Customer Reference'
    )
    source = fields.Char(
        string='Source Document'
    )
    total = fields.Float(
        compute='_compute_totalestimate', 
        string='Total Estimate', 
        store=True
    )
    user_id = fields.Many2one(
        'res.users',
        'Sales Person',
        default=lambda self: self.env.user,
    )
    team_id = fields.Many2one(
        'crm.team',
        'Sales Team',
    )
    quotation_id = fields.Many2one(
        'sale.order',
        'Sales Quotation',
        readonly=True,
        copy=False,
    )

    def view_custom_quotation(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sale.action_quotations_with_onboarding')
        action['domain'] = [('id','=',self.quotation_id.id)]
        return action
    
    @api.depends('estimate_ids.price_subtotal')
    def _compute_totalestimate(self):
        for rec in self:
            rec.total = 0
            for line in rec.estimate_ids:
                rec.total += line.price_subtotal
        
    @api.onchange('partner_id')
    def _onchange_customer_id(self):
        for rec in self:
            partner = self.env['res.partner'].browse(rec.partner_id.id)
            rec.pricelist_id = partner.property_product_pricelist.id
            rec.payment_term_id = partner.property_payment_term_id.id
            
    # @api.multi
    def estimate_send(self):
        for rec in self:
            rec.state = 'sent'
            
    # @api.multi
    def estimate_confirm(self):
        for rec in self:
            if not rec.estimate_ids:
                raise UserError(_('Please enter Estimation Lines!'))
            rec.state = 'confirm'
            
    # @api.multi
    def estimate_approve(self):
        for rec in self:
            rec.state = 'approve'
            
    # @api.multi
    def estimate_quotesend(self):
        for rec in self:
            rec.state = 'quotesend'
            
    # @api.multi
    def estimate_cancel(self):
        for rec in self:
            rec.state = 'cancel'
        
    # @api.multi
    def estimate_reject(self):
        for rec in self:
            rec.state = 'reject'
            
    # @api.multi
    def reset_todraft(self):
        for rec in self:
            rec.state = 'draft'
            
    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('product.estimate.seq')
        vals.update({
            'number': number
            })
        res = super(SaleEstimate, self).create(vals)
        return res
        
    # @api.multi
    def action_estimate_send(self):
        if self.state == 'sent' or self.state == 'approve' or self.state == 'quotesend' or self.state == 'confirm':
            '''
            This function opens a window to compose an email, with the edi sale template message loaded by default
            '''
            #self.state = 'sent'
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data._xmlid_to_res_id('odoo_sale_estimates.email_template_estimate', raise_if_not_found=False)
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data._xmlid_to_res_id('odoo_sale_estimates.email_compose_message_wizard_form', raise_if_not_found=False)
            except ValueError:
                compose_form_id = False
            ctx = dict()
            ctx.update({
                'default_model': 'sale.estimate',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                #'custom_layout': "sale.mail_template_data_notification_email_sale_order"
            })
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
        if self.state == 'draft':
            '''
            This function opens a window to compose an email, with the edi sale template message loaded by default
            '''
            self.state = 'sent'
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                # template_id = ir_model_data.get_object_reference('odoo_sale_estimates', 'email_template_estimate')[1]
                template_id = ir_model_data._xmlid_to_res_id('odoo_sale_estimates.email_template_estimate',raise_if_not_found=False)
            except ValueError:
                template_id = False
            try:
                # compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
                compose_form_id = ir_model_data._xmlid_to_res_id('mail.email_compose_message_wizard_form',raise_if_not_found=False)
            except ValueError:
                compose_form_id = False
            ctx = dict()
            ctx.update({
                'default_model': 'sale.estimate',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                #'custom_layout': "sale.mail_template_data_notification_email_sale_order"
            })
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
        
    # @api.multi
    def _prepare_quotation_line(self,quotation):
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            for line in rec.estimate_ids:
                vals1 = {
                                'product_id':  line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit' : line.price_unit,
                                'price_subtotal': line.price_subtotal,
                                'name' : line.product_description,
                                'price_total' : self.total,
                                'discount' : line.discount,
                                # 'estimate_id':quotation.id,
                                'order_id':quotation.id
                                }
                quo_line = quo_line_obj.create(vals1)
        
    # @api.multi
    def estimate_to_quotation(self):
        quo_obj = self.env['sale.order']
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            vals = {
                'partner_id':rec.partner_id.id,
                'origin': rec.number,
                }
            quotation = quo_obj.create(vals)
            rec._prepare_quotation_line(quotation)
            rec.quotation_id = quotation.id
        rec.state = 'quotesend'
        action = self.env['ir.actions.act_window']._for_xml_id('sale.action_quotations_with_onboarding')
        action['domain'] = [('id','=',rec.quotation_id.id)]
        return action
            
class SaleEstimateline(models.Model):
    _name = "sale.estimate.line"
    _description = 'Sales Estimate Line'
    
    @api.depends('price_unit','product_uom_qty','discount')
    def _compute_amount(self):
        for rec in self:
            if rec.discount:
                disc_amount = (rec.price_unit * rec.product_uom_qty) * rec.discount / 100
                rec.price_subtotal = (rec.price_unit * rec.product_uom_qty) - disc_amount
            else:
                rec.price_subtotal = rec.price_unit * rec.product_uom_qty
            
    estimate_id = fields.Many2one(
        'sale.estimate',
        string='Sale Estimate', 
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    product_uom_qty = fields.Float(
        string='Quantity', 
        #digits=dp.get_precision('Product Unit of Measure'), 
        digits='Product Unit of Measure',
        required=True, 
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom', #product.uom
        string='Unit of Measure', 
        required=True
    )
    price_unit = fields.Float(
        'Unit Price', 
        required=True, 
        #digits=dp.get_precision('Product Price'),
        digits='Product Price',
        default=0.0
    )
    price_subtotal = fields.Float(
        compute='_compute_amount', 
        string='Subtotal', 
        store=True
    )
    product_description = fields.Char(
        string='Description'
    )
    discount = fields.Float(
        string='Discount (%)'
    )
    company_id = fields.Many2one(related='estimate_id.company_id', string='Company', store=True, readonly=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])


    def _get_custom_pricelist_item_id(self):
        for line in self:
            if not line.product_id:
                price = 0.0
            else:
                if not line.product_id or not line.estimate_id.pricelist_id:
                    pricelist_item_id = False
                else:
                    pricelist_item_id = line.estimate_id.pricelist_id._get_product_rule(
                        line.product_id,
                        line.product_uom_qty or 1.0,
                        uom=line.product_uom,
                        date=line.estimate_id.estimate_date,
                    )

                pricelist_item = pricelist_item_id

                pricelist_rule = self.env['product.pricelist.item'].browse(pricelist_item)
                order_date = line.estimate_id.estimate_date or fields.Date.today()
                product = line.product_id
                qty = line.product_uom_qty or 1.0
                uom = line.product_uom or line.product_id.uom_id

                price = pricelist_rule._compute_price(
                    # product, qty, uom, order_date, currency=self.currency_id)
                    product, qty, uom, order_date, currency=line.estimate_id.pricelist_id.currency_id)
        return price

    @api.depends('product_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['sale.estimate.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for product in self.product_id:
            for tax in product.taxes_id:
                taxes_by_product_company[(product, tax.company_id)] += tax
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = taxes_by_product_company[(line.product_id, company)]
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = self.env['account.fiscal.position']._get_fiscal_position(line.estimate_id.partner_id)
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result

    @api.onchange('product_id')
    def custom_product_id_change(self):
        for line in self:
            line.product_uom = line.product_id.uom_id
            
            line.product_description = line.product_id.display_name
            if line.product_id.description_sale:
                line.product_description += '\n' + line.product_id.description_sale
            self._compute_tax_id()
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if not line.product_uom or not line.product_id or not line.estimate_id.pricelist_id:
                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price()
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.estimate_id.currency_id,
                    line.estimate_id.estimate_date,
                    'sale',
                    fiscal_position=self.env['account.fiscal.position']._get_fiscal_position(line.estimate_id.partner_id),
                    product_price_unit=price,
                    product_currency=line.estimate_id.currency_id
                )

    @api.onchange('product_id')
    def custom_onchange_product_id_warning(self):
        if not self.product_id:
            return

        product = self.product_id
        if product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False

            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }

    def _get_display_price(self):
        """Compute the displayed unit price for a given line.

        Overridden in custom flows:
        * where the price is not specified by the pricelist
        * where the discount is not specified by the pricelist

        Note: self.ensure_one()
        """
        self.ensure_one()

        pricelist_price = self._get_custom_pricelist_item_id()

        if self.estimate_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    def _get_pricelist_price_before_discount(self):
        """Compute the price used as base for the pricelist price computation.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        for line in self:
            if not line.product_id:
                price = 0.0
            else:
                order_date = line.estimate_id.estimate_date or fields.Date.today()
                product = line.product_id
                qty = line.product_uom_qty or 1.0
                uom = line.product_uom

                if not line.product_id or not line.estimate_id.pricelist_id:
                    pricelist_item_id = False
                else:
                    pricelist_item_id = line.estimate_id.pricelist_id._get_product_rule(
                        line.product_id,
                        line.product_uom_qty or 1.0,
                        uom=line.product_uom,
                        date=line.estimate_id.estimate_date,
                    )

                pricelist_rule = self.env['product.pricelist.item'].browse(pricelist_item_id)
                if pricelist_rule:
                    pricelist_item = pricelist_rule
                    if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                        # Find the lowest pricelist rule whose pricelist is configured
                        # to show the discount to the customer.
                        while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                            rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                                product, qty, uom=uom, date=order_date)
                            pricelist_item = self.env['product.pricelist.item'].browse(rule_id)

                    pricelist_rule = pricelist_item

                price = pricelist_rule._compute_base_price(
                    product,
                    qty,
                    uom,
                    order_date,
                    target_currency=self.estimate_id.currency_id,
                )

        return price

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def custom_onchange_discount(self):
        for line in self:
            if not line.product_id:
                line.discount = 0.0

            if not (
                line.estimate_id.pricelist_id
                and line.estimate_id.pricelist_id.discount_policy == 'without_discount'
            ):
                continue

            line.discount = 0.0

            line = line.with_company(line.company_id)
            pricelist_price = line._get_custom_pricelist_item_id()
            base_price = line._get_pricelist_price_before_discount()

            if base_price != 0:  # Avoid division by zero
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                    # only show negative discounts if price is negative
                    # otherwise it's a surcharge which shouldn't be shown to the customer
                    line.discount = discount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
