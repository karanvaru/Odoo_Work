# Copyright (c) 2018 Emipro Technologies Pvt Ltd (www.emiprotechnologies.com). All rights reserved.
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from io import BytesIO
from odoo.exceptions import ValidationError
from itertools import chain
import collections
import base64
try:
    import xlwt
    from xlwt import Borders
except ImportError:
    xlwt = None


class InventoryAgeBreakdownReport(models.TransientModel):

    _name = "inventory.age.breakdown.report.ept"

    def _get_company_domain(self):
        """
        Returns domain for company_ids.
        """
        return [('id', 'in', self.env.user.company_ids.ids)]

    def _default_breakdown_lines(self):
        breakdown_lines = self.env['breakdown.report.config.ept'].search([
            ('company_id', '=', self.env.user.company_id.id)
            ])
        breakdown_lst = []
        for line in breakdown_lines:
            breakdown_obj = self.env['inventory.age.breakdown.line.ept'].create({'day_start': line.day_start, 'day_end':line.day_end, 'inventory_breakdown_id': self.id})
            breakdown_lst.append(breakdown_obj.id)
        return  breakdown_lst 

    datas = fields.Binary('File')

#     report_wise = fields.Selection([('Warehouse', 'Warehouse'), ('Location', 'Location')], string='Generate Report Based on', default='Warehouse')
#     warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
#     location_ids = fields.Many2many('stock.location', string='Locations', domain=[('usage', 'not in', ['view', 'customer', 'supplier', 'procurement'])])
    company_ids = fields.Many2many("res.company", domain=lambda self:self._get_company_domain())
    include_all_products = fields.Boolean('Include All Products', default=True)
    product_ids = fields.Many2many('product.product', string='Products')

    day_breakdown_line_ids = fields.One2many('inventory.age.breakdown.line.ept', 'inventory_breakdown_id', 'Days Breakdown', default=_default_breakdown_lines)

    @api.multi
    def print_inventory_age_breakdown_report(self):
        today = datetime.now().strftime("%Y-%m-%d")
        active_id = self.ids[0]
        f_name = 'Inventory Age Breakdown Report for' + ' ' + today
        
        product_obj = self.env['product.product']
        if not self.include_all_products:
            all_product_ids = self.product_ids 
        else:
            all_product_ids = product_obj.with_context(active_test=True).search([])
        
        if not all_product_ids:
            raise ValidationError("Please select Include All Products or Products.")
        
#         warehouse_or_location = False
#         warehouse_obj = self.env['stock.warehouse']
#         location_obj = self.env['stock.location']
#         location_lst = []
#         if self.report_wise == 'Warehouse':
#             warehouse_or_location = self.warehouse_ids.ids
#             if not warehouse_or_location:
#                 warehouse_ids = warehouse_obj.search([])
#                 warehouse_or_location = warehouse_ids.ids        
#         if self.report_wise == 'Location':
#             warehouse_or_location = self.location_ids.ids
#             if not warehouse_or_location:
#                 location_ids = location_obj.search([('usage', 'not in', ['view', 'customer', 'supplier', 'procurement'])])
#                 if location_ids:
#                     for location in location_ids:
#                         child_list = self.get_child_locations(location)
#                         location_lst.append(child_list)
#                     
#                     locations = location_obj.browse(list(set(list(chain(*location_lst)))))
#                 else:
#                     return True            
#                 warehouse_or_location = locations.ids

        if self.company_ids:
            self.generate_inventory_age_breakdown_report(today, all_product_ids)
        else:
            raise ValidationError(_("Please select at least one company."))
        
        if self.datas:
            return {
            'type' : 'ir.actions.act_url',
            'url':   'web/content/?model=inventory.age.breakdown.report.ept&download=true&field=datas&id=%s&filename=%s.xls' % (active_id, f_name),
            'target': 'new',
             }
            
    @api.multi
    def generate_inventory_age_breakdown_report(self, today, all_product_ids):
#         warehouse_obj = self.env['stock.warehouse']
#         location_obj = self.env['stock.location']
#         location_lst = []
#         warehouse_ids = False
#         if self.report_wise == 'Warehouse':
#             warehouse_ids = warehouse_obj.search([('id', 'in', warehouse_or_location)])
#         else:
#             if not warehouse_ids:
#                 location_ids = location_obj.search([('id', 'in', warehouse_or_location)])
#             if location_ids:
#                 for location in location_ids:
#                     child_list = self.get_child_locations(location)
#                     location_lst.append(child_list)
#                     
#                 locations = location_obj.browse(list(set(list(chain(*location_lst)))))
#             else:
#                 return True
        companies = self.company_ids
        workbook , header_bold, body_style, style, default_code_style, body_horizontal_style, inventory_value_style, blank_cell_style, sales_data_style, worksheet_1_30_days_style = self.create_sheet()
        day_wise_value_dict = self.day_wise_value()
