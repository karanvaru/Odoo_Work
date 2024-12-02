# Copyright (c) 2018 Emipro Technologies Pvt Ltd (www.emiprotechnologies.com). All rights reserved.
from odoo import models, fields, api, _

from datetime import datetime
from odoo.exceptions import  UserError, Warning, ValidationError
from io import  BytesIO
from dateutil import parser
from itertools import chain
import collections
import base64

try:
    import xlwt
    from xlwt import Borders
except ImportError:
    xlwt = None


class InventoryAgeReport(models.TransientModel):
 
    _name = "inventory.age.report.ept"

    def _get_company_domain(self):
        """
        Returns domain for company_ids.
        """
        return [('id', 'in', self.env.user.company_ids.ids)]

    datas = fields.Binary('File')
#     report_wise = fields.Selection([('Warehouse', 'Warehouse'), ('Location', 'Location')], string='Generate Report Based on', default='Warehouse')
#     warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
#     location_ids = fields.Many2many('stock.location', string='Locations', domain=[('usage', 'not in', ['view', 'customer', 'supplier', 'procurement'])])
    company_ids = fields.Many2many("res.company", domain=lambda self:self._get_company_domain())
    include_all_products = fields.Boolean("Include All Products", default=True)
    product_ids = fields.Many2many("product.product", string="Products")
    
    @api.multi
    def get_data(self):
        today = datetime.now().strftime("%Y-%m-%d")
        product_obj = self.env['product.product']
        if not self.company_ids:
            raise Warning(_("Please select at least one company."))          
        if not self.include_all_products:
            all_product_ids = self.product_ids 
        else:
            all_product_ids = product_obj.with_context(active_test=True).search([])

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
        
#         inventory_datas = {'active_id': self.env.context.get('active_id', [])}
#         res = self.read(['report_wise', 'warehouse_ids', 'location_ids', 'product_ids']) 
        single_inventory_dict, all_inventory_dict = self.prepare_data(today, all_product_ids, self.company_ids)
        return single_inventory_dict, all_inventory_dict
    
    @api.multi
    def get_single_inventory_dict(self):
        single_inventory_dict, all_inventory_dict = self.get_data()
        for company_id, data in single_inventory_dict.items():
            total_qty = 0
            total_inv = 0
            for product_data in data:
                total_qty += product_data.get('product_qty')
                total_inv += product_data.get('product_inventory_value')
            
            for dict in data:
                overall_qty = (dict.get('product_qty') / total_qty) * 100
                dict.update({'overall_qty' : round(overall_qty, 5)}) 
                
                if total_inv :
                    overall_inv = (dict.get('product_inventory_value') / total_inv) * 100
                else : 
                    overall_inv = 0   
                dict.update({'overall_inv' : round(overall_inv, 5)})
        return single_inventory_dict
    
    @api.multi
    def get_all_inventory_dict(self):
        single_inventory_dict, all_inventory_dict = self.get_data()
        
        total_qty = 0
        total_inv = 0

        for product_id , product_data in all_inventory_dict.items():
            total_qty += product_data.get('product_qty')
            total_inv += product_data.get('product_inventory_value')
            
        for product_data in all_inventory_dict.values():
            overall_qty = (product_data.get('product_qty') / total_qty) * 100
            product_data.update({'overall_qty': round(overall_qty, 5)})
            
            if not product_data.get('product_inventory_value'):
                overall_inv = 0
            else:
                overall_inv = (product_data.get('product_inventory_value') / total_inv) * 100
            product_data.update({'overall_inv': round(overall_inv, 5)})
        
        new_value_list = []
        for warehouse_id, data_details in single_inventory_dict.items():
            for product_data in data_details:
                product_oldest_qty = product_data.get('product_oldest_qty')
                proudct_id = product_data.get('product_id')
                product_oldest_qty_day = product_data.get('product_oldest_qty_day')
                new_value_list.append({'proudct_id':proudct_id, 'product_oldest_qty':product_oldest_qty, 'product_oldest_qty_day':product_oldest_qty_day})
        
        for product_id, product_data in all_inventory_dict.items():
            for oldest_qty in new_value_list:
                if oldest_qty.get('proudct_id') == product_id:
                    if oldest_qty.get('product_oldest_qty_day') == product_data.get('product_oldest_qty_day'):
                        product_data.update({'product_oldest_qty':oldest_qty.get('product_oldest_qty') or 0})
        
        return all_inventory_dict
    
    @api.multi
    def download_pdf_report(self):
        
        if not self.include_all_products:
            all_product_ids = self.product_ids 
        else:
            all_product_ids = self.env['product.product'].with_context(active_test=True).search([])
         
        if not all_product_ids:
            raise ValidationError("Please select Include All Products or Products.")

        return self.env.ref('inventory_report_ept.action_download_pdf_report_ept').report_action(self)        
    
    @api.multi
    def print_inventory_age_report(self):
        active_id = self.ids[0]
        today = datetime.now().strftime("%Y-%m-%d")
        product_obj = self.env['product.product']
        f_name = 'Inventory Age Report for' + ' ' + today
