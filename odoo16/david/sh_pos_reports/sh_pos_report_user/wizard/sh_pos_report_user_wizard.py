# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import io
import xlwt
import base64
from io import BytesIO
import pytz
from datetime import datetime, timedelta


class ShPosReportUserWizard(models.TransientModel):
    _name = "sh.pos.report.user.wizard"
    _description = "sh pos report user wizard model"

    @api.model
    def default_company_ids(self):
        is_allowed_companies = self.env.context.get(
            'allowed_company_ids', False)
        if is_allowed_companies:
            return is_allowed_companies
        return

    date_start = fields.Datetime(
        string="Start Date", required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(
        string="End Date", required=True, default=fields.Datetime.now)
    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="rel_sh_pos_report_user_ids",
        string="POS User")
    state = fields.Selection([
        ('all', 'All'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('invoiced', 'Invoiced'),
    ], string='Status', default='all')
    company_ids = fields.Many2many(
        'res.company', string='Companies', default=default_company_ids)
    config_ids = fields.Many2many('pos.config', string='POS Configuration')

    @api.model
    def default_get(self, fields):
        rec = super(ShPosReportUserWizard, self).default_get(fields)
        search_users = self.env["res.users"].sudo().search(
            [('company_id', 'in', self.env.context.get('allowed_company_ids', False))])
        if self.env.user.has_group('point_of_sale.group_pos_manager'):
            rec.update({
                "user_ids": [(6, 0, search_users.ids)],
            })
        else:
            rec.update({
                "user_ids": [(6, 0, search_users.ids)],
            })
        return rec

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
            raise ValidationError(_('start date must be less than end date.'))

    def print_report(self):
        datas = self.read()[0]
        return self.env.ref('sh_pos_reports.sh_pos_report_user_report').report_action([], data=datas)
    
    def display_report(self):
        datas = self.read()[0]
        report = self.env['report.sh_pos_reports.sh_user_report_doc']
        data_values = report._get_report_values(
            docids=None, data=datas).get('user_order_dic')

        if data_values:
            self.env['sh.pos.report.user'].search([]).unlink()
            for user in data_values:
                for order in data_values[user]:
                    self.env['sh.pos.report.user'].create({
                        'sh_user_id': order['user_id'],
                        'sh_partner_id': order['partner_id'],
                        'name': order['order_number'],
                        'order_date': order['order_date'],
                        'total': order['total'],
                        'amount_invoiced': order['paid_amount'],
                        'amount_due': order['due_amount']
                    })
            return {
                'type': 'ir.actions.act_window',
                'name': 'POS Report By POS User',
                'view_mode': 'tree',
                'res_model': 'sh.pos.report.user',
                'context': "{'create': False,'search_default_group_user': 1}"
            }

    def print_xls_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        heading_format = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold = xlwt.easyxf(
            'font:bold True,height 215;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold_center = xlwt.easyxf(
            'font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;')
        worksheet = workbook.add_sheet('POS Report by POS User', bold_center)
        worksheet.write_merge(
            0, 1, 0, 5, 'POS Report by POS User', heading_format)
        left = xlwt.easyxf('align: horiz center;font:bold True')
        date_start = False
        date_stop = False
        if self.date_start:
            date_start = fields.Datetime.from_string(self.date_start)
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get(
                'tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(
                fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if self.date_end:
            date_stop = fields.Datetime.from_string(self.date_end)
            # avoid a date_stop smaller than date_start
            if (date_stop < date_start):
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        start_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.date_start),
                                                                           DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.date_end),
                                                                         DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        worksheet.write_merge(2, 2, 0, 5, start_date + " to " + end_date, bold)
        worksheet.col(0).width = int(30 * 260)
        worksheet.col(1).width = int(30 * 260)
        worksheet.col(2).width = int(18 * 260)
        worksheet.col(3).width = int(18 * 260)
        worksheet.col(4).width = int(33 * 260)
        worksheet.col(5).width = int(15 * 260)
        row = 4
        for user_id in self.user_ids:
            row = row + 2
            worksheet.write_merge(
                row, row, 0, 5, "POS User: " + user_id.name, bold_center)
            row = row + 2
            worksheet.write(row, 0, "Order Number", bold)
            worksheet.write(row, 1, "Order Date", bold)
            worksheet.write(row, 2, "Customer", bold)
            worksheet.write(row, 3, "Total", bold)
            worksheet.write(row, 4, "Amount Invoiced", bold)
            worksheet.write(row, 5, "Amount Due", bold)
            if self.state == 'all':
                sum_of_amount_total = 0.0
                total_invoice_amount = 0.0
                total_due_amount = 0.0
                domain = [
                    ("date_order", ">=", fields.Datetime.to_string(date_start)),
                    ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                    ("user_id", "=", user_id.id)
                ]
                if self.company_ids:
                    domain.append(('company_id', 'in', self.company_ids.ids))
                if self.config_ids:
                    session_ids = self.env['pos.session'].sudo().search(
                        [('config_id', 'in', self.config_ids.ids)])
                    domain.append(('session_id', 'in', session_ids.ids))
                for pos_order in self.env['pos.order'].sudo().search(domain):
                    row = row + 1
                    sum_of_amount_total = sum_of_amount_total + pos_order.amount_total
                    sum_of_invoice_amount = 0.0
                    sum_of_due_amount = 0.0
                    if pos_order.account_move:
                        for invoice_id in pos_order.account_move.filtered(lambda inv: inv.state not in ['cancel', 'draft']):
                            sum_of_invoice_amount += invoice_id.amount_total_signed
                            sum_of_due_amount += invoice_id.amount_residual_signed
                            total_invoice_amount += invoice_id.amount_total_signed
                            total_due_amount += invoice_id.amount_residual_signed
                    worksheet.write(row, 0, pos_order.name)
                    order_date = fields.Datetime.to_string(
                        pos_order.date_order)
                    date_order = datetime.strftime(pytz.utc.localize(datetime.strptime(order_date,
                                                                                       DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
                    worksheet.write(row, 1, date_order)
                    worksheet.write(row, 2, pos_order.partner_id.name)
                    worksheet.write(row, 3, pos_order.amount_total)
                    worksheet.write(row, 4, sum_of_invoice_amount)
                    worksheet.write(row, 5, sum_of_due_amount)
                row = row + 1
                worksheet.write(row, 2, "Total", left)
                worksheet.write(row, 3, sum_of_amount_total)
                worksheet.write(row, 4, total_invoice_amount)
                worksheet.write(row, 5, total_due_amount)
            elif self.state == 'done':
                sum_of_amount_total = 0.0
                total_invoice_amount = 0.0
                total_due_amount = 0.0
                domain = [
                    ("date_order", ">=", fields.Datetime.to_string(date_start)),
                    ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                    ("user_id", "=", user_id.id)
                ]
                domain.append(('state', 'in', ['paid', 'done', 'invoiced']))
                if self.company_ids:
                    domain.append(('company_id', 'in', self.company_ids.ids))
                if self.config_ids:
                    session_ids = self.env['pos.session'].sudo().search(
                        [('config_id', 'in', self.config_ids.ids)])
                    domain.append(('session_id', 'in', session_ids.ids))
                for pos_order in self.env['pos.order'].sudo().search(domain):
                    row = row + 1
                    sum_of_amount_total = sum_of_amount_total + pos_order.amount_total
                    sum_of_invoice_amount = 0.0
                    sum_of_due_amount = 0.0
                    if pos_order.account_move:
                        for invoice_id in pos_order.account_move.filtered(lambda inv: inv.state not in ['cancel', 'draft']):
                            sum_of_invoice_amount += invoice_id.amount_total_signed
                            sum_of_due_amount += invoice_id.residual_signed
                            total_invoice_amount += invoice_id.amount_total_signed
                            total_due_amount += invoice_id.residual_signed
                    worksheet.write(row, 0, pos_order.name)
                    order_date = fields.Datetime.to_string(
                        pos_order.date_order)
                    date_order = datetime.strftime(pytz.utc.localize(datetime.strptime(order_date,
                                                                                       DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
                    worksheet.write(row, 1, date_order)
                    worksheet.write(row, 2, pos_order.partner_id.name)
                    worksheet.write(row, 3, pos_order.amount_total)
                    worksheet.write(row, 4, sum_of_invoice_amount)
                    worksheet.write(row, 5, sum_of_due_amount)
                row = row + 1
                worksheet.write(row, 2, "Total", left)
                worksheet.write(row, 3, sum_of_amount_total)
                worksheet.write(row, 4, total_invoice_amount)
                worksheet.write(row, 5, total_due_amount)
        filename = ('POS By POS User Xls Report' + '.xls')
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
