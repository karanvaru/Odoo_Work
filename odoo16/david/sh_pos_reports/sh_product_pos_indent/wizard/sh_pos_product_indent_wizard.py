# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import io
import xlwt
import base64
import pytz
from datetime import datetime, timedelta


class POSProductIndentWizard(models.TransientModel):
    _name = 'sh.pos.product.indent.wizard'
    _description = 'Point of Sale Product Indent Wizard'

    sh_start_date = fields.Datetime(
        'Start Date', required=True, default=fields.Datetime.now)
    sh_end_date = fields.Datetime(
        'End Date', required=True, default=fields.Datetime.now)
    sh_partner_ids = fields.Many2many(
        'res.partner', string='Customers', required=True)
    sh_status = fields.Selection([('all', 'All'), ('draft', 'Draft'), ('paid', 'Paid'), (
        'done', 'Posted'), ('invoiced', 'Invoiced')], default='all', string='Status')
    sh_category_ids = fields.Many2many(
        'product.category', string='Categories', required=True)
    company_ids = fields.Many2many(
        'res.company', default=lambda self: self.env.companies, string="Companies")
    sh_session_id = fields.Many2one('pos.session', 'Session')

    @api.constrains('sh_start_date', 'sh_end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.sh_end_date and c.sh_start_date > c.sh_end_date):
            raise ValidationError(_('start date must be less than end date.'))

    def print_report(self):
        datas = self.read()[0]
        return self.env.ref('sh_pos_reports.sh_pos_product_indent_action').report_action([], data=datas)

    def display_report(self):
        datas = self.read()[0]
        report = self.env['report.sh_pos_reports.sh_pos_product_indent_doc']
        data_values = report._get_report_values(
            docids=None, data=datas).get('order_dic')

        if data_values:
            self.env['sh.product.pos.indent'].search([]).unlink()
            for key in data_values:
                for category_data in data_values[key]:
                    for key2 in category_data:
                        for data in category_data[key2]:
                            self.env['sh.product.pos.indent'].create({
                                'name': data['product_id'],
                                'quantity': data['qty'],
                                'sh_partner_id': data['partner_id'],
                                'sh_category_id': data['category_id'],
                            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Point Of Sale Product Indent',
                'view_mode': 'tree',
                'res_model': 'sh.product.pos.indent',
                'context': "{'create': False,'search_default_group_customer': 1}"
            }

    def print_xls_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        heading_format = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold = xlwt.easyxf(
            'font:bold True,height 215;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold_center = xlwt.easyxf(
            'font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;')
        worksheet = workbook.add_sheet(
            'Point of Sale Product Indent', bold_center)
        worksheet.write_merge(
            0, 1, 0, 1, 'Point of Sale Product Indent', heading_format)
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
        worksheet.write_merge(2, 2, 0, 1, start_date + " to " + end_date, bold)
        worksheet.col(0).width = int(30 * 260)
        worksheet.col(1).width = int(30 * 260)
        order_dic = {}
        for partner in self.sh_partner_ids:
            customer_list = []
            for category in self.sh_category_ids:
                category_dic = {}
                category_list = []
                products = self.env['product.product'].sudo().search(
                    [('categ_id', '=', category.id)])
                for product in products:
                    domain = [
                        ("order_id.date_order", ">=",
                         fields.Datetime.to_string(date_start)),
                        ("order_id.date_order", "<=",
                         fields.Datetime.to_string(date_stop)),
                        ('order_id.partner_id', '=', partner.id),
                        ('product_id', '=', product.id)
                    ]
                    if self.sh_status == 'all':
                        domain.append(('order_id.state', 'not in', ['cancel']))
                    elif self.sh_status == 'draft':
                        domain.append(('order_id.state', 'in', ['draft']))
                    elif self.sh_status == 'paid':
                        domain.append(('order_id.state', 'in', ['paid']))
                    elif self.sh_status == 'done':
                        domain.append(('order_id.state', 'in', ['done']))
                    elif self.sh_status == 'invoiced':
                        domain.append(('order_id.state', 'in', ['invoiced']))
                    if self.company_ids:
                        domain.append(
                            ('order_id.company_id', 'in', self.company_ids.ids))
                    if self.sh_session_id:
                        domain.append(
                            ('order_id.session_id', '=', self.sh_session_id.id))
                    order_lines = self.env['pos.order.line'].sudo().search(
                        domain).mapped('qty')
                    product_qty = 0.0
                    if order_lines:
                        for qty in order_lines:
                            product_qty += qty
                    if product_qty == 0:
                        continue
                    else:
                        product_dic = {
                            'name': product.name_get()[0][1],
                            'qty': product_qty,
                        }
                    category_list.append(product_dic)
                if category and category_list:
                    category_dic.update({
                        category.display_name: category_list
                    })
                    customer_list.append(category_dic)
            if partner and customer_list:
                order_dic.update({partner.name_get()[0][1]: customer_list})
        row = 4
        if order_dic:
            for key in order_dic.keys():
                worksheet.write(row, 0, key, bold)
                worksheet.write_merge(row, row, 0, 1, key, bold)
                row = row + 2
                for category_data in order_dic[key]:
                    for key_2 in category_data.keys():
                        total = 0.0
                        worksheet.write_merge(row, row, 0, 1, key_2, bold)
                        row = row + 1
                        worksheet.write(row, 0, "Product", bold_center_total)
                        worksheet.write(row, 1, "Quantity", bold_center_total)
                        row = row + 1
                        for record in category_data[key_2]:
                            total = total + record.get('qty')
                            worksheet.write(row, 0, record.get('name'), center)
                            worksheet.write(row, 1, "{:.2f}".format(
                                record.get('qty')), center)
                            row = row + 1
                        worksheet.write(row, 0, "Total", bold_center_total)
                        worksheet.write(row, 1, "{:.2f}".format(
                            total), bold_center_total)
                        row = row + 2
        else:
            raise UserError('There is no Data Found between these dates...')

        filename = ('Point of Sale Product Indent' + '.xls')
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