#         if not self.report_wise:
#             raise UserError(_("Please select the report generation field."))          
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
                    
#                     locations = location_obj.browse(list(set(list(chain(*location_lst)))))
#                 else:
#                     return True            
#                 warehouse_or_location = locations.ids

        if self.company_ids:
            self.generate_inventory_age_report(today, all_product_ids)
        else:
            raise UserError(_("Please select at least one company."))
            
        if self.datas:
            return {
            'type' : 'ir.actions.act_url',
            'url':   'web/content/?model=inventory.age.report.ept&download=true&field=datas&id=%s&filename=%s.xls' % (active_id, f_name),
            'target': 'new',
             }

    @api.multi
    def generate_inventory_age_report(self, today, all_product_ids):
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

        workbook, header_bold, body_style, qty_cell_style, value_style, days_style, sale_price_style, blank_cell_style = self.create_sheet()
       
        workbook, sheet_data, row_data = self.add_headings(companies, workbook, header_bold, blank_cell_style)
        
        workbook, worksheet_all_inventory = self.add_all_inv_headings(workbook, header_bold, blank_cell_style)
        
        single_inventory_dict, all_inventory_dict = self.sudo().prepare_data(today, all_product_ids, companies)
        
        self.print_data(single_inventory_dict, sheet_data, row_data, body_style, qty_cell_style, value_style, days_style, sale_price_style, blank_cell_style)
        
        self.print_all_inv_data(all_inventory_dict, single_inventory_dict, worksheet_all_inventory, body_style, qty_cell_style, value_style, days_style, sale_price_style, blank_cell_style)
        
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
        header_bold = xlwt.easyxf("font: bold on, height 200; pattern: pattern solid, fore_colour gray25;alignment: horizontal center ,vertical center")
        header_bold.borders = header_border
        body_style = xlwt.easyxf("font: height 200; alignment: horizontal left")
        body_style.borders = borders
        
        # # style for different colors in columns
        xlwt.add_palette_colour("light_blue_21", 0x21)
        workbook.set_colour_RGB(0x21, 153, 255, 255)  
        qty_cell_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour light_blue_21;  borders: top thin,right thin,bottom thin,left thin")
        
        xlwt.add_palette_colour("custom_orange", 0x22)
        workbook.set_colour_RGB(0x22, 255, 204, 153)
        value_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_orange;  borders: top thin,right thin,bottom thin,left thin")
        
        xlwt.add_palette_colour("custom_pink", 0x23)
        workbook.set_colour_RGB(0x23, 255, 204, 204)
        days_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_pink;  borders: top thin,right thin,bottom thin,left thin")
        
        xlwt.add_palette_colour("custom_green", 0x24)
        workbook.set_colour_RGB(0x24, 204, 255, 204)
        sale_price_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_green;  borders: top thin,right thin,bottom thin,left thin")
        
        xlwt.add_palette_colour("custom_yellow", 0x25)
        workbook.set_colour_RGB(0x25, 255, 255, 179)
        blank_cell_style = xlwt.easyxf("font: height 200,bold on, name Arial; align: horiz center, vert center;  pattern: pattern solid, fore_colour custom_yellow;  borders: top thin,right thin,bottom thin,left thin")
        return workbook, header_bold, body_style, qty_cell_style, value_style, days_style, sale_price_style, blank_cell_style
    
    @api.multi
    def add_headings(self, companies, workbook, header_bold, blank_cell_style):
        sheet_data = {}
        row_data = {}
        count = 0
        for company in companies:
            count += 1
#             company.name_worksheet = workbook.add_sheet('Sheet %s' % (count), cell_overwrite_ok=True)
#             if self.report_wise == 'Warehouse':
#                 ware_loc.name_worksheet = workbook.add_sheet('%s' % (ware_loc.name), cell_overwrite_ok=True)
#             else:
#                 ware_loc.name_worksheet = workbook.add_sheet('%s' % (ware_loc.complete_name), cell_overwrite_ok=True)

            company.name_worksheet = workbook.add_sheet('%s' % (company.name), cell_overwrite_ok=True)
            company.name_worksheet.row(0).height = 400
            company.name_worksheet.col(1).width = 6000
            company.name_worksheet.col(2).width = 10000
            company.name_worksheet.col(3).width = 3000
            company.name_worksheet.col(4).width = 7000
            company.name_worksheet.col(5).width = 1200
            company.name_worksheet.col(6).width = 5000
            company.name_worksheet.col(7).width = 4000
            company.name_worksheet.col(8).width = 1200
            company.name_worksheet.col(9).width = 3000
            company.name_worksheet.col(10).width = 7000
