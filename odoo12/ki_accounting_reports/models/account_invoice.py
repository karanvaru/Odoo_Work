# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    @api.depends('tax_line_ids')
    def compute_gst_taxes_invoice(self):
        for rec in self:
            sgst_total = 0
            cgst_total = 0
            igst_total = 0
            tds_total = 0
            for tax in rec.tax_line_ids:
                if 'SGST' in tax.name:
                    sgst_total = sgst_total + tax.amount_total
                if 'CGST' in tax.name:
                    cgst_total = cgst_total + tax.amount_total
                if 'IGST' in tax.name:
                    igst_total = igst_total + tax.amount_total
                if tax.tax_id.tax_group_id.name == 'TDS':
                    tds_total += tax.amount
            rec.tds = tds_total
            if rec.amount_total_signed < 0:
                rec.sgst = -sgst_total
                rec.cgst = -cgst_total
                rec.igst = -igst_total
                rec.total_tax = rec.sgst + rec.cgst + rec.igst
            else:
                rec.sgst = sgst_total
                rec.cgst = cgst_total
                rec.igst = igst_total
                rec.total_tax = rec.sgst + rec.cgst + rec.igst
