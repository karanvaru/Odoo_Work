# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class JobInvoiceLine(models.Model):
    _name = "job.invoice.line"
    _description = 'Job Invoice Line'

    #@api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'task_id.partner_id', 'task_id.custom_currency_id')
    def _compute_price(self):
        for rec in self:
            rec.tax_amount = 0.0
            currency = rec.task_id and rec.task_id.custom_currency_id or None
            price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
            taxes = False
            if rec.invoice_line_tax_ids:
                taxes = rec.invoice_line_tax_ids.compute_all(price, currency, rec.quantity, product=rec.product_id, partner=rec.task_id.partner_id)
            if taxes:
                for taxe in taxes['taxes']:
                    rec.tax_amount += taxe['amount']
            rec.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else rec.quantity * price
            #rec.price_total = taxes['total_included'] if taxes else rec.price_subtotal
            if rec.task_id.custom_currency_id and rec.task_id.custom_currency_id != rec.task_id.company_id.currency_id:
                price_subtotal_signed = rec.task_id.custom_currency_id.with_context(date=rec.task_id.create_date).compute(price_subtotal_signed, rec.task_id.company_id.currency_id)
            
    #@api.one
    @api.depends('invoice_id')
    def _compute_invoice(self):
        for rec in self:
            if not rec.invoice_id or rec.invoice_id.state == 'cancel':
                rec.is_invoice = False
            else:
                rec.is_invoice = True
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.price_unit = self.product_id.lst_price
        self.uom_id = self.product_id.uom_id.id
        
        company = self.task_id.company_id
        product = self.product_id
#        invoice_line_obj = self.env['account.invoice.line']
        invoice_line_obj = self.env['account.move.line']
#        account = invoice_line_obj.get_invoice_line_account(type='out_invoice', product=product, fpos=None, company=company)
        account = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=None)['income']
        if account:
           self.account_id = account.id

    is_invoice = fields.Boolean(
        string="Is Invoice",
        compute='_compute_invoice',
        store=True,   
    )
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )
    account_id = fields.Many2one(
        'account.account',
        string="Account",
        required=True,
    )
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account'
    )
#    analytic_tag_ids = fields.Many2many(
#        'account.analytic.tag',
#        string='Analytic Tags'
#    )
    quantity = fields.Float(
        string='Quantity',
        #digits=dp.get_precision('Product Unit of Measure'),
        digits='Product Unit of Measure',
        required=True,
        default=1
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        ondelete='set null',
        index=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True,
        #digits=dp.get_precision('Product Price')
        digits='Product Price'
    )
    discount = fields.Float(
        string='Discount (%)',
        #digits=dp.get_precision('Discount'),
        digits='Discount',
        default=0.0
    )
    invoice_line_tax_ids = fields.Many2many(
        'account.tax',
        'job_invoice_line_tax',
        'invoice_line_id',
        'tax_id',
        string='Taxes',
    )
    task_id = fields.Many2one(
        'project.task',
        string="Task"
    )
    tax_amount = fields.Float(
        string='Tax Amount',
        store=True,
        readonly=True,
        compute='_compute_price',
        help="Total tax amount"
    )
    price_subtotal = fields.Float(
        string='Amount',
        store=True,
        readonly=True,
        compute='_compute_price',
        help="Total amount without taxes"
    )
    invoice_id = fields.Many2one(
#        'account.invoice',
        'account.move',
        string='Invoice',
    )