#             company.name_worksheet.col(11).width = 1200
#             company.name_worksheet.col(12).width = 5000
#             company.name_worksheet.col(13).width = 5000
#             company.name_worksheet.col(14).width = 5000
            row = 0
            company.name_worksheet.write(row, 0, "Company", header_bold)
            company.name_worksheet.write(row, 1, company.name, header_bold)
            company.name_worksheet.merge(row, row, 1, 2)
            row += 1
            company.name_worksheet.write(row, 0, 'Odoo ID', header_bold)
            company.name_worksheet.write(row, 1, 'Odoo SKU', header_bold)
            company.name_worksheet.write(row, 2, 'Product Name', header_bold)
            company.name_worksheet.write(row, 3, 'Total Qty', header_bold)
            company.name_worksheet.write(row, 4, 'Qty (% of Overall Inventory)', header_bold)
            company.name_worksheet.write(row, 6, 'Qty (Oldest)', header_bold)
            company.name_worksheet.write(row, 7, 'Days Old (Oldest)', header_bold)
            company.name_worksheet.write(row, 9, 'Value (%s)' % (company.currency_id.symbol), header_bold)
            company.name_worksheet.write(row, 10, 'Value (% Of Overall Inventory)', header_bold)
#             company.name_worksheet.write(row, 12, 'Average Cost', header_bold)
#             company.name_worksheet.write(row, 13, 'Average Sale Price', header_bold)
#             company.name_worksheet.write(row, 14, 'Current Sale Price', header_bold)
            
            # #writing yellow color in blank cells
            company.name_worksheet.write(row, 5, None, blank_cell_style)
            company.name_worksheet.write(row, 8, None, blank_cell_style)
#             company.name_worksheet.write(row, 11, None, blank_cell_style)
            
            # # freezing columns
            company.name_worksheet.set_panes_frozen(True)
            company.name_worksheet.set_horz_split_pos(2) 
            company.name_worksheet.set_vert_split_pos(3)
            
            # #Get warehouse wise worksheet
            sheet_data.update({company.id: company.name_worksheet})
            
            # #initialize  worksheet wise row value
            row_data.update({company.name_worksheet: 2})
        
        return workbook, sheet_data, row_data
    
    @api.multi
    def add_all_inv_headings(self, workbook, header_bold, blank_cell_style):
        worksheet_all_inventory = workbook.add_sheet('All Inventory', cell_overwrite_ok=True)
        worksheet_all_inventory.row(0).height = 400
        worksheet_all_inventory.col(1).width = 6000
        worksheet_all_inventory.col(2).width = 10000
        worksheet_all_inventory.col(3).width = 3000
        worksheet_all_inventory.col(4).width = 7000
        worksheet_all_inventory.col(5).width = 1200
        worksheet_all_inventory.col(6).width = 5000
        worksheet_all_inventory.col(7).width = 4000
        worksheet_all_inventory.col(8).width = 1200
        worksheet_all_inventory.col(9).width = 3000
        worksheet_all_inventory.col(10).width = 7000
#         worksheet_all_inventory.col(11).width = 1200
#         worksheet_all_inventory.col(12).width = 5000
#         worksheet_all_inventory.col(13).width = 5000
#         worksheet_all_inventory.col(14).width = 5000
        worksheet_all_inventory.write(0, 0, 'Odoo ID', header_bold)
        worksheet_all_inventory.write(0, 1, 'Odoo SKU', header_bold)
        worksheet_all_inventory.write(0, 2, 'Product Name', header_bold)
        worksheet_all_inventory.write(0, 3, 'Total Qty', header_bold)
        worksheet_all_inventory.write(0, 4, 'Qty (% of Overall Inventory)', header_bold)
        worksheet_all_inventory.write(0, 6, 'Qty (Oldest)', header_bold)
        worksheet_all_inventory.write(0, 7, 'Days Old (Oldest)', header_bold)
        worksheet_all_inventory.write(0, 9, 'Value', header_bold)
        worksheet_all_inventory.write(0, 10, 'Value (% Of Overall Inventory)', header_bold)
#         worksheet_all_inventory.write(0, 12, 'Average Cost', header_bold)
#         worksheet_all_inventory.write(0, 13, 'Average Sale Price', header_bold)
#         worksheet_all_inventory.write(0, 14, 'Current Sale Price', header_bold)
        
        # #writing yellow color in blank cells
        worksheet_all_inventory.write(0, 5, None, blank_cell_style)
        worksheet_all_inventory.write(0, 8, None, blank_cell_style)
#         worksheet_all_inventory.write(0, 11, None, blank_cell_style)
        
        # # freezing columns
        worksheet_all_inventory.set_panes_frozen(True)
        worksheet_all_inventory.set_horz_split_pos(1) 
        worksheet_all_inventory.set_vert_split_pos(3)
    
        return workbook, worksheet_all_inventory
    
    @api.multi
    def prepare_data(self, today, all_product_ids, companies):
