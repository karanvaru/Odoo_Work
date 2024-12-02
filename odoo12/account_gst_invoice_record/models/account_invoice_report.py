from odoo import fields,models,api,_

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    @api.depends('tax_line_ids')
    def compute_gst_taxes_invoice(self):
        for rec in self:
            sgst_total = 0
            cgst_total = 0
            igst_total = 0
            tds_total= 0
            for tax in rec.tax_line_ids:
                if 'SGST' in tax.name:
                    sgst_total = sgst_total + tax.amount_total
                if 'CGST' in tax.name:
                    cgst_total = cgst_total + tax.amount_total
                if 'IGST' in tax.name:
                    igst_total = igst_total + tax.amount_total
                if tax.tax_id.tax_group_id.name == 'TDS':
                    tds_total += tax.amount


            rec.sgst = sgst_total
            rec.cgst = cgst_total
            rec.igst = igst_total
            rec.tds  = tds_total
            rec.total_tax = rec.sgst + rec.cgst + rec.igst

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
        related='date_invoice',
        store=True,
    )
    sgst = fields.Float(
        string='SGST',
        compute='compute_gst_taxes_invoice',
        store=True
    )
    cgst = fields.Float(
        string='CGST',
        compute='compute_gst_taxes_invoice',
        store=True
    )
    igst = fields.Float(
        string='IGST',
        compute='compute_gst_taxes_invoice',
        store=True

    )
    tds = fields.Monetary(
        string='TDS',
        compute='compute_gst_taxes_invoice',
        store=True

    )

    invoice_value = fields.Monetary(
        string='Invoice Value',
        related='amount_total',
        store=True
    )
    vendor_reference_no = fields.Char(
        string='Vendor Reference No',
    )
    invoice_state = fields.Selection(
        related="state",
        string="Invoice Line state"
    )
    journal_id_report = fields.Many2one(
        'account.journal',
        string="Journal",
        related="journal_id",
    )
    move_id_report = fields.Many2one(
        'account.move',
        string='Journal Entry',
        related='move_id',
    )

    total_tax = fields.Monetary(
        string='Total Tax Amount',
        store=True,
        compute='compute_gst_taxes_invoice',
        related="amount_tax"
    )

    invoice_line_tax = fields.Many2many(string="Taxes", related='invoice_line_ids.invoice_line_tax_ids')

