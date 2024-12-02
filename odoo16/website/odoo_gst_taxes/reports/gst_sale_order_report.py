# -*- coding: utf-8 -*-
import time
from odoo import api, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportAgedPartnerBalance(models.AbstractModel):
    _name = 'report.ki_gst_taxes.sale_order_report_view'

    def get_type(self, invoice):
        tax_type = []

        for rec in invoice.invoice_line_ids:
            for tax in rec.tax_ids:
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

    def get_tax_total(self, invoice):
        tax_total = {}

        for rec in invoice.invoice_line_ids:
            for tax in rec.tax_ids:
                if tax.children_tax_ids:
                    for child_tax in tax.children_tax_ids:
                        taxes = child_tax.compute_all(rec.price_unit, rec.currency_id, rec.quantity, \
                            product=rec.product_id, partner=rec.move_id.partner_shipping_id)
                        tax_type = child_tax.tax_group_id.name and child_tax.tax_group_id.name or 'other'
                        if tax_type not in tax_total:
                            tax_total.update({
                                tax_type: taxes['taxes'][0]['amount']
                            })
                        else:
                            tax_total[tax_type] += taxes['taxes'][0]['amount']
                else:
                    taxes = tax.compute_all(rec.price_unit, rec.currency_id, rec.quantity, \
                        product=rec.product_id, partner=rec.move_id.partner_shipping_id)
                    tax_type = tax.tax_group_id.name and tax.tax_group_id.name or 'other'
                    if tax_type not in tax_total:
                        tax_total.update({
                            tax_type: taxes['taxes'][0]['amount']
                        })
                    else:
                        tax_total[tax_type] += taxes['taxes'][0]['amount']
        return tax_total
    
    def get_line_total(self, line):
        invoice = line.move_id
        price_total = 0.0
        for rec in line:
            price_total = line.price_subtotal
            for tax in rec.tax_ids:
                price_total = price_total + ((line.price_subtotal * tax.amount) / 100.0)
        return price_total

    def get_line_tax(self, line):
        invoice = line.move_id
        price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        
        line_tax = []
        taxes = line.tax_ids.compute_all(price_unit,
                                        invoice.currency_id,
                                        line.quantity,
                                        line.product_id,
                                        invoice.partner_id)['taxes']                                
        tax_dict = {}
        for line in taxes:
            tax = self.env['account.tax'].sudo().browse(line['id'])
            tax_type = tax.tax_group_id.name and tax.tax_group_id.name or 'other'
            if tax_type not in tax_dict:
                tax_dict[tax_type] = {}
            tax_dict[tax_type].update({
                'rate': tax.amount,
                'amount': line['amount'],
                'tax_type': tax_type,
                'tax_id': tax.name,
            })
        return tax_dict

    def get_lines(self, order):
        lines_by_tax_id = {}
        for line in order.order_line:
            if line.tax_ids:
                if line.tax_ids not in lines_by_tax_id:
                    lines_by_tax_id.update({line.tax_ids: {'lines': [], 'sum': 0.0}})
                lines_by_tax_id[line.product_id.tax_id]['lines'].append(line)
                lines_by_tax_id[line.product_id.tax_id]['sum'] += line.price_subtotal
                self.total += line.price_subtotal
        return lines_by_tax_id
    
    def get_amount_in_word(self , invoice):
        if invoice:
            val = invoice.currency_id.amount_to_text(int(invoice.amount_total))
            return val
        else:
            return ''

    def amount(self, line):
        invoice = line.move_id
        total_amt = 0.0
        for rec in line:
            total_amt = (rec.price_unit * rec.quantity)
        return total_amt

    def total_disc(self, order):
        total_amt = 0.0
        final = 0.0
        for rec in order.invoice_line_ids:
            total_amt = (rec.price_unit * rec.quantity)
            final = final + total_amt
        return final

    def get_total(self):
        return self.total    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {
            'get_type' : self.get_type,
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': self.env['sale.order'].browse(docids),
            'get_lines': self.get_lines,
            'get_line_tax': self.get_line_tax,
            'get_tax_total':self.get_tax_total,
            'amount':self.amount,
            'total_disc':self.total_disc,
            'get_line_total':self.get_line_total,
            'get_amount_in_word': self.get_amount_in_word,
        }
        return docargs

    # total = 0.0

    # def get_type(self, order):
    #     tax_type = []

    #     for rec in order.order_line:
    #         for tax in rec.tax_id:
    #             if tax.children_tax_ids:
    #                 for child_tax in tax.children_tax_ids:
    #                     if child_tax.tax_group_id.name:
    #                         if child_tax.tax_group_id.name not in tax_type:
    #                             tax_type.append(str(child_tax.tax_group_id.name))
    #                     elif 'other' not in tax_type:
    #                         tax_type.append('other')
    #             else:
    #                 if tax.tax_group_id.name:
    #                     if tax.tax_group_id.name not in tax_type:
    #                         tax_type.append(str(tax.tax_group_id.name))
    #                 elif 'other' not in tax_type:
    #                     tax_type.append('other')
    #     return tax_type

    # def get_tax_total(self, order):
    #     tax_total = {}
        
    #     for rec in order.order_line:
    #         price_unit = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
    #         for tax in rec.tax_id:
    #             if tax.children_tax_ids:
    #                 for child_tax in tax.children_tax_ids:
    #                     total = child_tax.compute_all(price_unit,
    #                                           order.currency_id,
    #                                           rec.product_uom_qty,
    #                                           rec.product_id,
    #                                           order.partner_id)['taxes']
    #                     tax_type = child_tax.tax_group_id.name
    #                     for line in total:
    #                         if tax_type:
    #                             if tax_type not in tax_total:
    #                                 tax_total.update({
    #                                                 str(tax_type): line['amount']
    #                                                 })
    #                             else:
    #                                 tax_total[str(tax_type)] += line['amount']
    #                         else:
    #                             if 'other' not in tax_total:
    #                                 tax_total.update({
    #                                             str('other'): line['amount']
    #                                             })
    #                             else:
    #                                 tax_total[str('other')] += line['amount']
    #             else:
    #                 total = tax.compute_all(price_unit,
    #                                           order.currency_id,
    #                                           rec.product_uom_qty,
    #                                           rec.product_id,
    #                                           order.partner_id)['taxes']
    #                 tax_type = tax.tax_group_id.name
    #                 for line in total:
    #                     if tax_type:
    #                         if tax_type not in tax_total:
    #                             tax_total.update({
    #                                             str(tax_type): line['amount']
    #                                             })
    #                         else:
    #                             tax_total[str(tax_type)] += line['amount']
    #                     else:
    #                         if 'other' not in tax_total:
    #                             tax_total.update({
    #                                         str('other'): line['amount']
    #                                         })
    #                         else:
    #                             tax_total[str('other')] += line['amount']
    #     return tax_total
    
    # def get_line_total(self, line):
    #     invoice = line.order_id
    #     price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #     for rec in line:
    #         price_total = line.price_subtotal
    #         for tax in rec.tax_id:
    #             price_total = price_total + ((line.price_subtotal * tax.amount) / 100.0)
    #     return price_total

    # def get_line_tax(self, line):
    #     invoice = line.order_id
    #     price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

    #     line_tax = []
    #     taxes = line.tax_id.compute_all(price_unit,
    #                                       invoice.currency_id,
    #                                       line.product_uom_qty,
    #                                       line.product_id,
    #                                       invoice.partner_id)['taxes']
    #     tax_dict = {}
    #     for line in taxes:
    #         tax = self.env['account.tax'].sudo().browse(line['id'])
    #         if tax.tax_group_id.name and tax.tax_group_id.name not in tax_dict:
    #             tax_dict[tax.tax_group_id.name] = {}
    #         else:
    #             if 'other' not in tax_dict:
    #                 tax_dict['other'] = {}
    #         if tax.tax_group_id.name:
    #             tax_dict[tax.tax_group_id.name].update({
    #                 'rate': tax.amount,
    #                 'amount': line['amount'],
    #                 'tax_type': tax.tax_group_id.name,
    #                 'tax_id': tax,
    #             })
    #         else:
    #             tax_dict['other'].update({
    #                 'rate': tax.amount,
    #                 'amount': line['amount'],
    #                 'tax_type': 'other',
    #                 'tax_id': tax,
    #             })
    #     return tax_dict

    # def get_lines(self, order):
    #     lines_by_tax_id = {}
    #     for line in order.order_line:
    #         if line.tax_id:
    #             if line.tax_id not in lines_by_tax_id:
    #                 lines_by_tax_id.update({line.tax_id: {'lines': [], 'sum': 0.0}})
    #             lines_by_tax_id[line.product_id.tax_id]['lines'].append(line)
    #             lines_by_tax_id[line.product_id.tax_id]['sum'] += line.price_subtotal
    #             self.total += line.price_subtotal
    #     return lines_by_tax_id
    
    # def get_amount_in_word(self , invoice):
    #     val = invoice.currency_id.amount_to_text(int(invoice.amount_total))
    #     return val
    
    # def amount(self, line):
    #     invoice = line.order_id
    #     total_amt = 0.0
    #     final = 0.0
    #     for rec in line:
    #         total_amt = (rec.price_unit * rec.product_uom_qty)
    #         final = final + total_amt
    #     return final

    # def total_disc(self, order):
    #     total_amt = 0.0
    #     final = 0.0
    #     for rec in order.invoice_line_ids:
    #         total_amt = (rec.price_unit * rec.quantity)
    #         final = final + total_amt
    #     return final
    
    # def total(self, order):
    #     total_amt = 0.0
    #     final = 0.0
    #     for rec in order.order_line:
    #         total_amt = (rec.price_unit * rec.product_uom_qty)
    #         final = final + total_amt
    #     return final

    # def get_total(self):
    #     return self.total

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     docargs = {
    #         'get_type' : self.get_type,
    #         'doc_ids': docids,
    #         'doc_model': 'sale.order',
    #         'docs': self.env['sale.order'].browse(docids),
    #         'time': time,
    #         'get_lines': self.get_lines,
    #         'get_line_tax': self.get_line_tax,
    #         'get_tax_total':self.get_tax_total,
    #         'amount':self.amount,
    #         'total_disc':self.total_disc,
    #         'get_line_total':self.get_line_total,
    #         'get_amount_in_word': self.get_amount_in_word,
    #         'total': self.total,
    #     }
    #     return docargs
