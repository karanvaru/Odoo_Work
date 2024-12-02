from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import base64
import io

from xlwt import easyxf


class ExportProduct(models.TransientModel):
    _name = "wiz.sale.shop.product.export"
    _description = "Export Product"
    shop_id = fields.Many2one(
        'sale.shop',
        string="Shop",
        required=True,
        readonly=True
    )
    product_public_category_id = fields.Many2one(
        'product.public.category',
        string="Channel Category",
        required=True
    )
    need_stock_qty = fields.Boolean(
        string="with Stock Qty",
        default=True
    )
    qty_type = fields.Selection([('on_hand', 'On Hand'), ('forcasted', 'Forcasted')],
                                string='Qty Type'
                                )
    warehouse_type = fields.Selection([('all_warehouse', 'All Warehouse'), ('shop_warehouse', 'Shop Warehouse')],
                                      string='Warehouse'
                                      )

    @api.model
    def default_get(self, field_list):
        res = super(ExportProduct, self).default_get(field_list)
        shop = self._context.get('active_id', False)
        res.update({
            'shop_id': shop,
        })
        return res

    def export_product(self):
        filename = 'Export Product.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        sheet1 = workbook.add_sheet('Exprot PRoduct Report')
        domain = [
            ('shop_id', '=', self.shop_id.id),
            ('product_public_category_id', '=', self.product_public_category_id.id)
        ]

        record_ids = self.env['sale.shop.product'].search(domain)
        formate_2 = xlwt.easyxf("font: bold 1, color black ;align: horiz center")

        row_index = 0
        sheet1.write(row_index, 0, "Base Product", formate_2)
        sheet1.write(row_index, 1, "Name", formate_2)
        sheet1.write(row_index, 2, "SKU", formate_2)
        sheet1.write(row_index, 3, "Sales Price", formate_2)
        sheet1.write(row_index, 4, "MRP", formate_2)
        sheet1.write(row_index, 5, "Unit of Measure", formate_2)
        sheet1.write(row_index, 6, "Inventory", formate_2)
        sheet1.write(row_index, 7, "HSN ID", formate_2)
        sheet1.write(row_index, 8, "Size", formate_2)
        sheet1.write(row_index, 9, "GST %", formate_2)
        sheet1.write(row_index, 10, "Color", formate_2)
        sheet1.write(row_index, 11, "Product weight (gms)", formate_2)
        sheet1.write(row_index, 12, "Country of Origin", formate_2)

        # print("records_ids", record_ids)
        for rec in record_ids:
            row_index += 1
            sheet1.write(row_index, 0, rec.product_id.name)
            sheet1.write(row_index, 1, rec.name)
            sheet1.write(row_index, 2, rec.default_code)
            sheet1.write(row_index, 3, rec.list_price)
            sheet1.write(row_index, 4, rec.product_id.standard_price)
            sheet1.write(row_index, 5, rec.uom_id.name)
            qty = 0
            if self.need_stock_qty:
                if self.qty_type == "on_hand":
                    if self.warehouse_type == "shop_warehouse":
                        qty = rec.product_id.with_context(warehouse=rec.shop_id.default_warehouse_id.id).qty_available
                    else:
                        qty = rec.product_id.qty_available
                if self.qty_type == "forcasted":
                    if self.warehouse_type == "shop_warehouse":
                        qty = rec.product_id.with_context(
                            warehouse=rec.shop_id.default_warehouse_id.id).virtual_available
                    else:
                        qty = rec.product_id.virtual_available
            sheet1.write(row_index, 6, qty)
            sheet1.write(row_index, 7, rec.product_id.l10n_in_hsn_code)
            sheet1.write(row_index, 8, rec.size)

            taxes_id = rec.product_id.taxes_id.mapped('name')
            tax = ','.join(taxes_id)
            sheet1.write(row_index, 9, tax)

            color_id = self.env['product.attribute'].search([('name', '=', 'Color')], limit=1)
            color_val = rec.product_id.product_template_variant_value_ids.filtered(
                lambda line: line.attribute_id == color_id).product_attribute_value_id.name
            sheet1.write(row_index, 10, color_val or '')
            sheet1.write(row_index, 11, rec.product_id.weight)
            sheet1.write(row_index, 12, rec.country_id.name)

        fp = io.BytesIO()
        workbook.save(fp)
        report_id = self.env['excel.report'].create(
            {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': filename})
        fp.close()
        return {'view_mode': 'form',
                'res_id': report_id.id,
                'res_model': 'excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
                }


class ExcelReport(models.TransientModel):
    _name = 'excel.report'
    _description = "Excel Report"
    file_name = fields.Char(
        'Excel File',
        size=64,
        readonly=True,
    )

    excel_file = fields.Binary(
        'Download Report',
        readonly=True,
    )
