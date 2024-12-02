# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Milind Mohan(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

import datetime
import io
import json
# from datetime import datetime

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class MobileServiceReport(models.Model):
    _name = 'mobile.service.report'

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date", default=fields.Date.today,
                           required=True)
    status = fields.Selection([('draft', 'Draft'), ('assigned', 'Assigned'),
                               ('completed', 'Completed'),
                               ('returned', 'Returned'),
                               ('not_solved', 'Not solved')],
                              string='Service Status',
                              default='')
    technician = fields.Many2one('res.users', string="Technician")

    def get_report(self):
        if self.date_start:
            date_start = datetime.datetime.strftime(self.date_start, "%Y-%m-%d")
        else:
            date_start = False
        date_end = datetime.datetime.strftime(self.date_end, "%Y-%m-%d")
        if date_start:
            if date_start > date_end:
                raise UserError("Start date should be less than end date")

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': date_start,
                'date_end': date_end,
                'service_status': self.status,
                'technician': self.technician.name,
            },
        }

        return self.env.ref(
            'mobile_service_shop_pro.mobile_service_report').report_action(self,
                                                                           data=data)

    def print_xlsx_report(self):
        if self.date_start:
            date_start = datetime.datetime.strftime(self.date_start, "%Y-%m-%d")
        else:
            date_start = False
        date_end = datetime.datetime.strftime(self.date_end, "%Y-%m-%d")
        if date_start:
            if date_start > date_end:
                raise UserError("Start date should be less than end date")

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': date_start,
                'date_end': date_end,
                'service_status': self.status,
                'technician': self.technician.name,
            },
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'mobile.service.report',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Mobile Service Report',
                     },
            'report_type': 'service_xlsx'
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        if data['form']['date_start']:
            if data['form']['service_status']:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                        ('technician_name', '=', data['form']['technician']),
                        ('service_state', '=', data['form']['service_status']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                        ('service_state', '=', data['form']['service_status']),
                    ])
            else:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                        ('technician_name', '=', data['form']['technician']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                    ])

        else:
            if data['form']['service_status']:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                        ('service_state', '=', data['form']['service_status']),
                        ('technician_name', '=', data['form']['technician']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                        ('service_state', '=', data['form']['service_status']),
                    ])
            else:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                        ('technician_name', '=', data['form']['technician']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                    ])

        sheet = workbook.add_worksheet('Report')

        bold = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})
        date = workbook.add_format({'bold': True, 'font_size': '10px'})
        date_to = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px', 'border': 1})
        txt = workbook.add_format({'font_size': '10px', 'border': 1})
        type = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})

        sheet.merge_range('C2:H3', 'SERVICE REQUEST REPORT', head)
        sheet.write('C5', "FROM", date)
        sheet.write('D5', data['form']['date_start'], date)
        sheet.write('F5', "TO", date_to)
        sheet.write('G5', data['form']['date_end'], date)
        sheet.write('C7', 'SERV NO.', bold)
        sheet.write('D7', 'CUSTOMER', bold)
        sheet.write('E7', 'PRODUCT', bold)
        sheet.write('F7', 'REQ DATE', bold)
        sheet.write('G7', 'RET DATE', bold)
        sheet.write('H7', 'STATE', bold)

        sheet.set_column(2, 7, 15)
        sheet.set_column(3, 7, 15)
        sheet.set_column(4, 7, 15)
        sheet.set_column(5, 7, 15)
        sheet.set_column(6, 7, 15)
        sheet.set_column(7, 7, 15)

        lst = []
        row_num = 6
        col_num = 2
        for line in service_ids:

            if line.brand_name.brand_name and line.model_name.mobile_brand_models:
                product_name = line.brand_name.brand_name + "( " + line.model_name.mobile_brand_models + " )"
            else:
                product_name = " "

            sheet.write(row_num + 1, col_num, line.name, txt)
            sheet.write(row_num + 1, col_num + 1, line.person_name.name, txt)
            sheet.write(row_num + 1, col_num + 2, product_name, txt)
            sheet.write(row_num + 1, col_num + 3, str(line.return_date), txt)
            sheet.write(row_num + 1, col_num + 4, line.technician_name.name,
                        txt)
            sheet.write(row_num + 1, col_num + 5, line.service_state, txt)
            row_num = row_num + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class MobileServicePartsReport(models.Model):
    _name = 'mobile.parts.report'

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date", default=fields.Date.today,
                           required=True)

    parts_name = fields.Many2one('product.product', string="Parts Name",
                                 domain="[('is_a_parts','=', True)]")

    def get_report(self):
        if self.date_start:
            date_start = datetime.datetime.strptime(str(self.date_start),
                                                    "%Y-%m-%d")
        else:
            date_start = False
        date_end = datetime.datetime.strptime(str(self.date_end),
                                              "%Y-%m-%d").replace(hour=23,
                                                                  minute=59,
                                                                  second=59)
        if date_start:
            if date_start > date_end:
                raise UserError("Start date should be less than end date")
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': date_start,
                'date_end': date_end,
                'parts_id': self.parts_name.product_tmpl_id.id,
            },

        }
        return self.env.ref(
            'mobile_service_shop_pro.parts_usage_report').report_action(self,
                                                                        data=data)

    def print_xlsx_report(self):

        if self.date_start:
            date_start = datetime.datetime.strptime(str(self.date_start),
                                                    "%Y-%m-%d")
        else:
            date_start = False
        date_end = datetime.datetime.strptime(str(self.date_end), "%Y-%m-%d")
        if date_start:
            if date_start > date_end:
                raise UserError("Start date should be less than end date")

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'parts_id': self.parts_name.product_tmpl_id.id,
            },
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'mobile.parts.report',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Mobile Parts Report',
                     },
            'report_type': 'service_xlsx'
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        prod_id_lst = []
        if data['form']['date_start']:
            order_line_ids = self.env['product.order.line'].search([
                ('write_date', '>=', data['form']['date_start']),
                ('write_date', '<=', data['form']['date_end'])
            ])
        else:
            order_line_ids = self.env['product.order.line'].search([])

        for obj in order_line_ids:
            if obj.product_id.product_tmpl_id and obj.product_id.product_tmpl_id.id not in prod_id_lst:
                prod_id_lst.append(obj.product_id.product_tmpl_id.id)
        if data['form']['parts_id']:
            product_id = self.env['product.template'].search(
                [('is_a_parts', '=', True),
                 ('id', '=', data['form']['parts_id'])])
        else:
            product_id = self.env['product.template'].search(
                [('is_a_parts', '=', True)])
        lst = []
        lst1 = []
        for line in product_id:
            if line.id in prod_id_lst:
                lst.append({
                    'id': line.id,
                    'part_brand': line.brand_name.brand_name,
                    'part_model': line.model_name.mobile_brand_models,
                    'part_colour': line.model_colour,
                    'product_name': line.name,

                })
        for line in order_line_ids:
            lst1.append({
                'product_id': line.product_id.product_tmpl_id.id,
                'serv_id': line.product_order_id.name,
                'qty': line.qty_invoiced,
                'qty_used': line.product_uom_qty,
                'qty_stock_move': line.qty_stock_move,
                'price': line.part_price,
                'create_date': line.write_date,
                'technician': line.product_order_id.technician_name.name,
                'symbol': self.env.user.company_id.currency_id.symbol,

            })

        sheet = workbook.add_worksheet('Report')

        bold = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})
        date = workbook.add_format({'bold': True, 'font_size': '10px'})
        date_to = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px', 'border': 1})
        txt = workbook.add_format({'font_size': '10px', 'border': 1})
        type = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})

        sheet.merge_range('C2:I3', 'PARTS USAGE REPORT', head)
        sheet.write('C5', "FROM", date)
        sheet.write('D5', data['form']['date_start'], date)
        sheet.write('F5', "TO", date_to)
        sheet.write('G5', data['form']['date_end'], date)
        sheet.write('C7', 'SERV NO.', bold)
        sheet.write('D7', 'TECHNICIAN', bold)
        sheet.write('E7', 'USED DATE', bold)
        sheet.write('F7', 'USED QUANTITY', bold)
        sheet.write('G7', 'QTY INVOICED', bold)
        sheet.write('H7', 'QTY STOCK MOVE', bold)
        sheet.write('I7', 'PRICE', bold)

        sheet.set_column(2, 7, 15)
        sheet.set_column(3, 7, 15)
        sheet.set_column(4, 7, 15)
        sheet.set_column(5, 7, 15)
        sheet.set_column(6, 7, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 7, 15)

        row_num = 6
        col_num = 2
        for line in lst:
            prod_name = line['product_name']
            part_brand = line['part_brand']
            part_model = line['part_model']
            part_colour = line['part_colour']
            temp_name = str(prod_name) + "( " + str(part_brand) + " " + str(
                part_model) + " " + str(part_colour) + " )"
            sheet.merge_range(row_num + 1, col_num, row_num + 1, col_num + 6,
                              temp_name, bold)
            row_num = row_num + 1
            for prod_line in lst1:
                if line['id'] == prod_line['product_id']:
                    sheet.write(row_num + 1, col_num, prod_line['serv_id'], txt)
                    sheet.write(row_num + 1, col_num + 1,
                                prod_line['technician'], txt)
                    sheet.write(row_num + 1, col_num + 2,
                                str(prod_line['create_date']), txt)
                    sheet.write(row_num + 1, col_num + 3, prod_line['qty_used'],
                                txt)
                    sheet.write(row_num + 1, col_num + 4, prod_line['qty'], txt)
                    sheet.write(row_num + 1, col_num + 5,
                                prod_line['qty_stock_move'], txt)
                    sheet.write(row_num + 1, col_num + 6,
                                prod_line['price'] + prod_line['symbol'], txt)
                    row_num = row_num + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class MobileServiceComplaintsReport(models.Model):
    _name = 'complaint.type.report'

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date", default=fields.Date.today,
                           required=True)

    complaint_type = fields.Many2one('mobile.complaint',
                                     string="Complaint Type")

    def get_report(self):
        if self.date_start:
            date_start = datetime.datetime.strptime(str(self.date_start),
                                                    "%Y-%m-%d")
        else:
            date_start = False
        date_end = datetime.datetime.strptime(str(self.date_end), "%Y-%m-%d")
        if date_start:
            if date_start > date_end:
                raise UserError("Start date should be less than end date")

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'complaint_type': self.complaint_type.id,
            },
        }
        return self.env.ref(
            'mobile_service_shop_pro.complaint_type_report').report_action(self,
                                                                           data=data)

    def print_xlsx_report(self):
        if self.date_start:
            date_start = datetime.datetime.strptime(str(self.date_start),
                                                    "%Y-%m-%d")
        else:
            date_start = False
        date_end = datetime.datetime.strptime(str(self.date_end), "%Y-%m-%d")
        if date_start:
            if date_start > date_end:
                raise UserError("Start date should be less than end date")

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'complaint_type': self.complaint_type.id,
            },
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'complaint.type.report',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Mobile Service Report',
                     },
            'report_type': 'service_xlsx'
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        if data['form']['date_start']:
            if data['form']['complaint_type']:
                complaints_filterd = self.env['mobile.complaint.tree'].search([
                    ('write_date', '>=', data['form']['date_start']),
                    ('write_date', '<=', data['form']['date_end']),
                    ('complaint_type_tree', '=', data['form']['complaint_type'])
                ])
            else:
                complaints_filterd = self.env['mobile.complaint.tree'].search([
                    ('write_date', '>=', data['form']['date_start']),
                    ('write_date', '<=', data['form']['date_end']),
                ])
        else:
            if data['form']['complaint_type']:
                complaints_filterd = self.env['mobile.complaint.tree'].search([
                    ('complaint_type_tree', '=', data['form']['complaint_type'])
                ])
            else:
                complaints_filterd = self.env['mobile.complaint.tree'].search(
                    [])

        complaints_obj = self.env['mobile.complaint.description'].search([])
        lst = []
        lst1 = []
        for line1 in complaints_filterd:
            lst1.append({
                'complaint_type': line1.complaint_type_tree.complaint_type,
                'description': line1.description_tree.description,
                'serv_no': line1.complaint_id.name,
                'brand': line1.complaint_id.brand_name.brand_name,
                'model': line1.complaint_id.model_name.mobile_brand_models,
                'date': line1.complaint_id.date_request,
                'technician': line1.complaint_id.technician_name.name,
            })
        for line in complaints_obj:
            lst.append({
                'complaint_type': line.complaint_type_template.complaint_type,
                'description': line.description,
                'print': 0,
            })
        for lst_obj in lst:
            for lst1_obj in lst1:
                if lst_obj['complaint_type'] == lst1_obj['complaint_type'] and \
                        lst_obj['description'] == lst1_obj['description']:
                    lst_obj['print'] = 1

        sheet = workbook.add_worksheet('Report')

        bold = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})
        date = workbook.add_format({'bold': True, 'font_size': '10px'})
        date_to = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px', 'border': 1})
        txt = workbook.add_format({'font_size': '10px', 'border': 1})
        type = workbook.add_format(
            {'bold': True, 'font_size': '10px', 'border': 1})

        sheet.merge_range('C2:G3', 'COMPLAINT TYPE REPORT', head)
        sheet.write('C5', "FROM", date)
        sheet.write('D5', data['form']['date_start'], date)
        sheet.write('F5', "TO", date_to)
        sheet.write('G5', data['form']['date_end'], date)
        sheet.write('C7', 'SERV NO.', bold)
        sheet.write('D7', 'TECHNICIAN', bold)
        sheet.write('E7', 'BRAND', bold)
        sheet.write('F7', 'MODEL', bold)
        sheet.write('G7', 'DATE REQUEST', bold)

        sheet.set_column(2, 7, 20)
        sheet.set_column(3, 7, 20)
        sheet.set_column(4, 7, 20)
        sheet.set_column(5, 7, 20)

        row_num = 6
        col_num = 2
        for line in lst:
            compl_type = line['complaint_type']
            description = line['description']
            complaint = str(compl_type) + "-" + str(description)
            if line['print'] == 1:
                sheet.merge_range(row_num + 1, col_num, row_num + 1,
                                  col_num + 4, complaint, bold)
                row_num = row_num + 1

            for cmpl_line in lst1:
                if line['complaint_type'] == cmpl_line['complaint_type']:
                    if line['description'] == cmpl_line['description']:
                        sheet.write(row_num + 1, col_num, cmpl_line['serv_no'],
                                    txt)
                        sheet.write(row_num + 1, col_num + 1,
                                    cmpl_line['technician'], txt)
                        sheet.write(row_num + 1, col_num + 2,
                                    cmpl_line['brand'], txt)
                        sheet.write(row_num + 1, col_num + 3,
                                    cmpl_line['model'], txt)
                        sheet.write(row_num + 1, col_num + 4,
                                    str(cmpl_line['date']), txt)
                        row_num = row_num + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


