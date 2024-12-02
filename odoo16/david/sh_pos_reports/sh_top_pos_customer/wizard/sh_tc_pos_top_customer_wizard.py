# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import io
import operator
import xlwt
import base64
from io import BytesIO
import pytz
from datetime import datetime, timedelta


class ShTcTopCustomerWizard(models.TransientModel):
    _name = "sh.tc.pos.top.customer.wizard"
    _description = 'Top Customers'

    @api.model
    def default_company_ids(self):
        is_allowed_companies = self.env.context.get(
            'allowed_company_ids', False)
        if is_allowed_companies:
            return is_allowed_companies
        return

    type = fields.Selection([
        ('basic', 'Basic'),
        ('compare', 'Compare'),
    ], string="Report Type", default="basic")

    date_from = fields.Datetime(
        string='From Date', required=True, default=fields.Datetime.now)
    date_to = fields.Datetime(string='To Date', required=True,
                              default=fields.Datetime.now)
    date_compare_from = fields.Datetime(
        string='Compare From Date', default=fields.Datetime.now)
    date_compare_to = fields.Datetime(
        string='Compare To Date', default=fields.Datetime.now)
    no_of_top_item = fields.Integer(
        string='No of Items', required=True, default=10)
    amount_total = fields.Monetary(string="Total POS Amount")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    company_ids = fields.Many2many(
        'res.company', string="Company", default=default_company_ids)
    config_ids = fields.Many2many('pos.config', string='POS Configuration')

    @api.constrains('date_from', 'date_to')
    def _check_from_to_dates(self):
        if self.filtered(lambda c: c.date_to and c.date_from > c.date_to):
            raise ValidationError(_('from date must be less than to date.'))

    @api.constrains('date_compare_from', 'date_compare_to')
    def _check_compare_from_to_dates(self):
        if self.filtered(lambda c: c.date_compare_to and c.date_compare_from and c.date_compare_from > c.date_compare_to):
            raise ValidationError(
                _('compare from date must be less than compare to date.'))

    def print_top_customer_report(self):
        self.ensure_one()
        data = {}
        # we read self because we use from date and start date in our core bi logic.(in abstract model)
        data = self.read()[0]
        return self.env.ref('sh_pos_reports.sh_tc_pos_top_customers_report_action').report_action([], data=data)

    def display_report(self):
        datas = self.read()[0]
        report = self.env['report.sh_pos_reports.sh_tc_pos_doc']
        data_values = report._get_report_values(
            docids=None, data=datas).get('partners')
        data_values_amount = report._get_report_values(
            docids=None, data=datas).get('partners_amount')

        if self.type == 'basic':
            self.env['sh.top.pos.customers'].search([]).unlink()
            length = len(data_values)
            for i in range(length):
                self.env['sh.top.pos.customers'].create({
                    'name': data_values[i].id if data_values else False,
                    'sales_amount': data_values_amount[i]
                })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Top POS Customers',
                'view_mode': 'tree',
                'res_model': 'sh.top.pos.customers',
                'context': "{'create': False}"
            }

    def print_top_customer_xls_report(self,):
        workbook = xlwt.Workbook()
        heading_format = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold = xlwt.easyxf(
            'font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
        bold_center = xlwt.easyxf(
            'font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        left = xlwt.easyxf('align: horiz left')
        row = 1
        data = {}
        data = self.read()[0]
        data = dict(data or {})
        currency_id = False
        pos_order_obj = self.env['pos.order']
        date_start = False
        date_stop = False
        if data['date_from']:
            date_start = fields.Datetime.from_string(data['date_from'])
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get(
                'tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(
                fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if data['date_to']:
            date_stop = fields.Datetime.from_string(data['date_to'])
            # avoid a date_stop smaller than date_start
            if (date_stop < date_start):
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        domain = [
            ('date_order', '>=', fields.Datetime.to_string(date_start)),
            ('date_order', '<=', fields.Datetime.to_string(date_stop)),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ]
        if data.get('company_ids', False):
            domain.append(('company_id', 'in', data.get('company_ids', False)))
        if data.get('config_ids', False):
            session_ids = self.env['pos.session'].sudo().search(
                [('config_id', 'in', data.get('config_ids', False))])
            domain.append(('session_id', 'in', session_ids.ids))
        pos_orders = pos_order_obj.sudo().search(domain)
        partner_total_amount_dic = {}
        if pos_orders:
            for order in pos_orders.sorted(key=lambda o: o.partner_id.id):
                if order.currency_id:
                    currency_id = order.currency_id
                if partner_total_amount_dic.get(order.partner_id.name, False):
                    amount = partner_total_amount_dic.get(
                        order.partner_id.name)
                    amount += order.amount_total
                    partner_total_amount_dic.update(
                        {order.partner_id.name: amount})
                else:
                    partner_total_amount_dic.update(
                        {order.partner_id.name: order.amount_total})

        final_partner_list = []
        final_partner_amount_list = []
        if partner_total_amount_dic:
            # sort partner dictionary by descending order
            sorted_partner_total_amount_list = sorted(
                partner_total_amount_dic.items(), key=operator.itemgetter(1), reverse=True)
            counter = 0
            for tuple_item in sorted_partner_total_amount_list:
                if data['amount_total'] != 0 and tuple_item[1] >= data['amount_total']:
                    final_partner_list.append(tuple_item[0])
                elif data['amount_total'] == 0:
                    final_partner_list.append(tuple_item[0])
                final_partner_amount_list.append(tuple_item[1])
                # only show record by user limit
                counter += 1
                if counter >= data['no_of_top_item']:
                    break
        else:
            raise UserError('There is no Data Found between these dates...')

        ##################################
        # for Compare partner from to
        date_start = False
        date_stop = False
        if data['date_compare_from']:
            date_start = fields.Datetime.from_string(data['date_compare_from'])
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get(
                'tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(
                fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if data['date_compare_to']:
            date_stop = fields.Datetime.from_string(data['date_compare_to'])
            # avoid a date_stop smaller than date_start
            if (date_stop < date_start):
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        pos_orders = False
        domain = [
            ('date_order', '>=', fields.Datetime.to_string(date_start)),
            ('date_order', '<=', fields.Datetime.to_string(date_stop)),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ]
        if data.get('company_ids', False):
            domain.append(('company_id', 'in', data.get('company_ids', False)))
        if data.get('config_ids', False):
            session_ids = self.env['pos.session'].sudo().search(
                [('config_id', 'in', data.get('config_ids', False))])
            domain.append(('session_id', 'in', session_ids.ids))
        pos_orders = pos_order_obj.sudo().search(domain)

        partner_total_amount_dic = {}
        if pos_orders:
            for order in pos_orders.sorted(key=lambda o: o.partner_id.id):
                if order.currency_id:
                    currency_id = order.currency_id

                if partner_total_amount_dic.get(order.partner_id.name, False):
                    amount = partner_total_amount_dic.get(
                        order.partner_id.name)
                    amount += order.amount_total
                    partner_total_amount_dic.update(
                        {order.partner_id.name: amount})
                else:
                    partner_total_amount_dic.update(
                        {order.partner_id.name: order.amount_total})

        final_compare_partner_list = []
        final_compare_partner_amount_list = []
        if partner_total_amount_dic:
            # sort compare partner dictionary by descending order
            sorted_partner_total_amount_list = sorted(
                partner_total_amount_dic.items(), key=operator.itemgetter(1), reverse=True)

            counter = 0
            for tuple_item in sorted_partner_total_amount_list:
                if data['amount_total'] != 0 and tuple_item[1] >= data['amount_total']:
                    final_compare_partner_list.append(tuple_item[0])
                elif data['amount_total'] == 0:
                    final_compare_partner_list.append(tuple_item[0])

                final_compare_partner_amount_list.append(tuple_item[1])
                # only show record by user limit
                counter += 1
                if counter >= data['no_of_top_item']:
                    break

        # find lost and new partner here
        lost_partner_list = []
        new_partner_list = []
        if final_partner_list and final_compare_partner_list:
            for item in final_partner_list:
                if item not in final_compare_partner_list:
                    lost_partner_list.append(item)

            for item in final_compare_partner_list:
                if item not in final_partner_list:
                    new_partner_list.append(item)

#       finally update data dictionary
        if not currency_id:
            self.env.company.sudo().currency_id
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        basic_start_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.date_from),
                                                                                 DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        basic_end_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.date_to),
                                                                               DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        compare_start_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.date_compare_from),
                                                                                   DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        compare_end_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.date_compare_to),
                                                                                 DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        if self.type == 'basic':
            row = 1
            worksheet = workbook.add_sheet(
                u'Top Customers', cell_overwrite_ok=True)
            worksheet.write_merge(0, 1, 0, 2, 'Top Customers', heading_format)
            worksheet.write(3, 0, 'Date From: ', bold)
            worksheet.write(3, 1, basic_start_date)

            worksheet.write(4, 0, 'Date To: ', bold)
            worksheet.write(4, 1, basic_end_date)
            worksheet.col(0).width = int(25*260)
            worksheet.col(1).width = int(25*260)
            worksheet.col(2).width = int(14*260)
            row = 6
            worksheet.write(row, 0, "#", bold)
            worksheet.write(row, 1, "Customer", bold)
            worksheet.write(row, 2, "POS Amount", bold)
            no = 0
            row = 7
            for i in range(len(final_partner_list)):
                no = no+1
                worksheet.write(row, 0, no, left)
                worksheet.write(
                    row, 1, final_partner_list[i] if final_partner_list[i] else "", left)
                worksheet.write(row, 2, final_partner_amount_list[i], left)
                row = row+1
        elif self.type == 'compare':
            row = 1
            worksheet = workbook.add_sheet(
                u'Top Customers', cell_overwrite_ok=True)
            worksheet.write_merge(0, 1, 0, 6, 'Top Customers', heading_format)
            worksheet.write(3, 0, 'Date From: ', bold)
            worksheet.write(3, 1, basic_start_date)
            worksheet.write(4, 0, 'Date To: ', bold)
            worksheet.write(4, 1, basic_end_date)
            worksheet.write(3, 5, 'Compare From Date: ', bold)
            worksheet.write(3, 6, compare_start_date)

            worksheet.write(4, 5, 'Compare To Date: ', bold)
            worksheet.write(4, 6, compare_end_date)
            row = 7
            worksheet.col(0).width = int(25*260)
            worksheet.col(1).width = int(25*260)
            worksheet.col(2).width = int(14*260)
            worksheet.col(3).width = int(25*260)
            worksheet.col(4).width = int(25*260)
            worksheet.col(5).width = int(14*260)
            worksheet.col(6).width = int(14*260)
            worksheet.write(row, 0, "#", bold)
            worksheet.write(row, 1, "Customer", bold)
            worksheet.write(row, 2, "POS Amount", bold)
            worksheet.write(row, 4, "#", bold)
            worksheet.write(row, 5, "Compare Customer", bold)
            worksheet.write(row, 6, "POS Amount", bold)
            row = 8
            for i in range(len(final_partner_list)):
                worksheet.write(row, 0, i+1, left)
                worksheet.write(row, 1, final_partner_list[i], left)
                worksheet.write(row, 2, final_partner_amount_list[i], left)
                row = row+1
            row = 8
            for j in range(len(final_compare_partner_list)):
                worksheet.write(row, 4, j+1, left)
                worksheet.write(row, 5, final_compare_partner_list[j], left)
                worksheet.write(
                    row, 6, final_compare_partner_amount_list[j], left)
                row = row+1
            row = row+2
            worksheet.write_merge(row, row, 0, 2, 'New Customers', bold_center)
            worksheet.write_merge(
                row, row, 4, 6, 'Lost Customers', bold_center)
            row = row+1
            start_row = row
            for new in new_partner_list:
                worksheet.write_merge(row, row, 0, 2, new, left)
                row = row+1
            for lost in lost_partner_list:
                worksheet.write_merge(start_row, start_row, 4, 6, lost, left)
                start_row = start_row+1

        filename = ('Top Customer Xls Report' + '.xls')
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
