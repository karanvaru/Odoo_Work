# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class SaleEstimate(models.Model):
    _name = "sale.estimate"
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
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
                                'order_id':quotation.id,
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

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = self.env['account.fiscal.position'].get_fiscal_position(line.estimate_id.partner_id.id)
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes)
            

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.estimate_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.estimate_id.pricelist_id.id,  uom=self.product_uom.id).price
        product_context = dict(self.env.context, partner_id=self.estimate_id.partner_id.id, date=self.estimate_id.estimate_date, uom=self.product_uom.id)#

        final_price, rule_id = self.estimate_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.estimate_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, 
            self.product_uom, self.estimate_id.pricelist_id.id)
        if currency != self.estimate_id.pricelist_id.currency_id: #
            base_price = currency._convert(
                base_price, self.estimate_id.pricelist_id.currency_id,
                self.estimate_id.company_id or self.env.company, self.estimate_id.estimate_date or fields.Date.today()) #
        return max(base_price, final_price)

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            partner=self.estimate_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.estimate_id.estimate_date,
            pricelist=self.estimate_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['product_description'] = name

        self._compute_tax_id()

        if self.estimate_id.pricelist_id and self.estimate_id.partner_id:
            vals['price_unit'] = product._get_tax_included_unit_price(
                self.company_id,
                self.estimate_id.currency_id,
                self.estimate_id.estimate_date,
                'sale',
                product_price_unit=self._get_display_price(product),
                product_currency=self.estimate_id.currency_id
            )

        # if self.estimate_id.pricelist_id and self.estimate_id.partner_id:
        #     vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
        self.update(vals)

        title = False
        message = False
        warning = {}

        product = self.product_id
        if product and product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    _price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.estimate_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.company_id or self.env.company, self.estimate_id.estimate_date or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_uom and
                self.estimate_id.partner_id and self.estimate_id.pricelist_id and
                self.estimate_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.estimate_id.partner_id.lang,
            partner=self.estimate_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.estimate_id.estimate_date,
            pricelist=self.estimate_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.estimate_id.partner_id.id, date=self.estimate_id.estimate_date, uom=self.product_uom.id)

        price, rule_id = self.estimate_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.estimate_id.partner_id)
        new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.estimate_id.pricelist_id.id)

        if new_list_price != 0:
            if self.estimate_id.pricelist_id.currency_id != currency:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = currency._convert(
                    new_list_price, self.estimate_id.pricelist_id.currency_id,
                    self.estimate_id.company_id or self.env.company, self.estimate_id.estimate_date or fields.Date.today())
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
                self.discount = discount

    # @api.multi
    # @api.onchange('product_id')
    # def product_id_change(self):
    #     if not self.product_id:
    #         return {'domain': {'product_uom': []}}

    #     vals = {}
    #     domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
    #     if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
    #         vals['product_uom'] = self.product_id.uom_id
    #         vals['product_uom_qty'] = 1.0

    #     product = self.product_id.with_context(
    #         lang=self.estimate_id.partner_id.lang,
    #         partner=self.estimate_id.partner_id.id,
    #         quantity=vals.get('product_uom_qty') or self.product_uom_qty,
    #         date=self.estimate_id.estimate_date,
    #         pricelist=self.estimate_id.pricelist_id.id,
    #         uom=self.product_uom.id
    #     )

    #     name = product.name_get()[0][1]
    #     if product.description_sale:
    #         name += '\n' + product.description_sale
    #     vals['product_description'] = name

    #     self._compute_tax_id()

    #     if self.estimate_id.pricelist_id and self.estimate_id.partner_id:
    #         vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
    #     self.update(vals)

    #     title = False
    #     message = False
    #     warning = {}
    #     if product.sale_line_warn != 'no-message':
    #         title = _("Warning for %s") % product.name
    #         message = product.sale_line_warn_msg
    #         warning['title'] = title
    #         warning['message'] = message
    #         if product.sale_line_warn == 'block':
    #             self.product_id = False
    #         return {'warning': warning}
    #     return {'domain': domain}

    # @api.multi
    # def _compute_tax_id(self):
    #     for line in self:
    #         fpos = line.estimate_id.partner_id.property_account_position_id
    #         # If company_id is set, always filter taxes by the company
    #         taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
    #         line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes

    
    # @api.multi
    # def _get_display_price(self, product):
    #     if self.estimate_id.pricelist_id.discount_policy == 'without_discount':
    #         from_currency = self.estimate_id.company_id.currency_id
    #         return from_currency.compute(product.lst_price, self.estimate_id.pricelist_id.currency_id)
    #     return product.with_context(pricelist=self.estimate_id.pricelist_id.id).price
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
