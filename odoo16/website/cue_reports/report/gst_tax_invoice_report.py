# -*- coding: utf-8 -*-
import time
from odoo import api, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import decimal


def num2words(num):
	num = decimal.Decimal(num)
	decimal_part = num - int(num)
	num = int(num)

	if decimal_part:
		return num2words(num) + " point " + (" ".join(num2words(i) for i in str(decimal_part)[2:]))

	under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
	tens = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
	above_100 = {100: 'Hundred', 1000: 'Thousand', 100000: 'Lakh', 10000000: 'Crore'}

	if num < 20:
		return under_20[num]

	if num < 100:
		return tens[num // 10 - 2] + ('' if num % 10 == 0 else ' ' + under_20[num % 10])

	# find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
	pivot = max([key for key in above_100.keys() if key <= num])

	return num2words(num // pivot) + ' ' + above_100[pivot] + ('' if num % pivot==0 else ' ' + num2words(num % pivot))


class ReportAccountInvoice(models.AbstractModel):
    _name = 'report.cue_reports.pdf_report_templates_invoice'
    
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
        print("price_total ------",price_total)
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
    
    
    def currency_in_indian_formatdd(self, n):
        """ Convert a number (int / float) into indian formatting style """
        d = decimal.Decimal(str(n))
    
        if d.as_tuple().exponent < -2:
            s = str(n)
        else:
            s = '{0:.2f}'.format(n)
    
        l = len(s)
        i = l - 1
    
        res, flag, k = '', 0, 0
        while i >= 0:
            if flag == 0:
                res += s[i]
                if s[i] == '.':
                    flag = 1
            elif flag == 1:
                k += 1
                res += s[i]
                if k == 3 and i - 1 >= 0:
                    res += ','
                    flag = 2
                    k = 0
            else:
                k += 1
                res += s[i]
                if k == 2 and i - 1 >= 0:
                    res += ','
                    flag = 2
                    k = 0
            i -= 1
    
        return res[::-1]

    def get_amount_in_word(self , invoice):
        val = num2words(int(invoice.amount_total))
#         val = invoice.currency_id.amount_to_text(int(invoice.amount_total))
        val = 'Rupees ' + val + ' Only'
        return val

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
            'get_type' : self.get_type ,
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'get_lines': self.get_lines,
            'get_line_tax': self.get_line_tax,
            'get_tax_total':self.get_tax_total,
            'amount':self.amount,
            'total_disc':self.total_disc,
            'get_line_total':self.get_line_total,
            'get_amount_in_word': self.get_amount_in_word,
        }
        return docargs