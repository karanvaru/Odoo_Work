# -*- coding: utf-8 -*-
import base64
import io
import pytz
from dateutil import relativedelta

from odoo.tools.misc import xlwt
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrContractReportWizard(models.TransientModel):
    _name = "hr.contract.report.wizard"
    _description="Contract Expiry Report Wizard"

    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
    )
    month_count = fields.Integer(
        string="Contract Expiry in Month",
        default=1
    )

    def action_print_report(self):
        today_date = fields.Date.context_today(self)
        
        filename = 'Contract_Expiry_Staus_'
        filename = filename + today_date.strftime("%d/%m/%Y")

        workbook = xlwt.Workbook()
        
        header_style = xlwt.easyxf("""
            font: name Times New Roman, height 300;
            align: horiz center; font: color black; font:bold True;
        """)
        title_style_center = xlwt.easyxf("""
            align: horiz center ;font: name Times New Roman,bold off, italic off;
        """)
        title_style_left = xlwt.easyxf("""
            font: name Times New Roman, height 200;align: horiz left;
            borders:
                top_color black, bottom_color black, right_color black, left_color black,
                left thin, right thin, top thin, bottom thin;
        """)
        title_style_right = xlwt.easyxf("""
            font: name Times New Roman, height 200;align: horiz right;
            borders:
                top_color black, bottom_color black, right_color black, left_color black,
                left thin, right thin, top thin, bottom thin;
        """)
        title_style_right_date = xlwt.easyxf("""
            font: name Times New Roman, height 200;align: horiz right;
            borders:
                top_color black, bottom_color black, right_color black, left_color black,
                left thin, right thin, top thin, bottom thin;
        """, num_format_str='DD/MM/YYYY')
        title_style1_table_head_left = xlwt.easyxf("""
            align: horiz left ;
            font: name Times New Roman,bold on, italic off, height 200;
            pattern: pattern solid, fore_color gray25;
            borders:
                top_color black, bottom_color black, right_color black, left_color black,
                left thin, right thin, top thin, bottom thin;
        """)

        sheet = workbook.add_sheet('sheet1')

        label = 'Contract Expiry In %s Month' %(self.month_count)
        
        row = 0
        sheet.write_merge(row, row + 1, 0, 6, label, header_style)
        
        row += 2
        
        sheet.write(row, 0, 'Report Date:')
        sheet.write(row, 1, today_date, title_style_right_date)

        end_date = today_date + relativedelta.relativedelta(months=self.month_count)

        domain = [
            ('state', '=',  'open'),
            ('date_end', '<=', end_date),
            ('date_end', '>', today_date),
        ]

        if self.company_ids:
            domain = domain + [('company_id', 'in', self.company_ids.ids)]

        contract_ids = self.env['hr.contract'].sudo().search(domain)

        row += 2

        # Print Headers
        head_col = 0
        sheet.write(row , head_col, "#", title_style1_table_head_left)
        head_col += 1
        sheet.write(row , head_col, "Employee", title_style1_table_head_left)
        head_col += 1
        sheet.write(row , head_col, "Department", title_style1_table_head_left)
        head_col += 1
        sheet.write(row , head_col, "Job Position", title_style1_table_head_left)
        head_col += 1
        sheet.write(row , head_col, "Company", title_style1_table_head_left)
        head_col += 1
        sheet.write(row , head_col, "Start Date", title_style1_table_head_left)
        head_col += 1
        sheet.write(row , head_col, "End Date", title_style1_table_head_left)
        head_col += 1
        sheet.write(row , head_col, "Expiry In (Days)", title_style1_table_head_left)

        # Print Lines
        row += 1
        contract_count = 1
        for contract in contract_ids:
            employee_id = contract.employee_id
            col = 0
            sheet.write(row , col, contract_count, title_style_right)
            col += 1
            sheet.write(row , col, employee_id.name, title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row , col, contract.department_id.name or employee_id.department_id.name, title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row , col, contract.job_id.name or employee_id.job_id.name, title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row , col, employee_id.company_id.name, title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row , col, contract.date_start, title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            sheet.write(row , col, contract.date_end, title_style_right_date)
            sheet.col(col).width = 4000
            col += 1
            
            expiry_days = (contract.date_end - today_date).days
            sheet.write(row , col, expiry_days, title_style_right)

            row += 1
            contract_count += 1

        stream = io.BytesIO()
        
        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name' : filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()


class ExcelReport(models.TransientModel):
    _name = 'excel.export.document'

    name = fields.Char('File Name', size=256, readonly=True)
    filename = fields.Binary('File to Download', readonly=True)
    extension = fields.Char('Extension', default='xls')

    @api.model
    def download(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/document?model=%s&field=filename&id=%s&filename=%s.%s' % (
                self._name, self.id, self.name, self.extension
            ),
            'target': 'self'
        }
        
