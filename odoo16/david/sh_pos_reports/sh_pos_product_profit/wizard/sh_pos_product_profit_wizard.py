# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import io
import xlwt
import base64
from io import BytesIO
import pytz
from datetime import datetime, timedelta


class POSProductProfitWizard(models.TransientModel):
    _name = 'sh.pos.product.profit.wizard'
    _description = 'Point of Sale Product Profit Wizard'

    sh_start_date = fields.Datetime(
        'Start Date', required=True, default=fields.Datetime.now)
    sh_end_date = fields.Datetime(
        'End Date', required=True, default=fields.Datetime.now)
    sh_partner_ids = fields.Many2many('res.partner', string='Customers')
    sh_session_id = fields.Many2one('pos.session', 'Session')
    report_by = fields.Selection([('customer', 'Customers'), ('product', 'Products'), (
        'both', 'Both')], string='Report Print By', default='customer')
    sh_product_ids = fields.Many2many('product.product', string='Products')
    company_ids = fields.Many2many(
        'res.company', default=lambda self: self.env.companies, string="Companies")

    @api.constrains('sh_start_date', 'sh_end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.sh_end_date and c.sh_start_date > c.sh_end_date):
            raise ValidationError(_('start date must be less than end date.'))

    def print_report(self):
        datas = self.read()[0]
        return self.env.ref('sh_pos_reports.sh_pos_product_profit_action').report_action([], data=datas)

    def display_report(self):
        datas = self.read()[0]
        report = self.env['report.sh_pos_reports.sh_pos_product_profit_doc']
        data_values = report._get_report_values(
            docids=None, data=datas).get('order_dic_by_customers')
        data_values_by_products = report._get_report_values(
            docids=None, data=datas).get('order_dic_by_products')
        data_values_both_order_list = report._get_report_values(
            docids=None, data=datas).get('both_order_list')

        # Customer
        if self.report_by == "customer":
            if data_values:
                self.env['sh.pos.product.profit'].search([]).unlink()
                for customer in data_values:
                    for order in data_values[customer]:
                        cost = order['cost']*order['qty']
                        sale_price = order['sale_price']*order['qty']
                        profit = sale_price-cost
                        margin = (profit/sale_price)*100
                        self.env['sh.pos.product.profit'].create({
                            'sh_partner_id': order['partner_id'],
                            'name': order['order_number'],
                            'order_date': order['order_date'],
                            'product_id': order['product_id'],
                            'quantity': order['qty'],
                            'cost': cost,
                            'sale_price': sale_price,
                            'profit': profit,
                            'margin': margin,
                        })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Point Of Sale Product Profit',
                'view_mode': 'tree',
                'res_model': 'sh.pos.product.profit',
                'context': "{'create': False,'search_default_group_customer': 1}"
            }

        # Product
        if self.report_by == "product":
            if data_values_by_products:
                self.env['sh.pos.product.profit'].search([]).unlink()
                for product in data_values_by_products:
                    for order in data_values_by_products[product]:
                        cost = order['cost']*order['qty']
                        sale_price = order['sale_price']*order['qty']
                        profit = sale_price-cost
                        margin = (profit/sale_price)*100
                        self.env['sh.pos.product.profit'].create({
                            'sh_partner_id': order['partner_id'],
                            'name': order['order_number'],
                            'order_date': order['order_date'],
                            'product_id': order['product_id'],
                            'quantity': order['qty'],
                            'cost': cost,
                            'sale_price': sale_price,
                            'profit': profit,
                            'margin': margin,
                        })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Point Of Sale Product Profit',
                'view_mode': 'tree',
                'res_model': 'sh.pos.product.profit',
                'context': "{'create': False,'search_default_group_product': 1}"
            }

        # Both
        if self.report_by == "both":
            self.env['sh.pos.product.profit'].search([]).unlink()
            for order in data_values_both_order_list:
                cost = order['cost']*order['qty']
                sale_price = order['sale_price']*order['qty']
                profit = sale_price - cost
                margin = (profit/sale_price)*100
                self.env['sh.pos.product.profit'].create({
                    'sh_partner_id': order['partner_id'],
                    'name': order['order_number'],
                    'order_date': order['order_date'],
                    'product_id': order['product_id'],
                    'quantity': order['qty'],
                    'cost': cost,
                    'sale_price': sale_price,
                    'profit': profit,
                    'margin': margin,
                })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Point Of Sale Product Profit',
                'view_mode': 'tree',
                'res_model': 'sh.pos.product.profit',
                'context': "{'create': False}"
            }

    def print_xls_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        heading_format = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold = xlwt.easyxf(
            'font:bold True,height 215;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold_center = xlwt.easyxf(
            'align: horiz center;font:bold True')
        worksheet = workbook.add_sheet(
            'Point of Sale Product Profit', bold_center)
        left = xlwt.easyxf('align: horiz center;font:bold True')
        center = xlwt.easyxf('align: horiz center;')
        bold_center_total = xlwt.easyxf('align: horiz center;font:bold True')
        date_start = False
        date_stop = False
        if self.sh_start_date:
            date_start = fields.Datetime.from_string(self.sh_start_date)
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get(
                'tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(
                fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if self.sh_end_date:
            date_stop = fields.Datetime.from_string(self.sh_end_date)
            # avoid a date_stop smaller than date_start
            if (date_stop < date_start):
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        start_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.sh_start_date),
                                                                           DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.sh_end_date),
                                                                         DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        order_dic_by_customers = {}
        order_dic_by_products = {}
        both_order_list = []
        if self.report_by == 'customer':
            partners = False
            if self.sh_partner_ids:
                partners = self.sh_partner_ids
            else:
                partners = self.env['res.partner'].sudo().search([])
            if partners:
                for partner_id in partners:
                    order_list = []
                    domain = [
                        ("date_order", ">=", fields.Datetime.to_string(date_start)),
                        ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                        ("partner_id", "=", partner_id.id),
                        ('state', 'not in', ['draft', 'cancel'])
                    ]
                    if self.company_ids:
                        domain.append(
                            ('company_id', 'in', self.company_ids.ids))
                    if self.sh_session_id:
                        domain.append(
                            ('session_id', '=', self.sh_session_id.id))
                    search_orders = self.env['pos.order'].sudo().search(domain)
                    if search_orders:
                        for order in search_orders:
                            if order.lines:
                                order_dic = {}
                                for line in order.lines:
                                    line_dic = {
                                        'order_number': order.name,
                                        'order_date': order.date_order.date(),
                                        'product': line.product_id.name_get()[0][1],
                                        'qty': float("{:.2f}".format(line.qty)),
                                        'cost': float("{:.2f}".format(line.product_id.standard_price)),
                                        'sale_price': float("{:.2f}".format(line.price_unit)),
                                    }
                                    if order_dic.get(line.product_id.id, False):
                                        qty = order_dic.get(
                                            line.product_id.id)['qty']
                                        qty = qty + line.qty
                                        line_dic.update({
                                            'qty': float("{:.2f}".format(qty)),
                                        })
                                    order_dic.update(
                                        {line.product_id.id: line_dic})
                                for key, value in order_dic.items():
                                    order_list.append(value)
                    if partner_id and order_list:
                        order_dic_by_customers.update(
                            {partner_id.name_get()[0][1]: order_list})
        elif self.report_by == 'product':
            products = False
            if self.sh_product_ids:
                products = self.sh_product_ids
            else:
                products = self.env['product.product'].sudo().search([])
            if products:
                for product_id in products:
                    order_list = []
                    domain = [
                        ("date_order", ">=", fields.Datetime.to_string(date_start)),
                        ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                        ('state', 'not in', ['draft', 'cancel'])
                    ]
                    if self.company_ids:
                        domain.append(
                            ('company_id', 'in', self.company_ids.ids))
                    if self.sh_session_id:
                        domain.append(
                            ('session_id', '=', self.sh_session_id.id))
                    search_orders = self.env['pos.order'].sudo().search(domain)
                    if search_orders:
                        for order in search_orders:
                            if order.lines:
                                order_dic = {}
                                for line in order.lines.sudo().filtered(lambda x: x.product_id.id == product_id.id):
                                    line_dic = {
                                        'order_number': order.name,
                                        'order_date': order.date_order.date(),
                                        'customer': order.partner_id.name_get()[0][1] if order.partner_id else "",
                                        'qty': float("{:.2f}".format(line.qty)),
                                        'cost': float("{:.2f}".format(line.product_id.standard_price)),
                                        'sale_price': float("{:.2f}".format(line.price_unit)),
                                    }
                                    if order_dic.get(line.product_id.id, False):
                                        qty = order_dic.get(
                                            line.product_id.id)['qty']
                                        qty = qty + line.qty
                                        line_dic.update({
                                            'qty': float("{:.2f}".format(qty)),
                                        })
                                    order_dic.update(
                                        {line.product_id.id: line_dic})
                                for key, value in order_dic.items():
                                    order_list.append(value)
                    if product_id and order_list:
                        order_dic_by_products.update(
                            {product_id.name_get()[0][1]: order_list})
        elif self.report_by == 'both':
            products = False
            partners = False
            if self.sh_product_ids:
                products = self.sh_product_ids
            else:
                products = self.env['product.product'].sudo().search([])
            if self.sh_partner_ids:
                partners = self.sh_partner_ids
            else:
                partners = self.env['res.partner'].sudo().search([])
            domain = [
                ("date_order", ">=", fields.Datetime.to_string(date_start)),
                ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                ('state', 'not in', ['draft', 'cancel'])
            ]
            if self.company_ids:
                domain.append(('company_id', 'in', self.company_ids.ids))
            if self.sh_session_id:
                domain.append(('session_id', '=', self.sh_session_id.id))
            search_orders = self.env['pos.order'].sudo().search(domain)
            if search_orders:
                for order in search_orders.sudo().filtered(lambda x: x.partner_id.id in partners.ids):
                    if order.lines:
                        order_dic = {}
                        for line in order.lines.sudo().filtered(lambda x: x.product_id.id in products.ids):
                            line_dic = {
                                'order_number': order.name,
                                'order_date': order.date_order.date(),
                                'customer': order.partner_id.name_get()[0][1] if order.partner_id else "",
                                'product': line.product_id.name_get()[0][1],
                                'qty': float("{:.2f}".format(line.qty)),
                                'cost': float("{:.2f}".format(line.product_id.standard_price)),
                                'sale_price': float("{:.2f}".format(line.price_unit)),
                            }
                            if order_dic.get(line.product_id.id, False):
                                qty = order_dic.get(line.product_id.id)['qty']
                                qty = qty + line.qty
                                line_dic.update({
                                    'qty': float("{:.2f}".format(qty)),
                                })
                            order_dic.update({line.product_id.id: line_dic})
                        if order_dic:
                            for key, value in order_dic.items():
                                both_order_list.append(value)
        worksheet.col(0).width = int(30 * 260)
        worksheet.col(1).width = int(30 * 260)
        worksheet.col(2).width = int(60 * 260)
        worksheet.col(3).width = int(18 * 260)
        worksheet.col(4).width = int(33 * 260)
        worksheet.col(5).width = int(15 * 260)
        worksheet.col(6).width = int(15 * 260)
        worksheet.col(7).width = int(15 * 260)
        worksheet.col(8).width = int(15 * 260)
        row = 4
        if self.report_by == 'customer':
            worksheet.write_merge(
                0, 1, 0, 7, 'Point of Sale Product Profit', heading_format)
            worksheet.write_merge(
                2, 2, 0, 7, start_date + " to " + end_date, bold)
            if order_dic_by_customers:
                for customer in order_dic_by_customers.keys():
                    worksheet.write_merge(
                        row, row, 0, 7, customer, bold)
                    row = row + 2
                    total_cost = 0.0
                    total_sale_price = 0.0
                    total_profit = 0.0
                    total_margin = 0.0
                    worksheet.write(row, 0, "Order Number", bold_center)
                    worksheet.write(row, 1, "Order Date", bold_center)
                    worksheet.write(row, 2, "Product", bold_center)
                    worksheet.write(row, 3, "Quantity", bold_center)
                    worksheet.write(row, 4, "Cost", bold_center)
                    worksheet.write(row, 5, "Sale Price", bold_center)
                    worksheet.write(row, 6, "Profit", bold_center)
                    worksheet.write(row, 7, "Margin(%)", bold_center)
                    row = row + 1
                    for order in order_dic_by_customers[customer]:
                        sale_price = (order.get('sale_price', 0.0)
                                      * order.get('qty', 0.0))
                        profit = (order.get('sale_price', 0.0)*order.get('qty', 0.0)
                                  ) - (order.get('cost', 0.0)*order.get('qty', 0.0))
                        worksheet.write(row, 0, order.get(
                            'order_number', ''), center)
                        worksheet.write(row, 1, str(
                            order.get('order_date', '')), center)
                        worksheet.write(row, 2, order.get(
                            'product', ''), center)
                        worksheet.write(row, 3, "{:.2f}".format(
                            order.get('qty', 0.0)), center)
                        cost = order.get('cost', 0.0) * order.get('qty', 0.0)
                        worksheet.write(row, 4, "{:.2f}".format(cost), center)
                        sale_price = order.get(
                            'sale_price', 0.0) * order.get('qty', 0.0)
                        worksheet.write(
                            row, 5, "{:.2f}".format(sale_price), center)
                        profit = order.get('sale_price', 0.0)*order.get('qty', 0.0) - (
                            order.get('cost', 0.0)*order.get('qty', 0.0))
                        worksheet.write(
                            row, 6, "{:.2f}".format(profit), center)
                        if sale_price != 0.0:
                            margin = (profit/sale_price)*100
                        else:
                            margin = 0.00
                        worksheet.write(
                            row, 7, "{:.2f}".format(margin), center)
                        total_cost = total_cost + cost
                        total_sale_price = total_sale_price + sale_price
                        if profit:
                            total_profit = total_profit + profit
                        total_margin = total_margin + margin
                        row = row + 1
                        worksheet.write(row, 3, "Total", left)
                        worksheet.write(row, 4, "{:.2f}".format(
                            total_cost), bold_center_total)
                        worksheet.write(
                            row, 5, "{:.2f}".format(
                                total_sale_price), bold_center_total)
                        worksheet.write(row, 6, "{:.2f}".format(total_profit),
                                        bold_center_total)
                        worksheet.write(row, 7, "{:.2f}".format(total_margin),
                                        bold_center_total)
                    row = row + 2
            else:
                raise UserError(
                    'There is no Data Found between these dates...')
        elif self.report_by == 'product':
            worksheet.write_merge(
                0, 1, 0, 7, 'Point of Sale Product Profit', heading_format)
            worksheet.write_merge(
                2, 2, 0, 7, start_date + " to " + end_date, bold)
            if order_dic_by_products:
                for product in order_dic_by_products.keys():
                    worksheet.write_merge(
                        row, row, 0, 7, product, bold)
                    row = row + 2
                    total_cost = 0.0
                    total_sale_price = 0.0
                    total_profit = 0.0
                    total_margin = 0.0
                    worksheet.write(row, 0, "Order Number", bold_center)
                    worksheet.write(row, 1, "Order Date", bold_center)
                    worksheet.write(row, 2, "Customer", bold_center)
                    worksheet.write(row, 3, "Quantity", bold_center)
                    worksheet.write(row, 4, "Cost", bold_center)
                    worksheet.write(row, 5, "Sale Price", bold_center)
                    worksheet.write(row, 6, "Profit", bold_center)
                    worksheet.write(row, 7, "Margin(%)", bold_center)
                    row = row + 1
                    for order in order_dic_by_products[product]:
                        sale_price = (order.get('sale_price', 0.0)
                                      * order.get('qty', 0.0))
                        profit = (order.get('sale_price', 0.0)*order.get('qty', 0.0)
                                  ) - (order.get('cost', 0.0)*order.get('qty', 0.0))
                        worksheet.write(row, 0, order.get(
                            'order_number', ''), center)
                        worksheet.write(row, 1, str(
                            order.get('order_date', '')), center)
                        worksheet.write(row, 2, order.get(
                            'customer', ''), center)
                        worksheet.write(row, 3, "{:.2f}".format(
                            order.get('qty', 0.0)), center)
                        cost = order.get('cost', 0.0) * order.get('qty', 0.0)
                        sale_price = order.get(
                            'sale_price', 0.0) * order.get('qty', 0.0)
                        profit = order.get('sale_price', 0.0)*order.get('qty', 0.0) - (
                            order.get('cost', 0.0)*order.get('qty', 0.0))
                        if sale_price != 0.0:
                            margin = (profit/sale_price)*100
                        else:
                            margin = 0.00
                        worksheet.write(row, 4, "{:.2f}".format(cost), center)
                        worksheet.write(
                            row, 5, "{:.2f}".format(sale_price), center)
                        worksheet.write(
                            row, 6, "{:.2f}".format(profit), center)
                        worksheet.write(
                            row, 7, "{:.2f}".format(margin), center)
                        total_cost = total_cost + cost
                        total_sale_price = total_sale_price + sale_price
                        if profit:
                            total_profit = total_profit + profit
                        total_margin = total_margin + margin
                        row = row + 1
                        worksheet.write(row, 3, "Total", left)
                        worksheet.write(row, 4, "{:.2f}".format(
                            total_cost), bold_center_total)
                        worksheet.write(
                            row, 5, "{:.2f}".format(
                                total_sale_price), bold_center_total)
                        worksheet.write(row, 6, "{:.2f}".format(total_profit),
                                        bold_center_total)
                        worksheet.write(row, 7, "{:.2f}".format(total_margin),
                                        bold_center_total)
                    row = row + 2
            else:
                raise UserError(
                    'There is no Data Found between these dates...')
        elif self.report_by == 'both':
            worksheet.col(0).width = int(30 * 260)
            worksheet.col(1).width = int(30 * 260)
            worksheet.col(2).width = int(30 * 260)
            worksheet.col(3).width = int(60 * 260)
            worksheet.col(4).width = int(33 * 260)
            worksheet.col(5).width = int(15 * 260)
            worksheet.col(6).width = int(15 * 260)
            worksheet.col(7).width = int(15 * 260)
            worksheet.col(8).width = int(15 * 260)
            worksheet.write_merge(
                0, 1, 0, 8, 'Point of Sale Product Profit', heading_format)
            worksheet.write_merge(
                2, 2, 0, 8, start_date + " to " + end_date, bold)
            if both_order_list:
                total_cost = 0.0
                total_sale_price = 0.0
                total_profit = 0.0
                total_margin = 0.0
                worksheet.write(row, 0, "Order Number", bold_center)
                worksheet.write(row, 1, "Order Date", bold_center)
                worksheet.write(row, 2, "Customer", bold_center)
                worksheet.write(row, 3, "Product", bold_center)
                worksheet.write(row, 4, "Quantity", bold_center)
                worksheet.write(row, 5, "Cost", bold_center)
                worksheet.write(row, 6, "Sale Price", bold_center)
                worksheet.write(row, 7, "Profit", bold_center)
                worksheet.write(row, 8, "Margin(%)", bold_center)
                row = row + 1
                for order in both_order_list:
                    sale_price = (order.get('sale_price', 0.0)
                                  * order.get('qty', 0.0))
                    profit = (order.get('sale_price', 0.0)*order.get('qty', 0.0)
                              ) - (order.get('cost', 0.0)*order.get('qty', 0.0))
                    worksheet.write(row, 0, order.get(
                        'order_number', ''), center)
                    worksheet.write(row, 1, str(
                        order.get('order_date', '')), center)
                    worksheet.write(row, 2, order.get('customer', ''), center)
                    worksheet.write(row, 3, order.get('product', ''), center)
                    worksheet.write(row, 4, "{:.2f}".format(
                        order.get('qty', 0.0)), center)
                    cost = order.get('cost', 0.0) * order.get('qty', 0.0)
                    sale_price = order.get(
                        'sale_price', 0.0) * order.get('qty', 0.0)
                    profit = order.get('sale_price', 0.0)*order.get('qty', 0.0) - (
                        order.get('cost', 0.0)*order.get('qty', 0.0))
                    if sale_price != 0.0:
                        margin = (profit/sale_price)*100
                    else:
                        margin = 0.00

                    worksheet.write(row, 5, "{:.2f}".format(cost), center)
                    worksheet.write(
                        row, 6, "{:.2f}".format(sale_price), center)
                    worksheet.write(row, 7, "{:.2f}".format(profit), center)
                    worksheet.write(row, 8, "{:.2f}".format(margin), center)
                    total_cost = total_cost + cost
                    total_sale_price = total_sale_price + sale_price
                    if profit:
                        total_profit = total_profit + profit
                    total_margin = total_margin + margin
                    row = row + 1
                    worksheet.write(row, 4, "Total", left)
                    worksheet.write(row, 5, "{:.2f}".format(
                        total_cost), bold_center_total)
                    worksheet.write(
                        row, 6, "{:.2f}".format(
                            total_sale_price), bold_center_total)
                    worksheet.write(row, 7, "{:.2f}".format(total_profit),
                                    bold_center_total)
                    worksheet.write(row, 8, "{:.2f}".format(total_margin),
                                    bold_center_total)
                row = row + 2
            else:
                raise UserError(
                    'There is no Data Found between these dates...')
        filename = ('Point of Sale Product Profit' + '.xls')
        fp = io.BytesIO()
        workbook.save(fp)
        data = base64.encodebytes(fp.getvalue())
        IrAttachment = self.env['ir.attachment']
        attachment_vals = {
            "name": filename,
            "res_model": "ir.ui.view",
            "type": "binary",
            "datas": data,
            "public": True,
        }
        fp.close()

        attachment = IrAttachment.search([('name', '=', filename),
                                          ('type', '=', 'binary'),
                                          ('res_model', '=', 'ir.ui.view')],
                                         limit=1)
        if attachment:
            attachment.write(attachment_vals)
        else:
            attachment = IrAttachment.create(attachment_vals)
        # TODO: make user error here
        if not attachment:
            raise UserError('There is no attachments...')

        url = "/web/content/" + \
            str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
