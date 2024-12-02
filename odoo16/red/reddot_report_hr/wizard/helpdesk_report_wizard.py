from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import base64
import io
import pytz
from datetime import date, timedelta
from xlwt import easyxf
from bs4 import BeautifulSoup


class HelpdeskReportWizard(models.TransientModel):
    _name = "helpdesk.report.wizard"

    start_date = fields.Date(
        string='Start Date:',
        required=True,
        default=fields.Date.today()
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.today()
    )
    stage_id = fields.Many2one(
        'helpdesk.stage',
        string="Stage"
    )

    company_ids = fields.Many2many(
        'res.company',
        string="Company",
    )
    user_ids = fields.Many2many(
        'res.users',
        string='Users',
    )
    report_type = fields.Selection(
        selection=[
            ('summary', 'Summary'),
            ('detailed', 'Detailed'),
        ],
        required=True,
        default="detailed"
    )

    report_type_dct = {
        'detailed': 'Detailed',
        'summary': 'Summary',
    }

    def get_plain_text(self, html_content):
        if not html_content:
            return
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text()

    def action_print_report(self):
        today_date = fields.Date.context_today(self)
        filename = 'helpdesk_Report'
        filename = filename + '_' + today_date.strftime("%d/%m/%Y")
        workbook = xlwt.Workbook()

        header_style = xlwt.easyxf(
            "font: height 00,name Arial; align: horiz center, vert center;font: color black; font:bold True; ")

        title_style1_table_head_left = xlwt.easyxf("""
                                        align: horiz left ;font: color black; font:bold True;font: name Times New Roman,italic off, height 200;
                                          pattern: pattern solid, fore_color gray25;

                                        borders:
                                            top_color black, bottom_color black, right_color black, left_color black,
                                            left thin, right thin, top thin, bottom thin; 
                                    """)
        total_value_style = xlwt.easyxf("""
                                           font:name Times New Roman, height 200;align: horiz right;align: horiz left;
                                           borders:
                                               top_color black, bottom_color black, right_color black, left_color black,
                                               left thin, right thin, top thin, bottom thin; 
                                       """)

        total_value_count_style = xlwt.easyxf("""
                                             font:name Times New Roman, height 200;align: horiz right;align: horiz right;
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

        sheet = workbook.add_sheet('sheet1')

        if self.report_type == 'summary':
            label = 'Helpdesk Summary Report'
        if self.report_type == 'detailed':
            label = 'Helpdesk Detail Report'

        row = 0
        sheet.write_merge(row, row + 1, 0, 10, label, header_style)
        sheet.row(row).height = 300

        row += 3

        sheet.write(row, 1, "Start Date", title_style1_table_head_left)
        sheet.write(row, 2, self.start_date, title_style_right_date)

        sheet.write(row, 4, "End Date", title_style1_table_head_left)
        sheet.write(row, 5, self.end_date, title_style_right_date)

        sheet.write(row, 7, "Stage", title_style1_table_head_left)
        sheet.write(row, 8, self.stage_id.name or 'All', title_style_right_date)

        filter_user = 'All'
        filter_company = 'All'

        if self.user_ids:
            filter_user = '\n'.join([i.name for i in self.user_ids])

        if self.company_ids:
            filter_company = '\n'.join([i.name for i in self.company_ids])
        row += 2
        sheet.write(row, 1, "Users", title_style1_table_head_left)
        sheet.write(row, 2, filter_user or '', title_style_right_date)

        sheet.write(row, 4, "Companies", title_style1_table_head_left)
        sheet.write(row, 5, filter_company or '', title_style_right_date)

        sheet.write(row, 7, "Type", title_style1_table_head_left)
        sheet.write(row, 8, self.report_type_dct[self.report_type] or '', title_style_right_date)
        domain = [
            ('create_date', '>=', self.start_date),
            ('create_date', '<=', self.end_date),
        ]
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))

        if self.user_ids:
            domain.append(('user_id', 'in', self.user_ids.ids))

        if self.stage_id:
            domain.append(('stage_id', '=', self.stage_id.id))

        head_col = 1
        row += 3

        total = 0
        stage_domain = []
        if self.stage_id:
            stage_domain.append(('id', '=', self.stage_id.id))
        stage = self.env['helpdesk.stage'].sudo().search(stage_domain)
        ticket = self.env['helpdesk.ticket'].sudo().search(domain)
        sheet.write(row, head_col, 'Total', title_style1_table_head_left)
        stage_dct = {}
        for stag in stage:
            if stag not in stage_dct:
                stage_dct[stag] = 0
        for rec in ticket:
            stage_dct[rec.stage_id] += 1
        for rec in stage_dct:
            head_col += 1
            sheet.write(row, head_col, rec.name, title_style1_table_head_left)
            sheet.write(row + 1, head_col, stage_dct[rec], total_value_count_style)
            total += stage_dct[rec]
        sheet.write(row + 1, 1, total, total_value_count_style)
        row += 2

        if self.report_type == 'detailed':
            table_row = row + 3
            table_head_col = 1
            sheet.write(table_row, table_head_col, "#", title_style1_table_head_left)
            sheet.write(table_row, table_head_col + 1, "Company", title_style1_table_head_left)
            sheet.write(table_row, table_head_col + 2, "User", title_style1_table_head_left)
            sheet.write(table_row, table_head_col + 3, "Ticket Desc", title_style1_table_head_left)
            sheet.write(table_row, table_head_col + 4, "Date Assign", title_style1_table_head_left)
            sheet.write(table_row, table_head_col + 5, "Status", title_style1_table_head_left)

            ticket_count = 1
            table_row += 1
            for rec in ticket:
                sheet.write(table_row, table_head_col, ticket_count, total_value_count_style)
                sheet.write(table_row, table_head_col + 1, rec.company_id.name, total_value_style)
                sheet.col(table_head_col + 1).width = 5000
                sheet.write(table_row, table_head_col + 2, rec.user_id.name or '', total_value_style)
                sheet.col(table_head_col + 2).width = 5000
                sheet.write(table_row, table_head_col + 3, self.get_plain_text(rec.description) or '',
                            total_value_style)
                sheet.col(table_head_col + 3).width = 6000
                sheet.write(table_row, table_head_col + 4, rec.assign_date or '', title_style_right_date)
                sheet.col(table_head_col + 4).width = 5000
                sheet.write(table_row, table_head_col + 5, rec.stage_id.name, total_value_style)
                sheet.col(table_head_col + 5).width = 5000
                ticket_count += 1
                table_row += 1

        if self.report_type == 'summary':
            # stage_dct = {}
            # for stag in stage:
            #     if stag not in stage_dct:
            #         stage_dct[stag] = 0

            summary_ticket_dct = {}
            for rec in ticket:
                if rec.company_id not in summary_ticket_dct:
                    summary_ticket_dct[rec.company_id] = {}
                if rec.user_id not in summary_ticket_dct[rec.company_id]:
                    summary_ticket_dct[rec.company_id][rec.user_id] = {}
                for stages in stage_dct:
                    if stages not in summary_ticket_dct[rec.company_id][rec.user_id]:
                        summary_ticket_dct[rec.company_id][rec.user_id][stages] = 0
                summary_ticket_dct[rec.company_id][rec.user_id][rec.stage_id] += 1
            table_row = row + 2
            table_head_col = 1
            sheet.write(table_row, table_head_col, "#", title_style1_table_head_left)
            sheet.write(table_row, table_head_col + 1, "Company", title_style1_table_head_left)
            sheet.write(table_row, table_head_col + 2, "User", title_style1_table_head_left)
            table_head_col += 3
            for stag in stage_dct:
                sheet.write(table_row, table_head_col, stag.name, title_style1_table_head_left)
                table_head_col += 1
            sheet.write(table_row, table_head_col, "Total", title_style1_table_head_left)
            summary_ticket_count = 1

            for val in summary_ticket_dct:
                table_row += 1
                for user in summary_ticket_dct[val]:
                    table_head_col = 1
                    if user.name != False:
                        stage_wise_total = 0
                        sheet.write(table_row, table_head_col, summary_ticket_count, total_value_count_style)
                        sheet.write(table_row, table_head_col + 1, val.name, total_value_style)
                        sheet.write(table_row, table_head_col + 2, user.name, total_value_style)
                        table_head_col += 3
                        for count in summary_ticket_dct[val][user]:
                            sheet.write(table_row, table_head_col, summary_ticket_dct[val][user][count],
                                        total_value_count_style)
                            table_head_col += 1
                            stage_wise_total += summary_ticket_dct[val][user][count]
                        sheet.write(table_row, table_head_col, stage_wise_total, total_value_count_style)
                        table_row += 1
                        summary_ticket_count += 1

        stream = io.BytesIO()
        workbook.save(stream)
        attach_id = self.env['excel.export.document'].create({
            'name': filename,
            'filename': base64.encodebytes(stream.getvalue())
        })
        return attach_id.download()