#         if self.report_wise == 'Warehouse': 
#             workbook, warehouse_sheet_data_dict, warehouse_row_data_dict = self.add_heading_warehouse(warehouse_ids, workbook, header_bold, style, blank_cell_style)
#             total_qty_and_values, all_ware_or_loc_dict = self.get_report_warehouse_wise(today, all_product_ids, warehouse_ids, warehouse_sheet_data_dict, warehouse_row_data_dict, day_wise_value_dict, default_code_style, inventory_value_style, blank_cell_style, worksheet_1_30_days_style, sales_data_style)
#         else:
#             workbook, location_sheet_data_dict, location_row_data_dict = self.add_heading_location(locations, workbook, header_bold, style, blank_cell_style)
#             total_qty_and_values, all_ware_or_loc_dict = self.get_report_location_wise(today, all_product_ids, locations, workbook, default_code_style, body_horizontal_style, blank_cell_style, location_sheet_data_dict, location_row_data_dict, day_wise_value_dict, worksheet_1_30_days_style)

        workbook, company_sheet_data_dict, company_row_data_dict = self.add_heading(companies, workbook, header_bold, style, blank_cell_style)
        total_qty_and_values, all_ware_or_loc_dict = self.get_report(today, all_product_ids, companies, company_sheet_data_dict, company_row_data_dict, day_wise_value_dict, default_code_style, inventory_value_style, blank_cell_style, worksheet_1_30_days_style, sales_data_style)

        workbook, worksheet_all_inventory = self.add_heading_all_ware_or_loc(workbook, header_bold, style, blank_cell_style)
        self.print_all_ware_or_loc_data(all_ware_or_loc_dict, worksheet_all_inventory, day_wise_value_dict, total_qty_and_values, default_code_style, inventory_value_style, blank_cell_style, sales_data_style, worksheet_1_30_days_style)

        fp = BytesIO()            
        workbook.save(fp)
        fp.seek(0)
        sale_file = base64.encodebytes(fp.read())
        fp.close()
        self.write({'datas':sale_file})
        return True
    
    @api.multi
    def get_child_locations(self, view_locations):
        child_list = []
        # # finding all child of given location
        for view_location in view_locations:
            child_locations = self.env['stock.location'].search([('usage', '=', 'internal'), ('location_id', '=', view_location.id)])
            if child_locations:
                for child_location in child_locations:
                    child_list.append(child_location.id)
                    children_locs = self.get_child_locations(child_location)
                    for location in children_locs:
                        child_list.append(location)
        return child_list
     
    @api.multi
    def create_sheet(self):
        
        workbook = xlwt.Workbook()
        
        borders = Borders()
        header_border = Borders()
        header_border.left, header_border.right, header_border.top, header_border.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THICK
        borders.left, borders.right, borders.top, borders.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THIN
        header_bold = xlwt.easyxf("font: bold on, height 210; pattern: pattern solid, fore_colour gray25;alignment: horizontal center ,vertical center")
        header_bold.borders = header_border
        body_style = xlwt.easyxf("font: height 200; alignment: horizontal center")
        style = xlwt.easyxf("font: height 210, bold True; alignment: horizontal center,vertical center;borders: top medium,right medium,bottom medium,left medium")
        body_style.borders = borders
        default_code_style = xlwt.easyxf("font: height 200; alignment: horizontal left")
        default_code_style.borders = borders
        body_horizontal_style = xlwt.easyxf("font: height 200; alignment: horizontal right")
        body_horizontal_style.borders = borders
        
        style.borders = borders
        inventory_value_style = xlwt.easyxf("font: height 200; alignment: horizontal right")
        inventory_value_style.borders = borders
        inventory_value_style.string_num_format = '0.00'
        
        xlwt.add_palette_colour("custom_yellow", 0x21)
        workbook.set_colour_RGB(0x21, 255, 255, 179)
        blank_cell_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_yellow;  borders: top thin,right thin,bottom thin,left thin")
        
        xlwt.add_palette_colour("custom_pink", 0x23)
        workbook.set_colour_RGB(0x23, 255, 204, 204)
        sales_data_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_pink;  borders: top thin,right thin,bottom thin,left thin")
        sales_data_style.string_num_format = '0.00' 
        
        xlwt.add_palette_colour("custom_green", 0x24)
        workbook.set_colour_RGB(0x24, 204, 255, 204)
        worksheet_1_30_days_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_green;  borders: top thin,right thin,bottom thin,left thin")
        worksheet_1_30_days_style.string_num_format = '0.00' 
        
        xlwt.add_palette_colour("custom_orange", 0x22)
        workbook.set_colour_RGB(0x22, 255, 204, 153)
        worksheet_31_60_days_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_orange;  borders: top thin,right thin,bottom thin,left thin")
        worksheet_31_60_days_style.string_num_format = '0.00' 
        
        xlwt.add_palette_colour("light_blue_21", 0x25)
        workbook.set_colour_RGB(0x25, 179, 255, 240)  
        worksheet_61_90_days_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour light_blue_21;  borders: top thin,right thin,bottom thin,left thin")
        worksheet_61_90_days_style.string_num_format = '0.00' 
        
        xlwt.add_palette_colour("light_purple_21", 0x26)
        workbook.set_colour_RGB(0x26, 255, 204, 224)  
        worksheet_91_180_days_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour light_purple_21;  borders: top thin,right thin,bottom thin,left thin")
        worksheet_91_180_days_style.string_num_format = '0.00' 
        
        xlwt.add_palette_colour("light_21", 0x27)
        workbook.set_colour_RGB(0x27, 236, 64, 122) 
        worksheet_over_180_days_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour light_21;  borders: top thin,right thin,bottom thin,left thin")
        worksheet_over_180_days_style.string_num_format = '0.00'
            
        return workbook , header_bold, body_style, style, default_code_style, body_horizontal_style, inventory_value_style, blank_cell_style, sales_data_style, worksheet_1_30_days_style
   
    @api.multi
    def day_wise_value(self):
        day_wise_value_dict = {}
        move_obj = self.env['stock.move']
        
        for breakdown_line in self.day_breakdown_line_ids:
            # start_day = datetime.now() + timedelta(-breakdown_line.day_start)
            start_day = datetime.now() + timedelta(-breakdown_line.day_start) + timedelta(days=1)
            start_days_str = start_day.strftime("%Y-%m-%d")
            # end_days = datetime.now() + timedelta(-breakdown_line.day_end)
            end_days = datetime.now() + timedelta(-breakdown_line.day_end) + timedelta(days=1)
            end_days_str = end_days.strftime("%Y-%m-%d")
            days_wise_stock_move = False
            total_inventory_value_days_wise = 0
            total_qty_sum_days_wise = 0
            qry = """select mv.id from stock_move mv inner join stock_location sl on sl.id= mv.location_dest_id where date between '%s 00:00:00' and '%s 23:59:59' """ % (end_days_str, start_days_str)
            self._cr.execute(qry)
            total_move_days_wise_lst = self._cr.fetchall()
            if total_move_days_wise_lst:
                move_lst = list(zip(*total_move_days_wise_lst))[0]
                days_wise_stock_move = move_obj.browse(move_lst).filtered(lambda x:x.state == 'done')
                total_qty_sum_days_wise = sum(days_wise_stock_move.mapped('remaining_qty'))
                total_inventory_value_days_wise = sum(days_wise_stock_move.mapped('remaining_value'))

            day_dict_name = '%s-%s' % (breakdown_line.day_start, breakdown_line.day_end)
            day_wise_value_dict.update({day_dict_name: {'days_wise_stock_move': days_wise_stock_move,
                                                        'total_qty_sum_days_wise': total_qty_sum_days_wise,
                                                        'total_inventory_value_days_wise': total_inventory_value_days_wise}})

        return day_wise_value_dict

    @api.multi
    def add_heading(self, companies, workbook, header_bold, style, blank_cell_style):
        company_sheet_data_dict = {}
        company_row_data_dict = {}
        for company in companies:

            company.name_worksheet = workbook.add_sheet('%s' % (company.name), cell_overwrite_ok=True)
            # # freezing columns
            company.name_worksheet.set_panes_frozen(True)
            company.name_worksheet.set_horz_split_pos(2)
            company.name_worksheet.set_vert_split_pos(3)

            company.name_worksheet.row(0).height = 400
            company.name_worksheet.row(1).height = 400
            company.name_worksheet.col(0).width = 2500
            company.name_worksheet.col(1).width = 5000
            company.name_worksheet.col(2).width = 10000
            company.name_worksheet.col(3).width = 5000
            company.name_worksheet.col(4).width = 1200
            company.name_worksheet.col(5).width = 5000
            company.name_worksheet.col(6).width = 5000
            company.name_worksheet.col(7).width = 5000
            company.name_worksheet.col(8).width = 5000
            company.name_worksheet.col(9).width = 1200
            company.name_worksheet.col(10).width = 5000
            company.name_worksheet.col(11).width = 5000
            company.name_worksheet.col(12).width = 5000
            company.name_worksheet.col(13).width = 5000
            company.name_worksheet.col(14).width = 1200
            company.name_worksheet.col(15).width = 5000
            company.name_worksheet.col(16).width = 5000
            company.name_worksheet.col(17).width = 5000
            company.name_worksheet.col(18).width = 5000
            company.name_worksheet.col(19).width = 1200
            company.name_worksheet.col(20).width = 5000
            company.name_worksheet.col(21).width = 5000
            company.name_worksheet.col(22).width = 5000
            company.name_worksheet.col(23).width = 5000
            company.name_worksheet.col(24).width = 1200
            company.name_worksheet.col(25).width = 5000
            company.name_worksheet.col(26).width = 5000
            company.name_worksheet.col(27).width = 5000
            company.name_worksheet.col(28).width = 5000

            row = 0
            company.name_worksheet.write(row, 0, "Company", header_bold)
            company.name_worksheet.write(row, 1, company.name, header_bold)
            company.name_worksheet.merge(row, row, 1, 2)
            row += 1
            company.name_worksheet.write(row, 0, 'Odoo ID', header_bold)
            company.name_worksheet.write(row, 1, 'Odoo SKU', header_bold)
            company.name_worksheet.write(row, 2, 'Product Name', header_bold)
            company.name_worksheet.write(row, 3, 'Total Qty', header_bold)
