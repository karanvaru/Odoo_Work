from odoo import fields, models

import base64
import xlwt
import io
from xlwt import easyxf
import io
import xlsxwriter
import base64
from PIL import Image


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def export_excel(self):
        filename = 'Purchase_Report.xlsx'

        # Create a BytesIO buffer for the workbook
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        sheet1 = workbook.add_worksheet('Purchase Report')

        head_format = workbook.add_format({
            'font_size': 8,
            'align': 'left',
            'font_color': 'black',
            'bold': True,
            'border': 1
        })

        value_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'font_color': 'black',
            'border': 1
        })

        header_value = workbook.add_format({
            'bold': True,
            'font_size': 8,
            'font_color': 'black',
            'bg_color': '#C0C0C0',
            'border': 1
        })

        header_center_value = workbook.add_format({
            'align': 'center',
            'font_size': 9,
            'bold': True,
            'font_color': 'black',
            'bg_color': '#C0C0C0',
            'border': 1
        })

        value_format_green = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': 9,
            'font_color': 'black',
            'bg_color': '#92D050',
            'border': 1
        })

        value_format_green_dark = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_color': 'black',
            'bg_color': '#D8E4BC',
            'border': 1,
            'font_size': 8,
        })
        new_head_format = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'bold': True,
            'font_color': 'black',
            'border': 2,
            'valign': 'vcenter',
            'border': 1
        })

        date_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'bg_color': '#92D050',
            'border': 1,
            'num_format': 'dd/mm/yyyy'
        })

        im = Image.open(io.BytesIO(base64.b64decode(self.env.user.company_id.logo))).convert("RGB")
        im = im.resize((281, 75))
        im.save('/tmp/image.jpg', quality=400)
        sheet1.insert_image('A1:B2', '/tmp/image.jpg', {'x_scale': 0.62, 'y_scale': 0.8})
        sheet1.merge_range(0, 2, 2, 8, 'EAST, META & CSEE Manual Order Form ', new_head_format)

        row_header = 3
        sheet1.merge_range(row_header, 2, row_header, 5, 'Purchase Order Number:',head_format )
        sheet1.merge_range(row_header, 6, row_header, 8, self.name, value_format_green)

        sheet1.merge_range(row_header + 1, 2, row_header + 1, 5, 'Order Date:', head_format)
        sheet1.merge_range(row_header + 1, 6, row_header + 1, 8, self.date_order, date_format)

        sheet1.merge_range(row_header + 2, 2, row_header + 2, 5, 'Requested Delivery Date (CRAD):', head_format)
        sheet1.merge_range(row_header + 2, 6, row_header + 2, 8, self.date_planned, date_format)
        sheet1.merge_range(row_header + 3, 2, row_header + 3, 5, 'Distribution Channel:', head_format)
        sheet1.merge_range(row_header + 3, 6, row_header + 3, 8, '81 - SMB', value_format_green)
        sheet1.merge_range(row_header + 4, 2, row_header + 4, 5, 'Division:', head_format)
        sheet1.merge_range(row_header + 4, 6, row_header + 4, 8, '93 - THINK', value_format_green)


        sheet1.set_column(0, 0, 15)
        sheet1.write(row_header + 6, 0, 'Ship To ID:', header_value)
        sheet1.write(row_header + 7, 0, 'Ship To Address:', head_format)
        sheet1.write(row_header + 8, 0, 'Company Name:', head_format)
        sheet1.write(row_header + 9, 0, 'Company Address:', head_format)

        sheet1.merge_range(row_header + 6, 1, row_header + 6, 3, self.partner_id.phone, value_format_green)
        sheet1.merge_range(row_header + 7, 1, row_header + 7, 3, self.partner_id.street,
                           value_format_green_dark)
        sheet1.merge_range(row_header + 8, 1, row_header + 8, 3, self.partner_id.company_id.name or '',
                           value_format_green_dark)
        sheet1.merge_range(row_header + 9, 1, row_header + 9, 3, self.partner_id.company_id.street or '',
                           value_format_green_dark)

        sheet1.set_column(5, 5, 15)
        sheet1.write(row_header + 6, 5, 'Sold To ID:', header_value)
        sheet1.write(row_header + 7, 5, 'Sold To Address:', head_format)
        sheet1.write(row_header + 8, 5, 'Company Name:', head_format)
        sheet1.write(row_header + 9, 5, 'Company Address:', head_format)

        sheet1.merge_range(row_header + 6, 6, row_header + 6, 8, self.partner_id.phone, value_format_green)
        sheet1.merge_range(row_header + 7, 6, row_header + 7, 8, self.partner_id.street,
                           value_format_green_dark)
        sheet1.merge_range(row_header + 8, 6, row_header + 8, 8, self.partner_id.company_id.name or '',
                           value_format_green_dark)
        sheet1.merge_range(row_header + 9, 6, row_header + 9, 8, self.partner_id.company_id.street or '',
                           value_format_green_dark)

        sheet1.merge_range(row_header + 11, 0, row_header + 11, 3,
                           'Contact for Delivery / Warranty contact information', header_center_value)
        sheet1.write(row_header + 12, 0, 'Name:', head_format)
        sheet1.write(row_header + 13, 0, 'Email:', head_format)
        sheet1.write(row_header + 14, 0, 'Phone:', head_format)

        sheet1.merge_range(row_header + 12, 1, row_header + 12, 3, self.user_id.name, value_format)
        sheet1.merge_range(row_header + 13, 1, row_header + 13, 3, self.user_id.email, value_format)
        sheet1.merge_range(row_header + 14, 1, row_header + 14, 3, self.user_id.phone, value_format)

        sheet1.set_column(5, 5, 15)
        sheet1.write(row_header + 11, 5, 'Bill To ID:', header_value)
        sheet1.write(row_header + 12, 5, 'Bill To Address:', head_format)
        sheet1.write(row_header + 13, 5, 'Company Name:', head_format)
        sheet1.write(row_header + 14, 5, 'Company Address:', head_format)

        sheet1.merge_range(row_header + 11, 6, row_header + 11, 8, self.partner_id.phone, value_format_green)
        sheet1.merge_range(row_header + 12, 6, row_header + 12, 8, self.partner_id.street,
                           value_format_green_dark)
        sheet1.merge_range(row_header + 13, 6, row_header + 13, 8, self.partner_id.company_id.name or '',
                           value_format_green_dark)
        sheet1.merge_range(row_header + 14, 6, row_header + 14, 8, self.partner_id.company_id.street or '',
                           value_format_green_dark)

        sheet1.merge_range(row_header + 16, 0, row_header + 16, 3,
                           'Lenovo price information', header_center_value)
        sheet1.write(row_header + 17, 0, 'MCN/ Contract ID:', head_format)
        sheet1.merge_range(row_header + 17, 1, row_header + 17, 3, 'N/A', value_format_green)

        sheet1.merge_range(row_header + 19, 0, row_header + 19, 8, 'Product Information', header_center_value)

        sheet1.merge_range(row_header + 20, 0, row_header + 20, 1, 'PN - Part Number', value_format_green)
        sheet1.merge_range(row_header + 20, 2, row_header + 20, 4, 'Product Description', value_format_green)
        sheet1.write(row_header + 20, 5, 'Qty', value_format_green)
        sheet1.write(row_header + 20, 6, 'Unit Price', value_format_green)
        sheet1.merge_range(row_header + 20, 7, row_header + 20, 8, 'Total Price', value_format_green)

        table_row = row_header + 21
        line_subtotal = 0.0
        for line in self.order_line:
            sheet1.merge_range(table_row, 0, table_row, 1, line.product_id.default_code, value_format)
            sheet1.merge_range(table_row, 2, table_row, 4, line.name, value_format)
            sheet1.write(table_row, 5, line.product_qty, value_format)
            sheet1.write(table_row, 6, line.price_unit, value_format)
            sheet1.merge_range(table_row, 7, table_row, 8, line.price_subtotal, value_format)
            line_subtotal += line.price_subtotal
            table_row += 1
        sheet1.merge_range(table_row, 7, table_row, 8, line_subtotal, value_format_green)

        sheet1.write(table_row + 1, 0, 'Shipping mode', header_value)
        sheet1.merge_range(table_row + 1, 1, table_row + 1, 3, 'Ocean', value_format_green)

        sheet1.write(table_row + 3, 0, 'Special Requirements:', header_value)
        sheet1.merge_range(table_row + 3,1, table_row + 3,  3, 'NO PARTIAL SHIPMENTS ALLOWED.', head_format)

        workbook.close()

        fp.seek(0)
        report_id = self.env['excel.report'].create({
            'excel_file': base64.encodebytes(fp.read()),
            'file_name': filename
        })
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': report_id.id,
            'res_model': 'excel.report',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class ExcelReport(models.TransientModel):
    _name = 'excel.report'

    file_name = fields.Char(
        'Excel File',
        size=64,
        readonly=True,
    )

    excel_file = fields.Binary(
        'Download Report',
        readonly=True,
    )
