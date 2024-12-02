# -*- coding: utf-8 -*-
import time
from odoo import api, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportAgedPartnerBalance(models.AbstractModel):
    _name = 'report.cue_reports.pdf_report_templates_purchase'

    total = 0.0

    def get_type(self, order):
        tax_type = []

        for rec in order.order_line:
            for tax in rec.taxes_id:
                if tax.children_tax_ids:
                    for child_tax in tax.children_tax_ids:
                        if child_tax.tax_group_id.name:
                            if child_tax.tax_group_id.name not in tax_type:
                                tax_type.append(str(child_tax.tax_group_id.name))
                        elif 'other' not in tax_type:
                            tax_type.append('other')
                else:
                    if tax.tax_group_id.name:
                        if tax.tax_group_id.name not in tax_type:
                            tax_type.append(str(tax.tax_group_id.name))
                    elif 'other' not in tax_type:
                        tax_type.append('other')
        return tax_type

    def get_tax_total(self, order):
        
        tax_total = {}
        for rec in order.order_line:
            price_unit = rec.price_unit
            for tax in rec.taxes_id:
                if tax.children_tax_ids:
                    for child_tax in tax.children_tax_ids:
                        total = child_tax.compute_all(price_unit,
                                              order.currency_id,
                                              rec.product_qty,
                                              rec.product_id,
                                              order.partner_id)['taxes']
                        tax_type = child_tax.tax_group_id.name
                        for line in total:
                            if tax_type:
                                if tax_type not in tax_total:
                                    tax_total.update({
                                                    str(tax_type): line['amount']
                                                    })
                                else:
                                    tax_total[str(tax_type)] += line['amount']
                            else:
                                if 'other' not in tax_total:
                                    tax_total.update({
                                                str('other'): line['amount']
                                                })
                                else:
                                    tax_total[str('other')] += line['amount']
                else:
                    total = tax.compute_all(price_unit,
                                              order.currency_id,
                                              rec.product_qty,
                                              rec.product_id,
                                              order.partner_id)['taxes']
                    tax_type = tax.tax_group_id.name
                    for line in total:
                        if tax_type:
                            if tax_type not in tax_total:
                                tax_total.update({
                                                str(tax_type): line['amount']
                                                })
                            else:
                                tax_total[str(tax_type)] += line['amount']
                        else:
                            if 'other' not in tax_total:
                                tax_total.update({
                                            str('other'): line['amount']
                                            })
                            else:
                                tax_total[str('other')] += line['amount']
        return tax_total
    
    def get_line_total(self, line):
        invoice = line.order_id
        price_unit = line.price_unit
        for rec in line:
            price_total = line.price_subtotal
            for tax in rec.taxes_id:
                price_total = price_total + ((line.price_subtotal * tax.amount) / 100.0)
        return price_total

    def get_line_tax(self, line):
        invoice = line.order_id
        price_unit = line.price_unit

        line_tax = []
        taxes = line.taxes_id.compute_all(price_unit,
                                          invoice.currency_id,
                                          line.product_qty,
                                          line.product_id,
                                          invoice.partner_id)['taxes']
        tax_dict = {}
        for line in taxes:
            tax = self.env['account.tax'].sudo().browse(line['id'])
            if tax.tax_group_id.name and tax.tax_group_id.name not in tax_dict:
                tax_dict[tax.tax_group_id.name] = {}
            else:
                if 'other' not in tax_dict:
                    tax_dict['other'] = {}
            if tax.tax_group_id.name:
                tax_dict[tax.tax_group_id.name].update({
                    'rate': tax.amount,
                    'amount': line['amount'],
                    'tax_type': tax.tax_group_id.name,
                    'tax_id': tax,
                })
            else:
                tax_dict['other'].update({
                    'rate': tax.amount,
                    'amount': line['amount'],
                    'tax_type': 'other',
                    'tax_id': tax,
                })
        return tax_dict

    def get_lines(self, order):
        lines_by_tax_id = {}
        for line in order.order_line:
            if line.taxes_id:
                if line.taxes_id not in lines_by_tax_id:
                    lines_by_tax_id.update({line.taxes_id: {'lines': [], 'sum': 0.0}})
                lines_by_tax_id[line.product_id.taxes_id]['lines'].append(line)
                lines_by_tax_id[line.product_id.taxes_id]['sum'] += line.price_subtotal
                self.total += line.price_subtotal
        return lines_by_tax_id
    
    def get_amount_in_word(self , invoice):
        val = invoice.currency_id.amount_to_text(int(invoice.amount_total))
        return val
    
    def amount(self, line):
        invoice = line.order_id
        total_amt = 0.0
        final = 0.0
        for rec in line:
            total_amt = (rec.price_unit * rec.product_qty)
            final = final + total_amt
        return final
    
    def total(self, order):
        total_amt = 0.0
        final = 0.0
        for rec in order.order_line:
            total_amt = (rec.price_unit * rec.product_qty)
            final = final + total_amt
        return final

    def get_total(self):
        return self.total

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {
            'get_type' : self.get_type,
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': self.env['purchase.order'].browse(docids),
            'get_lines': self.get_lines,
            'get_line_tax': self.get_line_tax,
            'get_tax_total':self.get_tax_total,
            'amount':self.amount,
            'get_line_total':self.get_line_total,
            'get_amount_in_word': self.get_amount_in_word,
            'total': self.total,
        }
        return docargs