#             company.name_worksheet.write(row, 4, 'Total value', header_bold)

            merge_sell = col = 3
            for break_down_line in self.day_breakdown_line_ids:
                company.name_worksheet.write(row, col + 2, 'Qty', header_bold)
                company.name_worksheet.write(row, col + 3, 'Qty (% of overall)', header_bold)
                company.name_worksheet.write(row, col + 4, 'Value (%s)' % (company.currency_id.symbol), header_bold)
                company.name_worksheet.write(row, col + 5, 'Value (% of overall)', header_bold)
                col += 5
                merge_sell = merge_sell + 2
                company.name_worksheet.write_merge(0, 0, merge_sell, merge_sell + 3, '%s - %s days old' % (break_down_line.day_start, break_down_line.day_end), style)
                merge_sell = merge_sell + 3

            company.name_worksheet.write(row, 4, None, blank_cell_style)
            company.name_worksheet.write(row, 9, None, blank_cell_style)
            company.name_worksheet.write(row, 14, None, blank_cell_style)
            company.name_worksheet.write(row, 19, None, blank_cell_style)
            company.name_worksheet.write(row, 24, None, blank_cell_style)

            # #Get company wise worksheet
            company_sheet_data_dict.update({company.id: company.name_worksheet})

            # #initialize  worksheet wise row value
            company_row_data_dict.update({company.name_worksheet: 2})
            
        return workbook, company_sheet_data_dict, company_row_data_dict

    @api.multi
    def get_report(self, today, all_product_ids, companies, company_sheet_data_dict, company_row_data_dict, day_wise_value_dict, default_code_style, inventory_value_style, blank_cell_style, worksheet_1_30_days_style, sales_data_style):      
        total_qty_and_values = {}
        all_ware_or_loc_dict = {}

        column = 0

        for company in companies:
            warehouses = self.env['stock.warehouse'].search([('company_id', '=', company.id)])
            child_locations_list = self.get_child_locations(warehouses.mapped('view_location_id'))
            location_data_dict = {company.id: child_locations_list}

            for product in all_product_ids:
                product_qty = product.with_context(force_company=company.id).qty_available
                if product_qty > 0:
                    row = company_row_data_dict[company_sheet_data_dict[company.id]]
                    company_sheet_data_dict[company.id].row(row).height = 350
                    company_sheet_data_dict[company.id].write(row, column, product.id, default_code_style)
                    company_sheet_data_dict[company.id].write(row, column + 1, product.default_code or '-', default_code_style)
                    company_sheet_data_dict[company.id].write(row, column + 2, product.name, default_code_style)
    #                 company_sheet_data_dict[company.id].write(row, column + 3, round(average_cost, 2), inventory_value_style)
    #                 company_sheet_data_dict[company.id].write(row, column + 4, current_sale_price and current_sale_price[0][0] or 0, inventory_value_style)
                    company_sheet_data_dict[company.id].write(row, column + 3, product_qty, inventory_value_style)
    #                 company_sheet_data_dict[company.id].write(row, column + 4, total_value, inventory_value_style)
                    company_sheet_data_dict[company.id].write(row, column + 4, None, blank_cell_style)
    #                 company_sheet_data_dict[company.id].write(row, column + 8, round(avarage_sale_price_last_30, 2) or 0, sales_data_style)
    #                 company_sheet_data_dict[company.id].write(row, column + 9, round(sale_qty_last_30, 2) or 0, sales_data_style)
    #                 company_sheet_data_dict[company.id].write(row, column + 10, round(sales_price_last_30, 2) or  0, sales_data_style)
    #                 company_sheet_data_dict[company.id].write(row, column + 11, None, blank_cell_style)

                    new_column = 4
                    for breakdown_line in self.day_breakdown_line_ids:
                        qty_per_breakdown_days = 0
                        value_per_breakdown_days = 0
                        total_qty_breakdown_days = 0
                        total_value_breakdown_days = 0
                        day_key_dict_name = '%s-%s' % (breakdown_line.day_start, breakdown_line.day_end)
                        days_wise_move_obj = day_wise_value_dict.get(day_key_dict_name).get('days_wise_stock_move')
    
                        if days_wise_move_obj:
                            breakdown_product_moves = days_wise_move_obj.filtered(lambda mv:mv.product_id.id == product.id and mv.location_dest_id.id in location_data_dict[company.id])
                            total_qty_breakdown_days = sum(breakdown_product_moves.mapped('remaining_qty'))
                            total_value_breakdown_days = sum(breakdown_product_moves.mapped('remaining_value'))
    
                            total_qty_breakdown_days_warehouse = days_wise_move_obj.filtered(lambda mv: mv.location_dest_id.id in location_data_dict[company.id])
                            total_qty_sum_breakdown_days_internal = sum(total_qty_breakdown_days_warehouse.mapped('remaining_qty'))
                            total_inventory_value_breakdown_days_internal = sum(total_qty_breakdown_days_warehouse.mapped('remaining_value')) 
                            
                            if total_qty_sum_breakdown_days_internal > 0:
                                qty_per_breakdown_days = (total_qty_breakdown_days / total_qty_sum_breakdown_days_internal) * 100
                            if total_inventory_value_breakdown_days_internal > 0:
                                value_per_breakdown_days = (total_value_breakdown_days / total_inventory_value_breakdown_days_internal) * 100
    
                        company_sheet_data_dict[company.id].write(row, new_column + 1, total_qty_breakdown_days, worksheet_1_30_days_style)
                        company_sheet_data_dict[company.id].write(row, new_column + 2, round(qty_per_breakdown_days, 2), worksheet_1_30_days_style)
                        company_sheet_data_dict[company.id].write(row, new_column + 3, round(total_value_breakdown_days, 2), worksheet_1_30_days_style)
                        company_sheet_data_dict[company.id].write(row, new_column + 4, round(value_per_breakdown_days, 2), worksheet_1_30_days_style)
                        company_sheet_data_dict[company.id].write(row, new_column + 5, None, blank_cell_style)
                        new_column += 5

                        if total_qty_and_values.get((product.id, day_key_dict_name)):
                            product_data = total_qty_and_values.get((product.id, day_key_dict_name))
                            product_total_qty = product_data.get('product_total_qty')
                            product_total_qty = product_total_qty + total_qty_breakdown_days

                            product_total_values = product_data.get('product_total_values')
                            product_total_values = product_total_values + total_value_breakdown_days

                            total_qty_and_values.update({(product.id, day_key_dict_name):{'product_total_qty':product_total_qty, 'product_total_values':product_total_values}})

                        else:
                            total_qty_and_values.update({(product.id, day_key_dict_name):{ 'product_total_qty':total_qty_breakdown_days, 'product_total_values':total_value_breakdown_days} })
                    
                    row += 1
                    column = 0 
                    company_row_data_dict.update({company_sheet_data_dict[company.id]: row})

                    if all_ware_or_loc_dict.get(product.id):
                        all_ware_or_loc_dict.update({product.id:{'default_code':product.default_code,
                                                                'name':product.name,
                                                                'total_qty':product_qty}})
                        
                    else:
                        all_ware_or_loc_dict.update({product.id:{'default_code':product.default_code,
                                                                'name':product.name,
                                                                'total_qty':product_qty}})
#                         all_ware_or_loc_dict = self.prepare_dict_data(all_ware_or_loc_dict, product, product_qty)

        return total_qty_and_values, all_ware_or_loc_dict

    @api.multi
    def add_heading_warehouse(self, warehouse_ids, workbook, header_bold, style, blank_cell_style):
        warehouse_sheet_data_dict = {}
        warehouse_row_data_dict = {}
        count = 0
        for warehouse in warehouse_ids:
            count += 1