#         location_obj = self.env['stock.location']
#         warehouse_obj = self.env['stock.warehouse']
        stock_move_obj = self.env['stock.move']
        single_inventory_dict = {}
        all_inventory_dict = collections.OrderedDict()
        for company in companies:
            overall_product_qty = sum(all_product_ids.with_context(force_company=company.id).mapped('qty_available'))
            warehouses = self.env['stock.warehouse'].search([('company_id', '=', company.id)])
            child_locations_list = self.get_child_locations(warehouses.mapped('view_location_id'))
            total_inventory_value = self.find_total_value(today, child_locations_list)
            
            for product in all_product_ids:
                product_qty = product.with_context(force_company=company.id).qty_available

                if product_qty > 0:
                    move_ids = stock_move_obj.search([
                        ('location_dest_id', 'in', child_locations_list),
                        ('product_id', '=', product.id),
                        ('remaining_qty', '!=', False),
                        ('remaining_qty', '!=', 0),
                        ('state', '=', 'done')])

                    if move_ids:
                        oldest_date_str = min(move_ids.mapped('date'))
                        oldest_date = parser.parse(oldest_date_str.date().strftime('%Y-%m-%d'))   
                    else:
                        oldest_date = today

                    product_old = oldest_date
                    if isinstance(product_old, datetime):
                        product_old = product_old.strftime('%Y-%m-%d')
                    product_old_min = product_old + ' 00:00:00'
                    product_old_max = product_old + ' 23:59:59'

                    product_oldest_qty, product_oldest_qty_day = self.find_oldest_qty(stock_move_obj, child_locations_list, oldest_date, product, product_old_min, product_old_max)
                    if not product_oldest_qty:
                        continue

                    product_inventory_value = sum(move_ids.mapped('product_id.stock_value'))
                    if total_inventory_value and product_inventory_value:
                        product_overall_inventory_value = (product_inventory_value / total_inventory_value) * 100
                    else :
                        product_overall_inventory_value = 0

#                     product_current_sale_price = 0
#                     product_average_sale_price = 0
#                     product_average_cost = 0

                    single_inventory_dict, all_inventory_dict = self.write_data_dict(single_inventory_dict, all_inventory_dict, company, product, product_qty, overall_product_qty, product_oldest_qty, product_oldest_qty_day, product_inventory_value, product_overall_inventory_value)

        return single_inventory_dict, all_inventory_dict

#         if self.report_wise == 'Warehouse':
#             warehouse_ids = warehouse_obj.search([('id', 'in', warehouse_or_location)])
#             for warehouse in warehouse_ids:
#                 overall_product_qty = sum(all_product_ids.with_context(warehouse=warehouse.id).mapped('qty_available'))
#                 child_locations_list = self.get_child_locations(warehouse.lot_stock_id)
#                 total_inventory_value = self.find_total_value(stock_move_obj, today, child_locations_list)
#                     
#                 for product in all_product_ids:
#                     oldest_date_list = []
#                     product_current_qty = product.with_context(warehouse=warehouse.id)
#                     product_qty = product_current_qty.qty_available
#                     
#                     if product_qty > 0:
#                         move_ids = stock_move_obj.search([('location_dest_id', 'in', child_locations_list), ('product_id', '=', product.id), ('remaining_qty', '!=', False), ('remaining_qty', '!=', 0)])
#                         
#                         if move_ids:
#                             oldest_date_str = min(move_ids.mapped('date'))
#                             oldest_date = parser.parse(oldest_date_str.date().strftime('%Y-%m-%d'))   
#                             oldest_date_list.append(oldest_date)
#                         else:
#                             oldest_date = today
#                             oldest_date_list.append(oldest_date)
# 
#                         product_old = min(oldest_date_list)
#                         if isinstance(product_old, datetime):
#                             product_old = product_old.strftime('%Y-%m-%d')
#                         else:
#                             product_old = product_old
#                         product_old_min = product_old + ' 00:00:00'
#                         product_old_max = product_old + ' 23:59:59'
#                         
#                         product_oldest_qty, product_oldest_qty_day = self.find_oldest_qty(stock_move_obj, child_locations_list, oldest_date, product, product_old_min, product_old_max)
#                         if not product_oldest_qty:
#                             continue
#                         
#                         product_inventory_value = sum(move_ids.mapped('product_id.stock_value'))
#                         
#                         if total_inventory_value :
#                             product_overall_inventory_value = (product_inventory_value / total_inventory_value) * 100
#                         else :
#                             product_overall_inventory_value = 0
#                         po_move_line = stock_move_obj.search([('product_id', '=', product.id), ('location_dest_id', 'in', child_locations_list), ('purchase_line_id', '!=', False), ('state', '=', 'done')])
#                         total_unit_price = 0
#                         total_qty = 0
#                         for line in po_move_line:
#                             total_unit_price += line.purchase_line_id.qty_received * line.purchase_line_id.price_unit
#                             total_qty += line.purchase_line_id.qty_received
#                        
#                         if total_qty > 0:
#                             product_average_cost = total_unit_price / total_qty
#                         else:
#                             product_average_cost = 0
#                        
#                         sale_move = stock_move_obj.search([('product_id', '=', product.id), ('location_id', 'in', child_locations_list), ('sale_line_id', '!=', False), ('state', '=', 'done')]) 
#                         total_mv_qty = 0
#                         total_mv_price = 0
#                         for mv in sale_move:
#                             total_mv_price += mv.sale_line_id.qty_delivered * mv.sale_line_id.price_unit
#                             total_mv_qty += mv.sale_line_id.qty_delivered
#                        
#                         if total_mv_qty > 0:
#                             product_average_sale_price = total_mv_price / total_mv_qty
#                         else:
#                             product_average_sale_price = 0
#                             
#                         all_inv_sale_price_qry = """select sale_price_unit from stock_move mv Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer' where state='done' and product_id= %s and warehouse_id = %s order by date desc limit 1 """ % (product.id, warehouse.id)
#                         self._cr.execute(all_inv_sale_price_qry)
#                         product_current_sale_price = self._cr.fetchall()
#                         if isinstance(product_current_sale_price, list) and product_current_sale_price:
#                             product_current_sale_price = product_current_sale_price[0][0]
#                         else:
#                             product_current_sale_price = 0
#                         
#                         single_inventory_dict, all_inventory_dict = self.write_data_dict(single_inventory_dict, all_inventory_dict, warehouse, product, product_qty, overall_product_qty, product_oldest_qty, product_oldest_qty_day, product_inventory_value, product_overall_inventory_value, product_average_cost, product_average_sale_price, product_current_sale_price)

