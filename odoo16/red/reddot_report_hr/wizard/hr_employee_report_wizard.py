# -*- coding: utf-8 -*-
import base64
import io
import pytz
from dateutil import relativedelta

from odoo.tools.misc import xlwt
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

FIELD_LIST = [
    'birthday',
    'create_date',
    'departure_date',
    'first_contract_date',
    'id_expiry_date',
    'joining_date',
    'last_appraisal_date',
    'passport_expiry_date',
    'probation_renewal_date',
    'visa_expire',
    'work_permit_expiration_date',
]


class HrEmployeeReportWizard(models.TransientModel):
    _name = "hr.employee.report.wizard"

    @api.model
    def _get_field_domain(self):
        domain = [
            ('model', '=', 'hr.employee'),
            ('name', 'in', FIELD_LIST)
        ]
        return domain

    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
    )
    month_count = fields.Integer(
        string="Date Range In Month",
        default=1
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string="Date Type",
        domain=_get_field_domain,
        required=True
    )

    def action_print_report(self):
        today_date = fields.Date.context_today(self)

        filename = self.field_id.field_description.replace(" ", '_') + '_Staus_'
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

        label = self.field_id.field_description + ' In %s Month' % (self.month_count)

        row = 0
        sheet.write_merge(row, row + 1, 0, 6, label, header_style)

        row += 2

        sheet.write(row, 0, 'Report Date:')
        sheet.write(row, 1, today_date, title_style_right_date)

        end_date = today_date + relativedelta.relativedelta(months=self.month_count)

        if end_date < today_date:
            domain = [
                (self.field_id.name, '>=', end_date),
                (self.field_id.name, '<', today_date),
            ]
        else:
            domain = [
                (self.field_id.name, '<=', end_date),
                (self.field_id.name, '>', today_date),
            ]

        if self.company_ids:
            domain = domain + [('company_id', 'in', self.company_ids.ids)]

        field_list = [
            'name',
            'department_id',
            'job_id',
            'company_id',
            self.field_id.name
        ]

        employee_results = self.env['hr.employee'].sudo().search_read(
            domain,
            field_list
        )
        row += 2

        # Print Headers
        head_col = 0
        sheet.write(row, head_col, "#", title_style1_table_head_left)
        head_col += 1
        sheet.write(row, head_col, "Employee", title_style1_table_head_left)
        head_col += 1
        sheet.write(row, head_col, "Department", title_style1_table_head_left)
        head_col += 1
        sheet.write(row, head_col, "Job Position", title_style1_table_head_left)
        head_col += 1
        sheet.write(row, head_col, "Company", title_style1_table_head_left)
        head_col += 1
        sheet.write(row, head_col, self.field_id.field_description, title_style1_table_head_left)
        head_col += 1
        colum_value = '{} In (Days)'.format(self.field_id.field_description)

        sheet.write(row, head_col, colum_value, title_style1_table_head_left)

        # Print Lines
        row += 1
        contract_count = 1
        for employee in employee_results:
            col = 0
            sheet.write(row, col, contract_count, title_style_right)
            col += 1
            sheet.write(row, col, employee['name'], title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, employee['department_id'] and employee['department_id'][1] or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, employee['job_id'] and employee['job_id'][1] or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, employee['company_id'] and employee['company_id'][1] or '', title_style_left)
            sheet.col(col).width = 6000
            col += 1
            sheet.write(row, col, employee[self.field_id.name], title_style_right_date)
            sheet.col(col).width = 4000
            col += 1

            expiry_days = (employee[self.field_id.name] - today_date).days
            sheet.write(row, col, expiry_days, title_style_right)

            row += 1
            contract_count += 1

        stream = io.BytesIO()

        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()