#             warehouse.name_worksheet = workbook.add_sheet('Sheet %s'%(count), cell_overwrite_ok=True)
            warehouse.name_worksheet = workbook.add_sheet('%s' % (warehouse.name), cell_overwrite_ok=True)
            
            warehouse.name_worksheet.set_panes_frozen(True)
            warehouse.name_worksheet.set_horz_split_pos(2) 
            warehouse.name_worksheet.set_vert_split_pos(3)
            
            warehouse.name_worksheet.row(0).height = 400
            warehouse.name_worksheet.row(1).height = 400
            warehouse.name_worksheet.col(0).width = 2500
            warehouse.name_worksheet.col(1).width = 5000
            warehouse.name_worksheet.col(2).width = 10000
            warehouse.name_worksheet.col(3).width = 4000
            warehouse.name_worksheet.col(4).width = 5000
            warehouse.name_worksheet.col(5).width = 5000
            warehouse.name_worksheet.col(6).width = 5500
            warehouse.name_worksheet.col(7).width = 1200
            warehouse.name_worksheet.col(8).width = 5000
            warehouse.name_worksheet.col(9).width = 4000
            warehouse.name_worksheet.col(10).width = 5000
            warehouse.name_worksheet.col(11).width = 1200
            warehouse.name_worksheet.col(12).width = 5000
            warehouse.name_worksheet.col(13).width = 5000
            warehouse.name_worksheet.col(14).width = 5000
            warehouse.name_worksheet.col(15).width = 5000
            warehouse.name_worksheet.col(16).width = 1200
            warehouse.name_worksheet.col(17).width = 5000
            warehouse.name_worksheet.col(19).width = 5000
            warehouse.name_worksheet.col(20).width = 5000
            warehouse.name_worksheet.col(21).width = 1200
            warehouse.name_worksheet.col(22).width = 5000
            warehouse.name_worksheet.col(24).width = 5000
            warehouse.name_worksheet.col(25).width = 5000
            warehouse.name_worksheet.col(26).width = 1200
            warehouse.name_worksheet.col(27).width = 5000
            warehouse.name_worksheet.col(29).width = 5000
            warehouse.name_worksheet.col(30).width = 5000
            warehouse.name_worksheet.col(31).width = 1200
            warehouse.name_worksheet.col(32).width = 5000
            warehouse.name_worksheet.col(34).width = 5000
            
            row = 0
            warehouse.name_worksheet.write(row, 0, self.report_wise, header_bold)
            warehouse.name_worksheet.write(row, 1, warehouse.name, header_bold)
            warehouse.name_worksheet.merge(row, row, 1, 2)
            row += 1 
            warehouse.name_worksheet.write(row, 0, 'Odoo ID', header_bold)
            warehouse.name_worksheet.write(row, 1, 'Odoo SKU', header_bold)
            warehouse.name_worksheet.write(row, 2, 'Product Name', header_bold)
            warehouse.name_worksheet.write(row, 3, 'Average Cost', header_bold)
            warehouse.name_worksheet.write(row, 4, 'Current Sale Price', header_bold)
            warehouse.name_worksheet.write(row, 5, 'Total  Qty', header_bold)
            warehouse.name_worksheet.write(row, 6, 'Total  value', header_bold)
            warehouse.name_worksheet.write(row, 8, 'Average Sale Price', header_bold)
            warehouse.name_worksheet.write(row, 9, 'Sales (qty)', header_bold)
            warehouse.name_worksheet.write(row, 10, 'Sales (%s)' % (warehouse.company_id.currency_id.symbol), header_bold)
             
            warehouse.name_worksheet.write_merge(0, 0, 8, 10, 'Last 30 days', style)
            merge_sell = 10
            col = 10
            for break_down_line in self.day_breakdown_line_ids:
                warehouse.name_worksheet.write(row, col + 2, 'Qty', header_bold)
                warehouse.name_worksheet.write(row, col + 3, 'Qty (% of overall)', header_bold)
                warehouse.name_worksheet.write(row, col + 4, 'Value (%s)' % (warehouse.company_id.currency_id.symbol), header_bold)
                warehouse.name_worksheet.write(row, col + 5, 'Value (% of overall)', header_bold)
                col = col + 5
                merge_sell = merge_sell + 2
                warehouse.name_worksheet.write_merge(0, 0, merge_sell, merge_sell + 3, '%s - %s days old' % (break_down_line.day_start, break_down_line.day_end), style)
                merge_sell = merge_sell + 3
             
            warehouse.name_worksheet.write(row, 7, None, header_bold)
            warehouse.name_worksheet.write(row, 11, None, header_bold)
            warehouse.name_worksheet.write(row, 16, None, header_bold)
            warehouse.name_worksheet.write(row, 21, None, header_bold)
            warehouse.name_worksheet.write(row, 26, None, header_bold)
            warehouse.name_worksheet.write(row, 31, None, header_bold)
            
            # #Get warehouse wise worksheet
            warehouse_sheet_data_dict.update({warehouse.id: warehouse.name_worksheet})
            
            # #initialize  worksheet wise row value
            warehouse_row_data_dict.update({warehouse.name_worksheet: 2})
            
        return workbook, warehouse_sheet_data_dict, warehouse_row_data_dict
    
    @api.multi
    def get_report_warehouse_wise(self, today, all_product_ids, warehouse_ids, warehouse_sheet_data_dict, warehouse_row_data_dict, day_wise_value_dict, default_code_style, inventory_value_style, blank_cell_style, worksheet_1_30_days_style, sales_data_style):
        
        warehouse_obj = self.env['stock.warehouse']
        stock_move_obj = self.env['stock.move']
        column = 0
        all_ware_or_loc_dict = collections.OrderedDict()
        total_qty_and_values = collections.OrderedDict()
        thirty_days = datetime.now() + timedelta(-30)
        thirty_days_str = thirty_days.strftime("%Y-%m-%d")
        location_data_dict = {}
        if self.report_wise == 'Warehouse':
            if len(all_product_ids) > 1 :
                move_qry = """select distinct mv.id,product_id from stock_move mv inner join stock_location sl on sl.id=mv.location_dest_id  and sl.usage='internal' where product_id in %s order by mv.id """ % (str(tuple(all_product_ids.ids)))
            else:
                move_qry = """select distinct mv.id,product_id from stock_move mv inner join stock_location sl on sl.id=mv.location_dest_id  and sl.usage='internal' where product_id in (%s) order by mv.id """ % (all_product_ids.id)
            self._cr.execute(move_qry)
            move_lst = self._cr.fetchall()
            
            if not move_lst:
                product_lst = list(zip(*move_lst))
            else:
                product_lst = list(zip(*move_lst))[1]
                
            product_ids = self.env['product.product'].search([('id', 'in', product_lst), ('type', '=', 'product')])
            warehouse_ids = warehouse_obj.search([('id', 'in', warehouse_ids.ids)])
            for product in product_ids:
                for warehouse in warehouse_ids:
                    location_data_dict, total_sale_qty_last_30_days , total_sales_price_last_30_days = self.get_product_average_sale_qty_last_30_data(product_lst, warehouse, thirty_days_str, today)
                    
                    product_obj = product.with_context(warehouse=warehouse.id)
                    product_qty = product_obj.qty_available
                    if product_qty > 0:
                        child_locations_list = self.get_child_locations(warehouse.lot_stock_id)
                        move_ids = self.env['stock.move'].search([('product_id', '=', product.id), ('location_dest_id', 'in', child_locations_list)])
                        if move_ids:
                            po_move_line = stock_move_obj.search([('product_id', '=', product.id), ('location_dest_id', 'in', child_locations_list), ('purchase_line_id', '!=', False), ('state', '=', 'done')])
                            total_unit_price = 0
                            total_qty = 0
                            for line in po_move_line:
                                total_unit_price += line.purchase_line_id.qty_received * line.purchase_line_id.price_unit
                                total_qty += line.purchase_line_id.qty_received
                       
                            if total_qty > 0:
                                average_cost = total_unit_price / total_qty
                            else:
                                average_cost = 0 
                                
                        current_sale_price_qry = """select sale_price_unit from stock_move mv Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer' where state='done' and product_id= %s and warehouse_id= %s order by date desc limit 1 """ % (product.id, warehouse.id)
                        self._cr.execute(current_sale_price_qry)
                        current_sale_price = self._cr.fetchall() 
                        
                        total_value = product_qty * product.standard_price
                        
                        product_old_min = thirty_days_str + ' 00:00:00'
                        product_old_max = today + ' 23:59:59'
                        sale_move = stock_move_obj.search([('product_id', '=', product.id), ('location_id', 'in', child_locations_list), ('sale_line_id', '!=', False), ('state', '=', 'done'), ('date', '>', product_old_min), ('date', '<', product_old_max)]) 
                        total_mv_qty = 0
                        total_mv_price = 0
                        for mv in sale_move:
                            total_mv_price += mv.sale_line_id.qty_delivered * mv.sale_line_id.price_unit
                            total_mv_qty += mv.sale_line_id.qty_delivered
                       
                        if total_mv_qty > 0:
                            avarage_sale_price_last_30 = total_mv_price / total_mv_qty
                        else:
                            avarage_sale_price_last_30 = 0
                      
                        sale_qty_last_30 = total_sale_qty_last_30_days[warehouse.id].get(product.id, False)
                        sales_price_last_30 = total_sales_price_last_30_days[warehouse.id].get(product.id, False)
                        
                        row = warehouse_row_data_dict[warehouse_sheet_data_dict[warehouse.id]]
                        warehouse_sheet_data_dict[warehouse.id].row(row).height = 350
                        warehouse_sheet_data_dict[warehouse.id].write(row, column, product.id, default_code_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 1, product.default_code or '-', default_code_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 2, product.name, default_code_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 3, round(average_cost, 2), inventory_value_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 4, current_sale_price and current_sale_price[0][0] or 0, inventory_value_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 5, product_qty, inventory_value_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 6, total_value, inventory_value_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 7, None, blank_cell_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 8, round(avarage_sale_price_last_30, 2) or 0, sales_data_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 9, round(sale_qty_last_30, 2) or 0, sales_data_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 10, round(sales_price_last_30, 2) or  0, sales_data_style)
                        warehouse_sheet_data_dict[warehouse.id].write(row, column + 11, None, blank_cell_style)
                        
                        new_column = 11
                        for breakdown_line in self.day_breakdown_line_ids:
                            qty_per_breakdown_days = 0
                            value_per_breakdown_days = 0
                            total_qty_breakdown_days = 0
                            total_value_breakdown_days = 0
                            day_key_dict_name = '%s-%s' % (breakdown_line.day_start, breakdown_line.day_end)
                            days_wise_move_obj = day_wise_value_dict.get(day_key_dict_name).get('days_wise_stock_move')
                            
                            if days_wise_move_obj:
                                breakdown_product_moves = days_wise_move_obj.filtered(lambda mv:mv.product_id.id == product_obj.id and mv.location_dest_id.id in location_data_dict[warehouse.id])
                                total_qty_breakdown_days = sum(breakdown_product_moves.mapped('remaining_qty'))
                                total_value_breakdown_days = total_qty_breakdown_days * product_obj.standard_price
        
                                total_qty_breakdown_days_warehouse = days_wise_move_obj.filtered(lambda mv: mv.location_dest_id.id in location_data_dict[warehouse.id])
                                total_qty_sum_breakdown_days_internal = sum(total_qty_breakdown_days_warehouse.mapped('remaining_qty'))
                                total_inventory_value_breakdown_days_internal = sum(total_qty_breakdown_days_warehouse.mapped('product_id.stock_value'))
                                if total_qty_sum_breakdown_days_internal > 0:
                                    qty_per_breakdown_days = (total_qty_breakdown_days / total_qty_sum_breakdown_days_internal) * 100
                                if total_inventory_value_breakdown_days_internal > 0:
                                    value_per_breakdown_days = (total_value_breakdown_days / total_inventory_value_breakdown_days_internal) * 100
        
                            warehouse_sheet_data_dict[warehouse.id].write(row, new_column + 1, total_qty_breakdown_days, worksheet_1_30_days_style)
                            warehouse_sheet_data_dict[warehouse.id].write(row, new_column + 2, round(qty_per_breakdown_days, 2), worksheet_1_30_days_style)
                            warehouse_sheet_data_dict[warehouse.id].write(row, new_column + 3, round(total_value_breakdown_days, 2), worksheet_1_30_days_style)
                            warehouse_sheet_data_dict[warehouse.id].write(row, new_column + 4, round(value_per_breakdown_days, 2), worksheet_1_30_days_style)
                            warehouse_sheet_data_dict[warehouse.id].write(row, new_column + 5, None, blank_cell_style)
                            new_column += 5  
                            
                            if total_qty_and_values.get((product.id, day_key_dict_name)):
                                product_data = total_qty_and_values.get((product.id, day_key_dict_name))
                                product_total_qty = product_data.get('product_total_qty')
                                product_total_qty = product_total_qty + total_qty_breakdown_days
                                
                                product_total_values = product_data.get('product_total_values')
                                product_total_values = product_total_values + total_value_breakdown_days
                                
                                total_qty_and_values.update({(product.id, day_key_dict_name):{'product_total_qty':product_total_qty, 'product_total_values':product_total_values}})
                        
                            else:
                                total_qty_and_values.update({(product.id, day_key_dict_name):{ 'product_total_qty':total_qty_breakdown_days, 'product_total_values':total_value_breakdown_days} })
                        
                        row += 1
                        column = 0 
                        warehouse_row_data_dict.update({warehouse_sheet_data_dict[warehouse.id]: row})   
                        
                        all_ware_or_loc_dict = self.prepare_dict_data(all_ware_or_loc_dict, product, average_cost, current_sale_price, product_qty, total_value, avarage_sale_price_last_30, sale_qty_last_30, sales_price_last_30)
        return total_qty_and_values, all_ware_or_loc_dict
    
    @api.multi
    def get_product_average_sale_qty_last_30_data(self, product_lst, company, thirty_days_str, today, child_locations_list):
        
        total_sale_qty_last_30_days = {company.id:{}}
        total_sales_price_last_30_days = {company.id:{}}