#         else:
#             locations_id = location_obj.search([('id', 'in', companies)])
#             if locations_id:
#                 for locations in locations_id:
#                     overall_product_qty = sum(all_product_ids.with_context(location=locations.id).mapped('qty_available'))
#                     child_locations_list = self.get_child_locations(locations)
#                     total_inventory_value = self.find_total_value(stock_move_obj, today, child_locations_list)
#                     product_oldest_qty = 0
#                     product_oldest_qty_day = 0
#                     for product in all_product_ids:
#                         oldest_date_list = []
#                         product_current_qty = product.with_context(location=locations.id)
#                         product_qty = product_current_qty.qty_available
#                         
#                         if product_qty > 0:
#                             move_ids = stock_move_obj.search([('location_dest_id', 'in', child_locations_list), ('product_id', '=', product.id), ('remaining_qty', '!=', False), ('remaining_qty', '!=', 0)])
#                             if move_ids:
#                                 oldest_date_str = min(move_ids.mapped('date'))
#                                 oldest_date = parser.parse(oldest_date_str.date().strftime('%Y-%m-%d'))   
#                                 oldest_date_list.append(oldest_date)
#                             else:
#                                 oldest_date = today
#                                 oldest_date_list.append(oldest_date)
#                        
#                             product_old = min(oldest_date_list)
#                             product_old = str(product_old).split(' ')[0] + ' 00:00:00'  # .strftime('%Y-%m-%d')
#                             product_old_min = product_old
#                             product_old_max = product_old.split(' ')[0] + ' 23:59:59'  # product_old + ' 23:59:59'
#                             
#                             product_oldest_qty, product_oldest_qty_day = self.find_oldest_qty(stock_move_obj, child_locations_list, oldest_date, product, product_old_min, product_old_max)
#                             sum_all_nagtive_value = self.find_oldest_move(stock_move_obj, oldest_date, product, child_locations_list)
#                         
#                             if not product_oldest_qty:
#                                 continue
#                             if sum_all_nagtive_value:
#                                 product_oldest_qty = sum_all_nagtive_value + product_oldest_qty
#                             
#                             product_inventory_value = sum(move_ids.mapped('product_id.stock_value'))
#                             
#                             if total_inventory_value :
#                                 product_overall_inventory_value = (product_inventory_value / total_inventory_value) * 100
#                             else :
#                                 product_overall_inventory_value = 0
#                             po_move_line = stock_move_obj.search([('product_id', '=', product.id), ('location_dest_id', 'in', child_locations_list), ('purchase_line_id', '!=', False), ('state', '=', 'done')])
#                             total_unit_price = 0
#                             total_qty = 0
#                             for line in po_move_line:
#                                 total_unit_price += line.purchase_line_id.qty_received * line.purchase_line_id.price_unit
#                                 total_qty += line.purchase_line_id.qty_received
#                            
#                             if total_qty > 0:
#                                 product_average_cost = total_unit_price / total_qty
#                             else:
#                                 product_average_cost = 0
#                        
#                             if not (locations.usage in ['transit', 'production', 'inventory']):
#                                 sale_move = stock_move_obj.search([('product_id', '=', product.id), ('location_id', 'in', child_locations_list), ('sale_line_id', '!=', False), ('state', '=', 'done')]) 
#                                 total_mv_qty = 0
#                                 total_mv_price = 0
#                                 for mv in sale_move:
#                                     total_mv_price += mv.sale_line_id.qty_delivered * mv.sale_line_id.price_unit
#                                     total_mv_qty += mv.sale_line_id.qty_delivered
#                                
#                                 if total_mv_qty > 0:
#                                     product_average_sale_price = total_mv_price / total_mv_qty
#                                 else:
#                                     product_average_sale_price = 0
#                         
#                                 all_inv_sale_price_qry = """select sale_price_unit from stock_move mv Inner join stock_location sl on sl.id = mv.location_dest_id and sl.usage='customer' where state='done' and product_id= %s and warehouse_id = %s order by date desc limit 1 """ % (product.id, locations.get_warehouse().id)
#                                 self._cr.execute(all_inv_sale_price_qry)
#                                 product_current_sale_price = self._cr.fetchall()
#                               
#                                 if isinstance(product_current_sale_price, list) and product_current_sale_price:
#                                     product_current_sale_price = product_current_sale_price[0][0]
#                                 else:
#                                     product_current_sale_price = 0
#                             
#                             else:
#                                 product_average_sale_price = 0
#                                 product_current_sale_price = 0
#                                 
#                             single_inventory_dict, all_inventory_dict = self.write_data_dict(single_inventory_dict, all_inventory_dict, locations, product, product_qty, overall_product_qty, product_oldest_qty, product_oldest_qty_day, product_inventory_value, product_overall_inventory_value, product_average_cost, product_average_sale_price, product_current_sale_price)

    @api.multi                          
    def find_total_value(self, today, child_locations_list):
        value_all = self.env['stock.move'].search([
            ('date', '<=', today),
            ('location_dest_id', 'in', child_locations_list)
            ])
        all_value = sum(value_all.mapped('product_id.stock_value'))
        return all_value
    
    @api.multi
    def find_oldest_move(self, stock_move_obj, oldest_date, product, child_locations_list):
        domain = [('date', '<=', oldest_date),
                  ('product_id', '=', product.id),
                  ('location_id', 'in', child_locations_list),
                  ('remaining_qty', '<', 0)]
        oldest_move = stock_move_obj.search(domain)
        if oldest_move:
            sum_all_nagtive_value = sum(oldest_move.mapped('remaining_qty'))
            return sum_all_nagtive_value
        else:
            return False

    @api.multi
    def find_oldest_qty(self, stock_move_obj, child_locations_list, oldest_date, product, product_old_min, product_old_max, oldest_qty=0, flag=True):
        product_oldest_ids = stock_move_obj.search([('product_id', '=', product.id),
                                                    ('location_dest_id', 'in', child_locations_list),
                                                    ('date', '>=', product_old_min),
                                                    ('date', '<=', product_old_max),
                                                    ('remaining_qty', '!=', False),
                                                    ('remaining_qty', '!=', 0)])
        tmp = False
        if not product_oldest_ids:
            return False, False
        total_oldest_qty = sum(product_oldest_ids.mapped('remaining_qty'))
        if flag:
            sum_all_nagtive_value = self.find_oldest_move(stock_move_obj, oldest_date, product, child_locations_list)
            total_oldest_qty = total_oldest_qty + sum_all_nagtive_value
        total_oldest_qty = total_oldest_qty + oldest_qty
        if total_oldest_qty <= 0:
            move_ids = stock_move_obj.search([('location_dest_id', 'in', child_locations_list), ('date', '>', product_old_max), ('product_id', '=', product.id), ('remaining_qty', '!=', False), ('remaining_qty', '!=', 0)])
            if move_ids:
                oldest_date_str = min(move_ids.mapped('date'))
                oldest_date = parser.parse(oldest_date_str.date().strftime('%Y-%m-%d'))   

            product_old_min = oldest_date + ' 00:00:00'
            product_old_max = oldest_date + ' 23:59:59'
            tmp, product_oldest_qty_day = self.find_oldest_qty(stock_move_obj, child_locations_list, oldest_date, product, product_old_min, product_old_max, total_oldest_qty, flag=False)
      
        today = datetime.now().strftime("%Y-%m-%d")
        to_date = datetime.strptime(today, "%Y-%m-%d")
        old_date = oldest_date
        product_oldest_qty_day = abs((to_date - old_date).days)
        if tmp:
            return tmp , product_oldest_qty_day  
        else:
            return total_oldest_qty , product_oldest_qty_day
    
    @api.multi
    def write_data_dict(self, single_inventory_dict, all_inventory_dict, company, product, product_qty, overall_product_qty, product_oldest_qty, product_oldest_qty_day, product_inventory_value, product_overall_inventory_value):
        
        if single_inventory_dict.get(company.id):
            single_inventory_dict.get(company.id).append({'product_id':product.id,
                                                             'default_code':product.default_code,
                                                             'name':product.name,
                                                             'product_qty':product_qty,
                                                             'product_overall_qty':(product_qty / overall_product_qty) * 100,
                                                             'product_oldest_qty':product_oldest_qty,
                                                             'product_oldest_qty_day':product_oldest_qty_day,
                                                             'product_inventory_value':product_inventory_value,
                                                             'product_overall_inventory_value':round(float(product_overall_inventory_value), 5)})