class ReportAgedPartnerBalance(models.AbstractModel):
    _name = 'report.cue_reports.pdf_report_templates_rfq'

    total = 0.0

    def get_type(self, order):
        tax_type = []

        for rec in order.order_line:
            for tax in rec.taxes_id:
                if tax.children_tax_ids:
                    for child_tax in tax.children_tax_ids:
                        if child_tax.tax_group_id.name:
                            if child_tax.tax_group_id.name not in tax_type:
                                tax_type.append(str(child_tax.tax_group_id.name))
                        elif 'other' not in tax_type:
                            tax_type.append('other')
                else:
                    if tax.tax_group_id.name:
                        if tax.tax_group_id.name not in tax_type:
                            tax_type.append(str(tax.tax_group_id.name))
                    elif 'other' not in tax_type:
                        tax_type.append('other')
        return tax_type

    def get_tax_total(self, order):

        tax_total = {}
        for rec in order.order_line:
            price_unit = rec.price_unit
            for tax in rec.taxes_id:
                if tax.children_tax_ids:
                    for child_tax in tax.children_tax_ids:
                        total = child_tax.compute_all(price_unit,
                                                      order.currency_id,
                                                      rec.product_qty,
                                                      rec.product_id,
                                                      order.partner_id)['taxes']
                        tax_type = child_tax.tax_group_id.name
                        for line in total:
                            if tax_type:
                                if tax_type not in tax_total:
                                    tax_total.update({
                                        str(tax_type): line['amount']
                                    })
                                else:
                                    tax_total[str(tax_type)] += line['amount']
                            else:
                                if 'other' not in tax_total:
                                    tax_total.update({
                                        str('other'): line['amount']
                                    })
                                else:
                                    tax_total[str('other')] += line['amount']
                else:
                    total = tax.compute_all(price_unit,
                                            order.currency_id,
                                            rec.product_qty,
                                            rec.product_id,
                                            order.partner_id)['taxes']
                    tax_type = tax.tax_group_id.name
                    for line in total:
                        if tax_type:
                            if tax_type not in tax_total:
                                tax_total.update({
                                    str(tax_type): line['amount']
                                })
                            else:
                                tax_total[str(tax_type)] += line['amount']
                        else:
                            if 'other' not in tax_total:
                                tax_total.update({
                                    str('other'): line['amount']
                                })
                            else:
                                tax_total[str('other')] += line['amount']
        return tax_total

    def get_line_total(self, line):
        invoice = line.order_id
        price_unit = line.price_unit
        for rec in line:
            price_total = line.price_subtotal
            for tax in rec.taxes_id:
                price_total = price_total + ((line.price_subtotal * tax.amount) / 100.0)
        return price_total

    def get_line_tax(self, line):
        invoice = line.order_id
        price_unit = line.price_unit

        line_tax = []
        taxes = line.taxes_id.compute_all(price_unit,
                                          invoice.currency_id,
                                          line.product_qty,
                                          line.product_id,
                                          invoice.partner_id)['taxes']
        tax_dict = {}
        for line in taxes:
            tax = self.env['account.tax'].sudo().browse(line['id'])
            if tax.tax_group_id.name and tax.tax_group_id.name not in tax_dict:
                tax_dict[tax.tax_group_id.name] = {}
            else:
                if 'other' not in tax_dict:
                    tax_dict['other'] = {}
            if tax.tax_group_id.name:
                tax_dict[tax.tax_group_id.name].update({
                    'rate': tax.amount,
                    'amount': line['amount'],
                    'tax_type': tax.tax_group_id.name,
                    'tax_id': tax,
                })
            else:
                tax_dict['other'].update({
                    'rate': tax.amount,
                    'amount': line['amount'],
                    'tax_type': 'other',
                    'tax_id': tax,
                })
        return tax_dict

    def get_lines(self, order):
        lines_by_tax_id = {}
        for line in order.order_line:
            if line.taxes_id:
                if line.taxes_id not in lines_by_tax_id:
                    lines_by_tax_id.update({line.taxes_id: {'lines': [], 'sum': 0.0}})
                lines_by_tax_id[line.product_id.taxes_id]['lines'].append(line)
                lines_by_tax_id[line.product_id.taxes_id]['sum'] += line.price_subtotal
                self.total += line.price_subtotal
        return lines_by_tax_id

    def get_amount_in_word(self, invoice):
        val = invoice.currency_id.amount_to_text(int(invoice.amount_total))
        return val

    def amount(self, line):
        invoice = line.order_id
        total_amt = 0.0
        final = 0.0
        for rec in line:
            total_amt = (rec.price_unit * rec.product_qty)
            final = final + total_amt
        return final

    def total(self, order):
        total_amt = 0.0
        final = 0.0
        for rec in order.order_line:
            total_amt = (rec.price_unit * rec.product_qty)
            final = final + total_amt
        return final

    def get_total(self):
        return self.total

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {
            'get_type': self.get_type,
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': self.env['purchase.order'].browse(docids),
            'get_lines': self.get_lines,
            'get_line_tax': self.get_line_tax,
            'get_tax_total': self.get_tax_total,
            'amount': self.amount,
            'get_line_total': self.get_line_total,
            'get_amount_in_word': self.get_amount_in_word,
            'total': self.total,
        }
        return docargs