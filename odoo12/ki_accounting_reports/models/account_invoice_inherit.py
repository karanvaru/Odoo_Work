# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'

    company_gst_no = fields.Char(
        string='Company GST',
        related='company_id.vat'
    )
    partner_gst_no = fields.Char(
        string='Partner GST',
        related='partner_id.vat',
    )
    date = fields.Date(
        string='Date',
        related='invoice_id.date_invoice',
        store=True,
    )
    sgst = fields.Float(
        string='SGST',
        compute='_compute_gst_taxes',
        store=True
    )
    cgst = fields.Float(
        string='CGST',
        compute='_compute_gst_taxes',
        store=True
    )
    igst = fields.Float(
        string='IGST',
        compute='_compute_gst_taxes',
        store=True
    )
    hsn_code = fields.Char(
        string='HSN Code',
        related='product_id.l10n_in_hsn_code',
        store=True
    )
    invoice_value = fields.Monetary(
        string='Invoice Value',
        related='invoice_id.amount_total',
        store=True
    )
    vendor_reference_no = fields.Char(
        string='Vendor Reference No',
    )
    invoice_line_state = fields.Selection(
        related="invoice_id.state",
        string="Invoice Line state"
    )
    journal_id = fields.Many2one(
        'account.journal',
        string="Journal",
        related="invoice_id.journal_id",
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        related='invoice_id.move_id',
    )
    transaction_type = fields.Selection(
        related='invoice_id.type',
        string='Transaction Type',
        store=True,
    )
    total_tax = fields.Monetary(
        string='Total Tax Amount',
        compute='_compute_gst_taxes',
        store=True,
    )

    categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        compute='get_product_categ'
    )

    price_total_signed = fields.Float(
        string='Price Total Signed',
        compute='_compute_price',
        store=True
    )
    price_subtotal_signed = fields.Float(
        string='Price SubTotal Signed',
        compute='_compute_price',
        store=True
    )

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'price_subtotal')
    def _compute_price(self):
        res = super(AccountInvoiceLineInherit, self)._compute_price()
        for rec in self:
            sign = rec.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            rec.price_total_signed = rec.price_total * sign
            if rec.price_total_signed < 0:
                rec.price_subtotal_signed = rec.price_subtotal * sign
            else:
                rec.price_subtotal_signed = rec.price_subtotal
        return res

    @api.depends('invoice_line_tax_ids', 'quantity', 'product_id', 'price_unit', 'price_total')
    def _compute_gst_taxes(self):
        for rec in self:
            if rec.invoice_line_tax_ids:
                currency = rec.invoice_id and rec.invoice_id.currency_id or None
                price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
                taxes = rec.invoice_line_tax_ids.compute_all(price, currency, rec.quantity, product=rec.product_id,
                                                             partner=rec.invoice_id.partner_id)
                igst_total = 0
                cgst_total = 0
                sgst_total = 0
                for all_taxes in taxes['taxes']:
                    res = self.env['account.tax'].browse(all_taxes['id'])
                    if res.tax_group_id.name == 'IGST':
                        igst_total = igst_total + all_taxes['amount']
                    elif res.tax_group_id.name == 'SGST':
                        sgst_total = sgst_total + all_taxes['amount']
                    elif res.tax_group_id.name == 'CGST':
                        cgst_total = cgst_total + all_taxes['amount']
                if rec.price_total_signed < 0:
                    rec.igst = -igst_total
                    rec.sgst = -sgst_total
                    rec.cgst = -cgst_total
                    rec.total_tax = rec.sgst + rec.cgst + rec.igst
                else:
                    rec.igst = igst_total
                    rec.sgst = sgst_total
                    rec.cgst = cgst_total
                    rec.total_tax = rec.sgst + rec.cgst + rec.igst

    @api.multi
    def action_invoice_button(self):
        # act = self.env.ref('account.action_invoice_tree1').read([])[0]
        # act['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        # act['domain'] = [('id', '=', self.invoice_id.id)]
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        form_view = [(self.env.ref('account.invoice_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.invoice_id.id

        return action

    @api.depends('product_id')
    def get_product_categ(self):
        for rec in self:
            rec.categ_id = rec.product_id.categ_id