#                                                              'product_average_cost':round(float(product_average_cost), 4),
#                                                              'product_average_sale_price':round(float(product_average_sale_price or 0), 2) ,
#                                                              'product_current_sale_price':product_current_sale_price or 0})
        else:
            single_inventory_dict.update({company.id:[{'product_id':product.id,
                                                          'default_code':product.default_code,
                                                          'name':product.name,
                                                          'product_qty':product_qty,
                                                          'product_overall_qty':(product_qty / overall_product_qty) * 100,
                                                          'product_oldest_qty':product_oldest_qty,
                                                          'product_oldest_qty_day':product_oldest_qty_day,
                                                          'product_inventory_value':product_inventory_value,
                                                          'product_overall_inventory_value':round(float(product_overall_inventory_value), 5)}]})
#                                                           'product_average_cost':round(float(product_average_cost), 4),
#                                                           'product_average_sale_price':round(float(product_average_sale_price or 0), 2) ,
#                                                           'product_current_sale_price':product_current_sale_price or 0}]})
        
        if all_inventory_dict.get(product.id):
            product_data = all_inventory_dict.get(product.id)
            single_product_qty = product_data.get('product_qty')
            single_product_qty = single_product_qty + product_qty
            
            all_inv_days_old = product_data.get('product_oldest_qty_day')
            if product_oldest_qty_day > all_inv_days_old:
                all_inv_days_old = product_oldest_qty_day
            
            all_inv_value = product_data.get('product_inventory_value')
            all_inv_value = all_inv_value + product_inventory_value
            
            all_inv_product_value_per = product_data.get('product_overall_inventory_value')
            all_inv_product_value_per = all_inv_product_value_per + product_overall_inventory_value
            
            all_inventory_dict.update({product.id:{'default_code':product.default_code,
                                                'name':product.name,
                                                'product_qty':single_product_qty,
                                                'product_oldest_qty_day':all_inv_days_old,
                                                'product_inventory_value':all_inv_value,
                                                'product_overall_inventory_value':all_inv_product_value_per,
#                                                 'product_average_cost':all_inv_value / single_product_qty,
#                                                 'product_average_sale_price':round(float(product_average_sale_price or 0), 2) ,
#                                                 'product_current_sale_price':product_current_sale_price or 0
                                                }})
               
        else:
            all_inventory_dict.update({product.id:{'default_code':product.default_code,
                                          'name':product.name,
                                          'product_qty':product_qty,
                                          'product_oldest_qty':product_oldest_qty,
                                          'product_oldest_qty_day':product_oldest_qty_day,
                                          'product_inventory_value':product_inventory_value,
                                          'product_overall_inventory_value':round(float(product_overall_inventory_value), 5)}})