#         
#         location_data_dict = {}
#         
#         location_ids = self.env['stock.location'].browse(child_locations_list)
#         location_data_dict.update({company.id: child_locations_list})  
                
#         total_qty_qry = """select product_id, sum(product_uom_qty) from stock_move mv Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer'  where state='done' and product_id in %s and warehouse_id= %s  and date between '%s 00:00:00' and '%s 23:59:59'  group by product_id  """ % (str(tuple(product_lst)), company.id, thirty_days_str, today)   
#         self._cr.execute(total_qty_qry)
#         total_sale_qty_lst = self._cr.fetchall()
#         total_sale_qty_dict = dict(total_sale_qty_lst)
#         total_sale_qty_last_30_days.update({company.id:total_sale_qty_dict})        
#                    
#         total_sales_qry = """select  product_id, sum(product_uom_qty * sale_price_unit) sales  from stock_move mv Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer' where state='done' and product_id in %s and warehouse_id= %s  and date between '%s 00:00:00' and '%s 23:59:59' group by product_id """ % (str(tuple(product_lst)), company.id, thirty_days_str, today)
#         self._cr.execute(total_sales_qry)
#         total_sales_lst = self._cr.fetchall()
#         total_sales_dict = dict(total_sales_lst)
#         total_sales_price_last_30_days.update({company.id:total_sales_dict})
        
        return total_sale_qty_last_30_days , total_sales_price_last_30_days 
    
    @api.multi
    def add_heading_location(self, locations_or_warehouses, workbook, header_bold, style, blank_cell_style):
        location_sheet_data_dict = {}
        location_row_data_dict = {}
        # location_ids = self.env['stock.location'].search([('id', 'in', locations_or_warehouses.ids), ('location_id', 'not in', locations_or_warehouses.ids)])
        location_ids = self.env['stock.location'].search([('id', 'in', locations_or_warehouses.ids)])
        count = 0
        for location in location_ids:
            count += 1
