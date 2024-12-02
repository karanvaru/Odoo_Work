# -*- coding: utf-8 -*-
import base64
import io
from odoo.tools.misc import xlwt
from odoo import models, fields, api, _


class LeaveWizardReport(models.TransientModel):
    _name = "leave.wizard.report"

    start_date = fields.Date(
        string='Start Date:',
        required=True,
    )
    #     end_date = fields.Date(
    #         string='End Date',
    #         required=False,
    #     )
    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
    )

    department_ids = fields.Many2many(
        "hr.department",
        string="Departments",
    )
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employees",
    )
    # holiday_status_id = fields.Many2one(
    #     'hr.leave.type',
    #     string="Leave Type"
    # )
    holiday_status_id = fields.Many2many(
        'hr.leave.type',
        string="Leave Type"
    )

    report_type = fields.Selection(
        selection=[
            ('detailed', 'Detailed'),
            ('summary', 'Summary'),
        ],
        required=True,
        default="detailed"
    )

    @api.model
    def default_get(self, default_fields):
        vals = super(LeaveWizardReport, self).default_get(default_fields)
        if self._context.get('from_anual_menu'):
            leave_type = self.env['hr.leave.type'].sudo().search([('is_anual_type', '=', True)])
            if leave_type:
                vals['holiday_status_id'] = leave_type.ids
        return vals

    def action_print_report(self):
        today_date = fields.Date.context_today(self)
        filename = 'Leave_Report'
        filename = filename + '_' + today_date.strftime("%d/%m/%Y")
        workbook = xlwt.Workbook()
        report_type = {
            'detailed': 'Detailed',
            'summary': 'Summary'
        }
        header_style = xlwt.easyxf(
            "font: height 00,name Arial; align: horiz center, vert center;font: color black; font:bold True; ")

        title_style_left = xlwt.easyxf("""
            font: name Times New Roman, height 200;align: horiz left;
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
                                   align: horiz left ;font: color black; font:bold True;font: name Times New Roman,italic off, height 200;
                                     pattern: pattern solid, fore_color gray25;

                                   borders:
                                       top_color black, bottom_color black, right_color black, left_color black,
                                       left thin, right thin, top thin, bottom thin; 
                               """)
        total_value_style = xlwt.easyxf("""
                                      font:bold True,name Times New Roman, height 200;align: horiz right;align: horiz left;
                                      borders:
                                          top_color black, bottom_color black, right_color black, left_color black,
                                          left thin, right thin, top thin, bottom thin; 
                                  """)

        sheet = workbook.add_sheet('sheet1')
        label = 'Leave Report'

        row = 0
        sheet.write_merge(row, row + 1, 0, 10, label, header_style)
        sheet.row(row).height = 300

        domain = [
            ('date_from', '>=', self.start_date),
            #             ('date_from', '<=', self.end_date),
        ]
        if self.company_ids:
            domain.append(('employee_company_id', 'in', self.company_ids.ids))

        if self.department_ids:
            domain.append(('employee_id.department_id', 'in', self.department_ids.ids))

        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        if self.holiday_status_id:
            domain.append(('holiday_status_id', 'in', self.holiday_status_id.ids))

        leave_results = self.env['hr.leave'].sudo().search(domain)
        leave_summary_dct = {}
        for l in leave_results:
            for emp in l.all_employee_ids:
                if emp not in leave_summary_dct:
                    leave_summary_dct[emp] = {}
                if l.holiday_status_id not in leave_summary_dct[emp]:
                    leave_summary_dct[emp][l.holiday_status_id] = l.number_of_days_display
                leave_summary_dct[emp][l.holiday_status_id] += l.number_of_days_display
                if l.request_unit_half:
                    leave_summary_dct[emp][l.holiday_status_id] += 0.5

        row += 3

        sheet.write(row, 1, "Start Date", title_style1_table_head_left)
        sheet.write(row, 2, self.start_date, title_style_right_date)
        #         sheet.write(row, 5, "End Date", title_style1_table_head_left)
        #         sheet.write(row, 6, self.end_date, title_style_right_date)
        filter_leave = 'All'
        if self.holiday_status_id:
            filter_leave = '\n'.join([i.name for i in self.holiday_status_id])

        sheet.write(row, 5, "Leave Type", title_style1_table_head_left)
        sheet.write(row, 6, filter_leave or '', title_style_right_date)
        filter_company = 'All'
        filter_employee = 'All'
        filter_department = 'All'

        if self.company_ids:
            filter_company = '\n'.join([i.name for i in self.company_ids])

        if self.department_ids:
            filter_department = '\n'.join([i.name for i in self.department_ids])

        if self.employee_ids:
            filter_employee = '\n'.join([i.name for i in self.employee_ids])

        row += 1
        sheet.write(row, 1, "Companies", title_style1_table_head_left)
        sheet.write(row, 2, filter_company, title_style_right_date)
        sheet.row(row).height = 300

        row += 1
        sheet.write(row, 1, "Departments", title_style1_table_head_left)
        sheet.write(row, 2, filter_department, title_style_right_date)
        row += 1
        sheet.write(row, 1, "Employees", title_style1_table_head_left)
        sheet.write(row, 2, filter_employee, title_style_right_date)
        sheet.write(row, 5, "Report Type", title_style1_table_head_left)
        sheet.write(row, 6, report_type.get(self.report_type), title_style_right_date)
        row += 1

        head_col = 0
        row += 2
        sheet.write(row, head_col, "Employee", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Department", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, "Line Manager", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        # if self.report_type == "summary":
        sheet.write(row, head_col, "Allocated Days", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1

        sheet.write(row, head_col, "Total Taken", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1

        sheet.write(row, head_col, "Leave Type", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1

        sheet.write(row, head_col, "Start Date Leave", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'End Date Leave', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1
        sheet.write(row, head_col, 'Number of days', title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1

        # if self.report_type == "summary":
        sheet.write(row, head_col, "Balance", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        head_col += 1

        sheet.write(row, head_col, "Company", title_style1_table_head_left)
        sheet.col(head_col).width = 6000
        sheet.row(row).height = 300
        row += 1
        leave_details_dct = {}
        if self.report_type == "detailed":
            for leave in leave_results:
                for emp in leave.all_employee_ids:
                    if emp not in leave_details_dct:
                        leave_details_dct[emp] = []
                    leave_details_dct[emp].append({leave.holiday_status_id: leave.number_of_days_display})
                    if leave.request_unit_half:
                        leave_details_dct[emp].append({leave.holiday_status_id: 0.5})
        for rec in leave_details_dct:
            total_leave = 0
            for leaves in leave_details_dct[rec]:
                for re in leaves:
                    allocated = self.env['hr.leave.allocation'].sudo().search([
                        ('employee_id', '=', rec.id), ('holiday_status_id', '=', re.id)])
                    details_allocated_leaves = 0
                    for allote in allocated:
                        alloc_leave = int(allote.duration_display.split()[0])
                        details_allocated_leaves += alloc_leave
                    total_leave += leaves[re]
                    col = 0
                    sheet.write(row, col, rec.name or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, rec.department_id.name or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, rec.parent_id.name or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, details_allocated_leaves or '', title_style_left)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, leaves[re], title_style_left)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, re.name, title_style_left)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, '', title_style_right_date)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, '', title_style_right_date)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, leaves[re], title_style_left)
                    sheet.col(col).width = 4000
                    col += 1
                    details_leave_balance = details_allocated_leaves - leaves[
                        re] if details_allocated_leaves != 0 else ''
                    sheet.write(row, col, details_leave_balance, title_style_left)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, rec.company_id.name, title_style_left)
                    sheet.col(col).width = 6000
                    col += 1

                    row += 1
            total_str = 'Total For {}'.format(rec.name)
            sheet.write_merge(row, row, 0, 7, total_str, total_value_style)
            sheet.write_merge(row, row, 8, 10, total_leave, total_value_style)
            row += 1

        if self.report_type == "summary":
            for emp in leave_summary_dct:
                total_leave = 0
                for leave in leave_summary_dct[emp]:
                    allocated = self.env['hr.leave.allocation'].sudo().search([
                        ('employee_id', '=', emp.id), ('holiday_status_id', '=', leave.id)])
                    allocated_leaves = 0
                    for rec in allocated:
                        alloc_leave = int(rec.duration_display.split()[0])
                        allocated_leaves += alloc_leave
                    total_leave += leave_summary_dct[emp][leave]
                    col = 0
                    sheet.write(row, col, emp.name or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, emp.department_id.name or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, emp.parent_id.name or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1

                    sheet.write(row, col, allocated_leaves or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, leave_summary_dct[emp][leave], title_style_left)
                    sheet.col(col).width = 6000
                    col += 1

                    sheet.write(row, col, leave.name or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, '', title_style_right_date)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, '', title_style_right_date)
                    sheet.col(col).width = 4000
                    col += 1
                    sheet.write(row, col, leave_summary_dct[emp][leave] or '', title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    leave_balance = allocated_leaves - leave_summary_dct[emp][leave] if allocated_leaves != 0 else ''
                    sheet.write(row, col, leave_balance, title_style_left)
                    sheet.col(col).width = 6000
                    col += 1
                    sheet.write(row, col, emp.company_id.name, title_style_left)
                    sheet.col(col).width = 6000
                    row += 1
                total_str = 'Total For {}'.format(emp.name)
                sheet.write_merge(row, row, 0, 7, total_str, total_value_style)
                sheet.write_merge(row, row, 8, 10, total_leave, total_value_style)
                row += 1

        stream = io.BytesIO()
        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()