#                                           'product_average_cost':round(float(product_average_cost), 4),
#                                           'product_average_sale_price':round(float(product_average_sale_price or 0), 2) ,
#                                           'product_current_sale_price':product_current_sale_price or 0 }})
               
        return single_inventory_dict, all_inventory_dict
    
    @api.multi
    def print_data(self, single_inventory_dict, sheet_data, row_data, body_style, qty_cell_style, value_style, days_style, sale_price_style, blank_cell_style):
        row = 1
        column = 0
        new_qty = 0
        new_total_overall_qty = 0
        product_overall_value = 0
        new_product_overall_value = 0
        new_value_list = []
        
        if not single_inventory_dict:
#             if self.report_wise == 'Warehouse':
            raise ValidationError('No data available for product in companies.')
#             else:
#                 raise ValidationError('No data available for product in location.')
        
        for company_id, data_details in single_inventory_dict.items():
            new_qty = 0
            product_overall_value = 0
            for product_data in data_details:
                new_qty += product_data.get('product_qty')
                product_overall_value += product_data.get('product_inventory_value')
            new_value_list.append({'product_qty':new_qty, 'company_id':company_id, 'product_inventory_value':product_overall_value})
        
        for company_id, data_details in single_inventory_dict.items():
            for product_data in data_details:
                row = row_data[sheet_data[company_id]]
                sheet_data[company_id].row(row).height = 350
                sheet_data[company_id].write(row, column, product_data.get('product_id'), body_style)
                sheet_data[company_id].write(row, column + 1, product_data.get('default_code') or '-', body_style)
                sheet_data[company_id].write(row, column + 2, product_data.get('name'), body_style)
                sheet_data[company_id].write(row, column + 3, product_data.get('product_qty'), qty_cell_style)
                
                for new_value in new_value_list:
                    if new_value.get('company_id') == company_id:
                        overall_qty = new_value.get('product_qty')
                        product_total_value = new_value.get('product_inventory_value')
                        new_total_overall_qty = product_data.get('product_qty') / overall_qty * 100
                        if product_total_value:
                            new_product_overall_value = product_data.get('product_inventory_value') / product_total_value * 100
                        
                sheet_data[company_id].write(row, column + 4, round(new_total_overall_qty, 2), qty_cell_style)
                sheet_data[company_id].write(row, column + 5, None, blank_cell_style)
                sheet_data[company_id].write(row, column + 6, product_data.get('product_oldest_qty') , days_style)
                sheet_data[company_id].write(row, column + 7, product_data.get('product_oldest_qty_day') or 0, days_style)
                sheet_data[company_id].write(row, column + 8, None, blank_cell_style)
                sheet_data[company_id].write(row, column + 9, product_data.get('product_inventory_value') or 0, value_style)
                sheet_data[company_id].write(row, column + 10, round(new_product_overall_value, 2) or 0, value_style)