#             location.name_worksheet = workbook.add_sheet('Sheet %s'%(count), cell_overwrite_ok=True)
            location.name_worksheet = workbook.add_sheet('%s' % (location.complete_name), cell_overwrite_ok=True)
            # # freezing columns
            location.name_worksheet.set_panes_frozen(True)
            location.name_worksheet.set_horz_split_pos(2)
            location.name_worksheet.set_vert_split_pos(3)

            location.name_worksheet.row(0).height = 400
            location.name_worksheet.row(1).height = 400
            location.name_worksheet.col(0).width = 2500
            location.name_worksheet.col(1).width = 5000
            location.name_worksheet.col(2).width = 10000
            location.name_worksheet.col(3).width = 5500
            location.name_worksheet.col(4).width = 5500
            location.name_worksheet.col(5).width = 1200
            location.name_worksheet.col(6).width = 5000
            location.name_worksheet.col(7).width = 5000
            location.name_worksheet.col(8).width = 5000
            location.name_worksheet.col(9).width = 5000
            location.name_worksheet.col(10).width = 1200
            location.name_worksheet.col(11).width = 5000
            location.name_worksheet.col(12).width = 5000
            location.name_worksheet.col(13).width = 5500
            location.name_worksheet.col(14).width = 5000
            location.name_worksheet.col(15).width = 1200
            location.name_worksheet.col(16).width = 5000
            location.name_worksheet.col(17).width = 5000
            location.name_worksheet.col(18).width = 5000
            location.name_worksheet.col(19).width = 5000
            location.name_worksheet.col(20).width = 1200
            location.name_worksheet.col(21).width = 5000
            location.name_worksheet.col(22).width = 5000
            location.name_worksheet.col(23).width = 5000
            location.name_worksheet.col(24).width = 5000
            location.name_worksheet.col(25).width = 1200
            location.name_worksheet.col(26).width = 5000
            location.name_worksheet.col(27).width = 5000
            location.name_worksheet.col(28).width = 5000
            location.name_worksheet.col(29).width = 5000
            
            row = 0
            location.name_worksheet.write(row, 0, self.report_wise, header_bold)
            location.name_worksheet.write(row, 1, location.display_name, header_bold)
            location.name_worksheet.merge(row, row, 1, 2)
            row += 1
            location.name_worksheet.write(row, 0, 'Odoo ID', header_bold)
            location.name_worksheet.write(row, 1, 'Odoo SKU', header_bold)
            location.name_worksheet.write(row, 2, 'Product Name', header_bold)
            location.name_worksheet.write(row, 3, 'Total Qty', header_bold)
            location.name_worksheet.write(row, 4, 'Total value', header_bold)

            merge_sell = 4
            col = 4
            for break_down_line in self.day_breakdown_line_ids:
                location.name_worksheet.write(row, col + 2, 'Qty', header_bold)
                location.name_worksheet.write(row, col + 3, 'Qty (% of overall)', header_bold)
                location.name_worksheet.write(row, col + 4, 'Value (%s)' % (location.company_id.currency_id.symbol), header_bold)
                location.name_worksheet.write(row, col + 5, 'Value (% of overall)', header_bold)
                col = col + 5
                merge_sell = merge_sell + 2
                location.name_worksheet.write_merge(0, 0, merge_sell, merge_sell + 3, '%s - %s days old' % (break_down_line.day_start, break_down_line.day_end), style)
                merge_sell = merge_sell + 3

            location.name_worksheet.write(row, 5, None, header_bold)
            location.name_worksheet.write(row, 10, None, header_bold)
            location.name_worksheet.write(row, 15, None, header_bold)
            location.name_worksheet.write(row, 20, None, header_bold)
            location.name_worksheet.write(row, 25, None, header_bold)

            # #Get location wise worksheet
            location_sheet_data_dict.update({location.id: location.name_worksheet})

            # #initialize  worksheet wise row value
            location_row_data_dict.update({location.name_worksheet: 2})
            
        return workbook, location_sheet_data_dict, location_row_data_dict

    @api.multi
    def get_report_location_wise(self, today, all_product_ids, locations, workbook, default_code_style, body_horizontal_style, blank_cell_style, location_sheet_data_dict, location_row_data_dict, day_wise_value_dict, worksheet_1_30_days_style):   
        location_obj = self.env['stock.location']
        stock_move_obj = self.env['stock.move']
      
        total_qty_and_values = {}
        all_ware_or_loc_dict = {}

        column = 0
        thirty_days = datetime.now() + timedelta(-30)
        thirty_days_str = thirty_days.strftime("%Y-%m-%d")
        
        # locations_ids = location_obj.search([('id', 'in', warehouse_or_location.ids)])
        if self.report_wise == 'Location':
            if len(all_product_ids) > 1 :
                product_move_qry = """select distinct mv.id,product_id from stock_move mv inner join stock_location sl on sl.id=mv.location_dest_id  and sl.usage='internal' where product_id in %s order by mv.id """ % (str(tuple(all_product_ids.ids)))
            else:
                product_move_qry = """select distinct mv.id,product_id from stock_move mv inner join stock_location sl on sl.id=mv.location_dest_id  and sl.usage='internal' where product_id in (%s) order by mv.id """ % (all_product_ids.id)
            self._cr.execute(product_move_qry)
            move_lst = self._cr.fetchall()
            
            if not move_lst:
                product_lst = list(zip(*move_lst))
            else:
                product_lst = list(zip(*move_lst))[1]
            
            new_product_ids = self.env['product.product'].search([('id', 'in', product_lst), ('type', '=', 'product')])
            locations_ids = location_obj.search([('id', 'in', locations.ids)])
            for product in new_product_ids:
                for location in locations_ids:
                    child_locations_list = self.get_child_locations(location)
                    
                    product_total_sale_qty_dict, product_total_sales_dict = self.last_30_sale_qty_all_inventory(product_lst, thirty_days_str, today, all_product_ids)
                  
                    product_obj = product.with_context(location=location.id)
                    product_qty = product_obj.qty_available
                    if product_qty > 0:
                        
                        total_qty = product_qty
                        total_value = product.with_context(location=location.id).stock_value  # product_qty * product.standard_price   
                        
                        po_move_line = stock_move_obj.search([('product_id', '=', product.id), ('location_dest_id', 'in', child_locations_list), ('purchase_line_id', '!=', False), ('state', '=', 'done')])
                        total_unit_price = 0
                        total_qty = 0
                        for line in po_move_line:
                            total_unit_price += line.purchase_line_id.qty_received * line.purchase_line_id.price_unit
                            total_qty += line.purchase_line_id.qty_received
                       
                        if total_qty > 0:
                            average_cost = total_unit_price / total_qty
                        else:
                            average_cost = 0
                        
                        product_old_min = thirty_days_str + ' 00:00:00'
                        product_old_max = today + ' 23:59:59'
                        sale_move = stock_move_obj.search([('product_id', '=', product.id), ('location_id', 'in', child_locations_list), ('sale_line_id', '!=', False), ('state', '=', 'done'), ('date', '>', product_old_min), ('date', '<', product_old_max)]) 
                        total_mv_qty = 0
                        total_mv_price = 0
                        for mv in sale_move:
                            total_mv_price += mv.sale_line_id.qty_delivered * mv.sale_line_id.price_unit
                            total_mv_qty += mv.sale_line_id.qty_delivered
                       
                        if total_mv_qty > 0:
                            avarage_sale_price_last_30 = total_mv_price / total_mv_qty
                        else:
                            avarage_sale_price_last_30 = 0
                    
                        # sale_qty_last_30 = product_total_sale_qty_dict[location.id].get(product.id, False)
                        # sales_price_last_30 = product_total_sales_dict[location.id].get(product.id, False)
                        sale_qty_last_30 = product_total_sale_qty_dict.get(product.id, False)  # .get(location.id,{})
                        sales_price_last_30 = product_total_sales_dict.get(product.id, False)  # .get(location.id,{}).get(product.id, False)
                        
                        current_price_qry = """ select sale_price_unit from stock_move mv  Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer' where state='done' and product_id= %s order by date desc limit 1   """ % (product.id) 
                        self._cr.execute(current_price_qry)
                        current_sale_price = self._cr.fetchall()
                        
                        row = location_row_data_dict[location_sheet_data_dict[location.id]]
                        location_sheet_data_dict[location.id].row(row).height = 350
                        location_sheet_data_dict[location.id].write(row, column, product.id, default_code_style)
                        location_sheet_data_dict[location.id].write(row, column + 1, product.default_code or '-', default_code_style)
                        location_sheet_data_dict[location.id].write(row, column + 2, product.name, default_code_style)
                        location_sheet_data_dict[location.id].write(row, column + 3, product_qty, body_horizontal_style)
                        location_sheet_data_dict[location.id].write(row, column + 4, total_value, body_horizontal_style)
                        location_sheet_data_dict[location.id].write(row, column + 5, None, blank_cell_style)
                        
                        new_column = 5
                        for breakdown_line in self.day_breakdown_line_ids:
                            day_key_dict_name = '%s-%s' % (breakdown_line.day_start, breakdown_line.day_end)
                           
                            total_qty_breakdown_days = 0
                            overall_qty_breakdown_days = 0
                            total_inventory_value_breakdown_days = 0
                            overall_inventory_value_breakdown_days = 0
                            days_wise_stock_move = day_wise_value_dict.get(day_key_dict_name).get('days_wise_stock_move')
                            total_qty_sum_days = day_wise_value_dict.get(day_key_dict_name).get('total_qty_sum_days_wise')
                            total_inventory_value_breakdown_days = day_wise_value_dict.get(day_key_dict_name).get('total_inventory_value_days_wise')

                            if days_wise_stock_move:
                                last_breakdown_days_product_in_transit = days_wise_stock_move.filtered(lambda mv:mv.product_id.id == product.id and mv.location_dest_id.id == location.id)
                                total_qty_breakdown_days = sum(last_breakdown_days_product_in_transit.mapped('remaining_qty')) 
                                total_inventory_stock_value_breakdown_day = total_qty_breakdown_days * product.standard_price
                                   
                                if total_qty_breakdown_days > 0:
                                    overall_qty_breakdown_days = (total_qty_breakdown_days / total_qty_sum_days) * 100
                                                                                    
                                if total_inventory_stock_value_breakdown_day > 0:
                                    overall_inventory_value_breakdown_days = (total_inventory_stock_value_breakdown_day / total_inventory_value_breakdown_days) * 100
                                                                                      
                            location_sheet_data_dict[location.id].write(row, new_column + 1, total_qty_breakdown_days or 0, worksheet_1_30_days_style)
                            location_sheet_data_dict[location.id].write(row, new_column + 2, round(overall_qty_breakdown_days, 2) or 0, worksheet_1_30_days_style)
                            location_sheet_data_dict[location.id].write(row, new_column + 3, total_inventory_stock_value_breakdown_day or 0, worksheet_1_30_days_style)
                            location_sheet_data_dict[location.id].write(row, new_column + 4, round(overall_inventory_value_breakdown_days, 2) or 0, worksheet_1_30_days_style)
                            location_sheet_data_dict[location.id].write(row, new_column + 5, None, blank_cell_style)
                            new_column += 5
                            
                            if total_qty_and_values.get((product.id, day_key_dict_name)):
                                product_data = total_qty_and_values.get((product.id, day_key_dict_name))
                                product_total_qty = product_data.get('product_total_qty')
                                product_total_qty = product_total_qty + total_qty_breakdown_days

                                product_total_values = product_data.get('product_total_values')
                                product_total_values = product_total_values + total_inventory_stock_value_breakdown_day

                                total_qty_and_values.update({(product.id, day_key_dict_name): {'product_total_qty': product_total_qty, 'product_total_values': product_total_values}})                               
                                    
                            else:
                                total_qty_and_values.update({(product.id, day_key_dict_name): {'product_total_qty': total_qty_breakdown_days, 'product_total_values': total_inventory_stock_value_breakdown_day}})
                                    
                        row += 1
                        location_row_data_dict.update({location_sheet_data_dict[location.id]: row})
                        
                        all_ware_or_loc_dict = self.prepare_dict_data(all_ware_or_loc_dict, product, average_cost, current_sale_price, product_qty, total_value, avarage_sale_price_last_30, sale_qty_last_30, sales_price_last_30)
                        
        return total_qty_and_values, all_ware_or_loc_dict
    
    @api.multi
    def last_30_sale_qty_all_inventory(self, product_lst, thirty_days_str, today, all_product_ids):
        if isinstance(product_lst, list) :
            product_id_str = '(' + str(product_lst or [0]).strip('[]') + ')'
        else :
            product_id_str = product_lst
        all_product_ids_str = '(' + str(all_product_ids and all_product_ids.ids or [0]).strip('[]') + ')'
        product_total_qty_qry = """select product_id, sum(product_uom_qty) from stock_move mv Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer' where state='done' and product_id in %s and date between '%s 00:00:00' and '%s 23:59:59' and product_id in %s group by product_id """ % (product_id_str, thirty_days_str, today, all_product_ids_str)
        self._cr.execute(product_total_qty_qry)
        product_total_sale_qty_lst = self._cr.fetchall()
        product_total_sale_qty_dict = dict(product_total_sale_qty_lst)

        # # finding total sales($) in last 30 days for all inventory sheet
        product_total_sales_qry = """ select  product_id, sum(product_uom_qty * sale_price_unit) sales from stock_move mv  Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer' where state='done' and product_id in %s  and date between '%s 00:00:00' and '%s 23:59:59'and product_id in %s group by product_id """ % (product_id_str, thirty_days_str, today, all_product_ids_str)
        self._cr.execute(product_total_sales_qry)
        product_total_sales_lst = self._cr.fetchall()
        product_total_sales_dict = dict(product_total_sales_lst)
        
        return  product_total_sale_qty_dict, product_total_sales_dict
    
    @api.multi
    def prepare_dict_data(self, all_ware_or_loc_dict, product, average_cost, product_current_sale_price, product_qty, product_value, avarage_sale_price, total_sale_qty, total_sales_price):           
                   
        if all_ware_or_loc_dict.get(product.id):
            all_ware_or_loc_dict.update({product.id:{'default_code':product.default_code,
                                                    'name':product.name,
                                                    'average_cost':average_cost,
                                                    'current_sale_price':product_current_sale_price and product_current_sale_price[0][0] or 0,
                                                    'total_qty':product_qty,
                                                    'total_value':product_value,
                                                    'average_sale_price':avarage_sale_price,
                                                    'sales_qty':total_sale_qty,
                                                    'total_sales':total_sales_price}})
            
        else:
            all_ware_or_loc_dict.update({product.id:{'default_code':product.default_code,
                                                    'name':product.name,
                                                    'average_cost':average_cost,
                                                    'current_sale_price':product_current_sale_price and product_current_sale_price[0][0] or 0,
                                                    'total_qty':product_qty,
                                                    'total_value':product_value,
                                                    'average_sale_price':avarage_sale_price,
                                                    'sales_qty':total_sale_qty,
                                                    'total_sales':total_sales_price}})
    
        return  all_ware_or_loc_dict

    @api.multi
    def add_heading_all_ware_or_loc(self, workbook, header_bold, style, blank_cell_style):
        
        worksheet_all_inventory = workbook.add_sheet('All inventory', cell_overwrite_ok=True)
        
        worksheet_all_inventory.set_panes_frozen(True)
        worksheet_all_inventory.set_horz_split_pos(2) 
        worksheet_all_inventory.set_vert_split_pos(3)
        
        worksheet_all_inventory.row(0).height = 400
        worksheet_all_inventory.row(1).height = 400
        worksheet_all_inventory.col(0).width = 2500
        worksheet_all_inventory.col(1).width = 5000
        worksheet_all_inventory.col(2).width = 10000
        worksheet_all_inventory.col(3).width = 5000
        worksheet_all_inventory.col(4).width = 1200
        worksheet_all_inventory.col(5).width = 5000
        worksheet_all_inventory.col(6).width = 5000
        worksheet_all_inventory.col(7).width = 5000
        worksheet_all_inventory.col(8).width = 5000
        worksheet_all_inventory.col(9).width = 1200
        worksheet_all_inventory.col(10).width = 5000
        worksheet_all_inventory.col(11).width = 5000
        worksheet_all_inventory.col(12).width = 5000
        worksheet_all_inventory.col(13).width = 5000
        worksheet_all_inventory.col(14).width = 1200
        worksheet_all_inventory.col(15).width = 5000
        worksheet_all_inventory.col(16).width = 5000
        worksheet_all_inventory.col(17).width = 5000
        worksheet_all_inventory.col(18).width = 5000
        worksheet_all_inventory.col(19).width = 1200
        worksheet_all_inventory.col(20).width = 5000
        worksheet_all_inventory.col(21).width = 5000
        worksheet_all_inventory.col(22).width = 5000
        worksheet_all_inventory.col(23).width = 5000
        worksheet_all_inventory.col(24).width = 1200
        worksheet_all_inventory.col(25).width = 5000
        worksheet_all_inventory.col(26).width = 5000
        worksheet_all_inventory.col(27).width = 5000
        worksheet_all_inventory.col(28).width = 5000
         
        worksheet_all_inventory.write(1, 0, 'Odoo ID', header_bold)
        worksheet_all_inventory.write(1, 1, 'Odoo SKU', header_bold)
        worksheet_all_inventory.write(1, 2, 'Product Name', header_bold)
