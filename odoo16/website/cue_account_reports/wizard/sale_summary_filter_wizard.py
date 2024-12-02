# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo import models, fields, api
import xlwt
import base64
from io import BytesIO


class SaleSummaryFilterExcel(models.TransientModel):
    _name = "sale.summary.excel"
    _description = "Sales Summary wizard"

    datas_date = fields.Binary(string="Report")
    file_name = fields.Char(string='Filename')


class SaleSummaryFilterWizard(models.TransientModel):
    _name = 'sale.summary.filter.wizard'

    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today().replace(day=1)
    )
    date_end = fields.Date(
        string='End Date',
        default=fields.Date.today().replace(day=30),
        required=True
    )
    partner_ids = fields.Many2many(
        'res.partner'
    )
    product_ids = fields.Many2many(
        'product.product'
    )

    def print_excel_report(self):
        filename = "Sales Summary Report.xls"
        workbook = xlwt.Workbook(encoding='utf-8')

        sheet1 = workbook.add_sheet("exel", cell_overwrite_ok=True)
        month_title_style = xlwt.easyxf(
            'font: name Times New Roman, bold on;align: horiz  center;\
            borders: top_color black, bottom_color black, right_color black, left_color black, \
            top thin, bottom thin, left thin, right thin;',
        )

        product_label = xlwt.easyxf(
            'font: name Times New Roman, bold on;\
            borders: top_color black, bottom_color black, right_color black, left_color black, \
            top thin, bottom thin, left thin, right thin;',
        )
        partner_label = xlwt.easyxf(
            'font: name Times New Roman, bold on;\
            borders: top_color black, bottom_color black, right_color black, left_color black, \
            top thin, bottom thin, left thin, right thin;',
        )
        product_right = xlwt.easyxf(
            'font: name Times New Roman, bold on;align: horiz  right;\
            borders: top_color black, bottom_color black, right_color black, left_color black, \
            top thin, bottom thin, left thin, right thin;',
            num_format_str='#,##0'
        )

        table_data_right = xlwt.easyxf(
            'font: name Times New Roman;align: horiz  right;\
            borders: top_color black, bottom_color black, right_color black, left_color black, \
            top thin, bottom thin, left thin, right thin;',
            num_format_str='#,##0'
        )
        table_title = xlwt.easyxf(
            'font: name Times New Roman, bold on;align: horiz  right;\
            pattern: pattern solid, fore_colour black;',
            num_format_str='#,##0.00'
        )
        domain = [
            ('move_id.invoice_date', '>=', self.date_start),
            ('move_id.invoice_date', '<=', self.date_end),
            ('move_id.state', '=', "posted"),
            ('move_id.move_type', 'in', ['out_invoice']),
        ]
        if self.partner_ids:
            domain += [('move_id.partner_id', 'in', self.partner_ids.ids)]

        if self.product_ids:
            domain += [('product_id', 'in', self.product_ids.ids)]
        else:
            domain += [('product_id', '!=', False)]

        move_lines = self.env['account.move.line'].search(domain)

        month_dict = {}
        month_list = []

        mvline_total = {}
        product_total = {}
        product_line_total = {}
        product_partner_line_total = {}

        month_name = {}

        new_main_dict = {}
        for line in move_lines:
            if line.product_id not in new_main_dict:
                new_main_dict[line.product_id] = {line.move_id.partner_id: {}}

            if line.move_id.partner_id not in new_main_dict[line.product_id]:
                new_main_dict[line.product_id].update({line.move_id.partner_id: {}})

            if line.date.strftime("%m") not in new_main_dict[line.product_id][line.move_id.partner_id]:
                new_main_dict[line.product_id][line.move_id.partner_id].update({line.date.strftime("%m"): {}})

            if line.date.strftime("%m") not in month_list:
                month_list.append(line.date.strftime("%m"))
                month_name[line.date.strftime("%m")] = line.date.strftime("%B")

            dict_key = (line.product_id.id, line.move_id.partner_id.id, line.date.strftime("%m"))
            if dict_key not in mvline_total:
                mvline_total[dict_key] = {'qty': line.quantity, 'subtotal': line.price_subtotal,
                                          'total': line.price_total}
            else:
                mvline_total[dict_key]['qty'] += line.quantity
                mvline_total[dict_key]['subtotal'] += line.price_subtotal
                mvline_total[dict_key]['total'] += line.price_total

            product_key = (line.product_id.id, line.date.strftime("%m"))
            if product_key not in product_total:
                product_total[product_key] = {'qty': line.quantity, 'subtotal': line.price_subtotal,
                                              'total': line.price_total}
            else:
                product_total[product_key]['qty'] += line.quantity
                product_total[product_key]['subtotal'] += line.price_subtotal
                product_total[product_key]['total'] += line.price_total

            product_line_key = (line.product_id.id)
            if product_line_key not in product_line_total:
                product_line_total[product_line_key] = {'qty': line.quantity, 'subtotal': line.price_subtotal,
                                                        'total': line.price_total}
            else:
                product_line_total[product_line_key]['qty'] += line.quantity
                product_line_total[product_line_key]['subtotal'] += line.price_subtotal
                product_line_total[product_line_key]['total'] += line.price_total

            product_partner_line_key = (line.product_id.id, line.move_id.partner_id.id)
            if product_partner_line_key not in product_partner_line_total:
                product_partner_line_total[product_partner_line_key] = {'qty': line.quantity,
                                                                        'subtotal': line.price_subtotal,
                                                                        'total': line.price_total}
            else:
                product_partner_line_total[product_partner_line_key]['qty'] += line.quantity
                product_partner_line_total[product_partner_line_key]['subtotal'] += line.price_subtotal
                product_partner_line_total[product_partner_line_key]['total'] += line.price_total
        pr_inext = 0
        m_col = 2
        month_list.reverse()
        max_month_col = 2
        for m in month_list:
            sheet1.write_merge(pr_inext, pr_inext, m_col, m_col + 2, month_name[m], month_title_style)
            sheet1.write(pr_inext + 1, m_col, "Qty", month_title_style)
            sheet1.write(pr_inext + 1, m_col + 1, "Subtotal", month_title_style)
            sheet1.write(pr_inext + 1, m_col + 2, "Total", month_title_style)
            month_dict[m] = m_col
            m_col += 3
            if m_col > max_month_col:
                max_month_col = m_col

        sheet1.write(pr_inext + 1, max_month_col, "Total Qty", month_title_style)
        sheet1.write(pr_inext + 1, max_month_col + 1, "Subtotal", month_title_style)
        sheet1.write(pr_inext + 1, max_month_col + 2, "Total", month_title_style)

        pr_inext = 2
        product_row = 2
        for product in new_main_dict:
            product_row = pr_inext
            sheet1.write(pr_inext, 0, product.name, product_label)
            sheet1.write(pr_inext, 1, '', product_label)
            pr_inext += 1
            for partner in new_main_dict[product]:
                sheet1.write(pr_inext, 1, partner.name, partner_label)
                sheet1.write(pr_inext, 0, '', partner_label)

                #                 for m  in new_main_dict[product][partner]:
                for m in month_list:
                    m_index = month_dict[m]
                    dict_key = (product.id, partner.id, m)
                    if dict_key in mvline_total:
                        sheet1.write(pr_inext, m_index, mvline_total[dict_key]['qty'], table_data_right)
                        sheet1.write(pr_inext, m_index + 1, mvline_total[dict_key]['subtotal'], table_data_right)
                        sheet1.write(pr_inext, m_index + 2, mvline_total[dict_key]['total'], table_data_right)
                    else:
                        sheet1.write(pr_inext, m_index, 0, table_data_right)
                        sheet1.write(pr_inext, m_index + 1, 0, table_data_right)
                        sheet1.write(pr_inext, m_index + 2, 0, table_data_right)

                    product_key = (product.id, m)
                    if product_key in product_total:
                        sheet1.write(product_row, m_index, product_total[product_key]['qty'], product_right)
                        sheet1.write(product_row, m_index + 1, product_total[product_key]['subtotal'], product_right)
                        sheet1.write(product_row, m_index + 2, product_total[product_key]['total'], product_right)
                    else:
                        sheet1.write(product_row, m_index, 0, product_right)
                        sheet1.write(product_row, m_index + 1, 0, product_right)
                        sheet1.write(product_row, m_index + 2, 0, product_right)

                    product_line_key = (product.id)
                    if product_line_key in product_line_total:
                        sheet1.write(product_row, max_month_col, product_line_total[product_line_key]['qty'],
                                     product_right)
                        sheet1.write(product_row, max_month_col + 1, product_line_total[product_line_key]['subtotal'],
                                     product_right)
                        sheet1.write(product_row, max_month_col + 2, product_line_total[product_line_key]['total'],
                                     product_right)
                    else:
                        sheet1.write(product_row, max_month_col, 0, product_right)
                        sheet1.write(product_row, max_month_col + 1, 0, product_right)
                        sheet1.write(product_row, max_month_col + 2, 0, product_right)

                    product_partner_line_key = (product.id, partner.id)

                    if product_partner_line_key in product_partner_line_total:
                        sheet1.write(pr_inext, max_month_col,
                                     product_partner_line_total[product_partner_line_key]['qty'], table_data_right)
                        sheet1.write(pr_inext, max_month_col + 1,
                                     product_partner_line_total[product_partner_line_key]['subtotal'], table_data_right)
                        sheet1.write(pr_inext, max_month_col + 2,
                                     product_partner_line_total[product_partner_line_key]['total'], table_data_right)
                    else:
                        sheet1.write(pr_inext, max_month_col, 0, table_data_right)
                        sheet1.write(pr_inext, max_month_col + 1, 0, table_data_right)
                        sheet1.write(pr_inext, max_month_col + 2, 0, table_data_right)
                pr_inext += 1

        sheet1.col(0).width = 6000
        sheet1.col(1).width = 7000

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        exel_id = self.env['sale.summary.excel'].create({
            'file_name': filename,
            'datas_date': out
        })
        return {
            'view_mode': 'form',
            'res_id': exel_id.id,
            'res_model': 'sale.summary.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