#                 sheet_data[company_id].write(row, column + 11, None, blank_cell_style)
#                 sheet_data[company_id].write(row, column + 12, round((product_data.get('product_average_cost') or 0), 2), sale_price_style)
#                 sheet_data[company_id].write(row, column + 13, product_data.get('product_average_sale_price') or 0, sale_price_style)
#                 sheet_data[company_id].write(row, column + 14, product_data.get('product_current_sale_price') or 0, sale_price_style)
                row += 1
                # #store row value worksheet wise
                row_data.update({sheet_data[company_id]: row})

        return True

    @api.multi
    def print_all_inv_data(self, all_inventory_dict, single_inventory_dict, worksheet_all_inventory, body_style, qty_cell_style, value_style, days_style, sale_price_style, blank_cell_style):
        row = 1
        column = 0
        new_qty = 0
        new_overall_inventory = 0
        new_value_list = []
        for company_id, data_details in single_inventory_dict.items():
            for product_data in data_details:
                product_oldest_qty = product_data.get('product_oldest_qty')
                proudct_id = product_data.get('product_id')
                product_oldest_qty_day = product_data.get('product_oldest_qty_day')
                new_value_list.append({'proudct_id':proudct_id, 'product_oldest_qty':product_oldest_qty, 'product_oldest_qty_day':product_oldest_qty_day})
        
        for product_id , product_data in all_inventory_dict.items():
            new_qty += product_data.get('product_qty')
            new_overall_inventory += product_data.get('product_inventory_value')
            
        for product_id, product_data in all_inventory_dict.items():
            new_inventory_value = 0
            worksheet_all_inventory.row(row).height = 350
            worksheet_all_inventory.write(row, column, product_id, body_style)
            worksheet_all_inventory.write(row, column + 1, product_data.get('default_code') or '-', body_style)
            worksheet_all_inventory.write(row, column + 2, product_data.get('name'), body_style)
            worksheet_all_inventory.write(row, column + 3, product_data.get('product_qty'), qty_cell_style)
            if new_qty:
                new_overall_qty = (product_data.get('product_qty') / new_qty) * 100
            worksheet_all_inventory.write(row, column + 4, round(new_overall_qty, 2), qty_cell_style)
            worksheet_all_inventory.write(row, column + 5, None, blank_cell_style)
            
            for oldest_qty in new_value_list:
                if oldest_qty.get('proudct_id') == product_id:
                    if oldest_qty.get('product_oldest_qty_day') == product_data.get('product_oldest_qty_day'):
                        worksheet_all_inventory.write(row, column + 6, oldest_qty.get('product_oldest_qty') or 0, days_style)
                
            worksheet_all_inventory.write(row, column + 7, product_data.get('product_oldest_qty_day') or 0, days_style)
            worksheet_all_inventory.write(row, column + 8, None, blank_cell_style)
            worksheet_all_inventory.write(row, column + 9, product_data.get('product_inventory_value') or 0, value_style)
            if new_overall_inventory:
                new_inventory_value = (product_data.get('product_inventory_value') / new_overall_inventory) * 100
            worksheet_all_inventory.write(row, column + 10, round(new_inventory_value, 5) or 0, value_style)
#             worksheet_all_inventory.write(row, column + 11, None, blank_cell_style)
#             worksheet_all_inventory.write(row, column + 12, round((product_data.get('product_average_cost') or 0), 2), sale_price_style)
#             worksheet_all_inventory.write(row, column + 13, product_data.get('product_average_sale_price') or 0, sale_price_style)
#             worksheet_all_inventory.write(row, column + 14, product_data.get('product_current_sale_price') or 0, sale_price_style)
            row += 1
        return True
    
    @api.model
    def auto_generator_inventory_age_report(self, ctx={}):
        return True
        today = datetime.now().strftime("%Y-%m-%d")
        f_name = 'Inventory Age Report for' + ' ' + today + '.xls'
        inventory_age_id = self.create({})
        product_obj = self.env['product.product']
        warehouse_obj = self.env['stock.warehouse']
        product_ids = product_obj.search([])
        warehouse_id = warehouse_obj.search([])
        warehouse_ids = warehouse_id.ids
        inventory_age_id.generate_inventory_age_report(today, product_ids, warehouse_ids)
        vals = {'name':'Inventory Age Report.xls',
               'datas':inventory_age_id.datas,
               'datas_fname':f_name,
               'type':'binary',
               'res_model': 'inventory.age.report.ept'}
        
        attachment_id = self.env['ir.attachment'].create(vals)
        mail_template_view = self.env.ref('inventory_report_ept.mail_template_inventory_age_report_ept')
        msg_ids = mail_template_view.send_mail(inventory_age_id.id)
        mail_brow_obj = self.env['mail.mail'].browse(msg_ids)
        mail_brow_obj.write({'attachment_ids': [(6, 0, [attachment_id.id])]})
        mail_brow_obj.send()