#         worksheet_all_inventory.write(1, 3, 'Average Cost', header_bold)
#         worksheet_all_inventory.write(1, 4, 'Current Sale Price', header_bold)
        worksheet_all_inventory.write(1, 3, 'Total Inventory Qty', header_bold)
#         worksheet_all_inventory.write(1, 6, 'Total Inventory value', header_bold)
#         worksheet_all_inventory.write(1, 8, 'Average Sale Price', header_bold)
#         worksheet_all_inventory.write(1, 9, 'Sales (qty)', header_bold)
#         worksheet_all_inventory.write(1, 10, 'Sales', header_bold)
        
#         worksheet_all_inventory.write_merge(0, 0, 8, 10, 'Last 30 days', style)
        merge_cell = col = 3

        for break_down_line in self.day_breakdown_line_ids:
            worksheet_all_inventory.write(1, col + 2, 'Qty', header_bold)
            worksheet_all_inventory.write(1, col + 3, 'Qty (% of overall)', header_bold)
            worksheet_all_inventory.write(1, col + 4, 'Value', header_bold)
            worksheet_all_inventory.write(1, col + 5, 'Value (% of overall)', header_bold)
            col = col + 5
            merge_cell = merge_cell + 2
            worksheet_all_inventory.write_merge(0, 0, merge_cell, merge_cell + 3, '%s - %s days old' % (break_down_line.day_start, break_down_line.day_end), style)
            merge_cell = merge_cell + 3

        worksheet_all_inventory.write(1, 4, None, blank_cell_style)
        worksheet_all_inventory.write(1, 9, None, blank_cell_style)
        worksheet_all_inventory.write(1, 14, None, blank_cell_style)
        worksheet_all_inventory.write(1, 19, None, blank_cell_style)
        worksheet_all_inventory.write(1, 24, None, blank_cell_style)

        return workbook, worksheet_all_inventory
    
    @api.multi
    def print_all_ware_or_loc_data(self, all_ware_or_loc_dict, worksheet_all_inventory, day_wise_value_dict, total_qty_and_values, default_code_style, inventory_value_style, blank_cell_style, sales_data_style, worksheet_1_30_days_style):
        column = 0
        row = 2
        if not all_ware_or_loc_dict:
            raise ValidationError('No data available for product in companies.')

        for product_id, product_data in all_ware_or_loc_dict.items():
            worksheet_all_inventory.row(row).height = 350
            worksheet_all_inventory.write(row, column, product_id, default_code_style)
            worksheet_all_inventory.write(row, column + 1, product_data.get('default_code') or '-', default_code_style)
            worksheet_all_inventory.write(row, column + 2, product_data.get('name'), default_code_style)
#             worksheet_all_inventory.write(row, column + 3, round(product_data. get('average_cost'), 2), inventory_value_style)
#             worksheet_all_inventory.write(row, column + 4, round(product_data.get('current_sale_price'), 2) or  0, inventory_value_style)
            worksheet_all_inventory.write(row, column + 3, product_data.get('total_qty'), inventory_value_style)
#             worksheet_all_inventory.write(row, column + 6, product_data.get('total_value'), inventory_value_style)
            worksheet_all_inventory.write(row, column + 4, None, blank_cell_style)
#             worksheet_all_inventory.write(row, column + 8, round(product_data.get('average_sale_price', False), 2), sales_data_style)
#             worksheet_all_inventory.write(row, column + 9, round(product_data.get('sales_qty', False), 2) or 0, sales_data_style)
#             worksheet_all_inventory.write(row, column + 10, round(product_data.get('total_sales', False), 2), sales_data_style)
#             worksheet_all_inventory.write(row, column + 11, None, blank_cell_style)

            column = 4
            for breakdown_line in self.day_breakdown_line_ids:
                overall_qty_breakdown_day_wise = 0
                overall_value_breakdown_day_wise = 0
                day_key_dict_name = '%s-%s' % (breakdown_line.day_start, breakdown_line.day_end)

                total_qty_sum_days_wise = day_wise_value_dict.get(day_key_dict_name).get('total_qty_sum_days_wise')
                total_inventory_value_days_wise = day_wise_value_dict.get(day_key_dict_name).get('total_inventory_value_days_wise')

                product_total_qty = total_qty_and_values.get((product_id, day_key_dict_name), {}) and total_qty_and_values.get((product_id, day_key_dict_name)).get('product_total_qty') or 0
                product_total_values = total_qty_and_values.get((product_id, day_key_dict_name), {}) and total_qty_and_values.get((product_id, day_key_dict_name)).get('product_total_values') or 0
 
                if total_qty_sum_days_wise > 0:
                    overall_qty_breakdown_day_wise = (product_total_qty / total_qty_sum_days_wise) * 100
                if total_inventory_value_days_wise > 0:
                    overall_value_breakdown_day_wise = (product_total_values / total_inventory_value_days_wise) * 100
 
                worksheet_all_inventory.write(row, column + 1, product_total_qty or 0, worksheet_1_30_days_style)
                worksheet_all_inventory.write(row, column + 2, round(overall_qty_breakdown_day_wise, 2), worksheet_1_30_days_style)
                worksheet_all_inventory.write(row, column + 3, product_total_values or 0, worksheet_1_30_days_style)
                worksheet_all_inventory.write(row, column + 4, round(overall_value_breakdown_day_wise, 2), worksheet_1_30_days_style)
                worksheet_all_inventory.write(row, column + 5, None, blank_cell_style)
                column += 5

            row += 1
            column = 0

    @api.model
    def auto_generator_inventory_age_breakdown_report(self):
        return True
        today = datetime.now().strftime("%Y-%m-%d")
        product_obj = self.env['product.product']
        warehouse_obj = self.env['stock.warehouse']
        f_name = 'Inventory Age Breakdown Report for' + ' ' + today + '.xls'
        inventory_age_breakdown_id = self.create({})
        product_ids = product_obj.search([]) 
        warehouse_ids = warehouse_obj.search([])     
        inventory_age_breakdown_id.generate_inventory_age_breakdown_report(today, product_ids, warehouse_ids.ids)
        vals = {'name':'Inventory Age Breakdown Report.xls',
               'datas':inventory_age_breakdown_id.datas,
               'datas_fname':f_name,
                'type':'binary',
                'res_model': 'inventory.age.breakdown.report.ept'}
           
        attachment_id = self.env['ir.attachment'].create(vals)
        mail_template_view = self.env.ref('inventory_report_ept.mail_template_inventory_age_breakdown_report_ept')
        msg_ids = mail_template_view.send_mail(inventory_age_breakdown_id.id)
        mail_brow_obj = self.env['mail.mail'].browse(msg_ids)
        mail_brow_obj.write({'attachment_ids': [(6, 0, [attachment_id.id])]})
        mail_brow_obj.send()

        
class InventoryAgeBreakdownline(models.TransientModel):
    _name = "inventory.age.breakdown.line.ept"         
    
    day_start = fields.Integer('Day Start', required=True)
    day_end = fields.Integer('Day End', requird=True)     
    inventory_breakdown_id = fields.Many2one('inventory.age.breakdown.report.ept', 'Breakdown Report')

