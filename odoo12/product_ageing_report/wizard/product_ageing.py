# -*- coding: utf-8 -*-

from odoo import fields,api, models, _
from odoo.exceptions import UserError
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AgeingAnalysis(models.TransientModel):
    _name = 'product.ageing'

    from_date = fields.Datetime(string="Starting Date", required=True)
    location_id = fields.Many2many('stock.location', string="Location", domain=[('usage', '=', 'internal')])
    product_categ = fields.Many2many('product.category', string="Category")
    interval = fields.Integer(string="Interval(days)", default=30, required=True)
    filter_by = fields.Selection([
        ('location', "Location"), ('lot', "Lot"),
    ], string="Expand By", default='lot')

    @api.model
    def compute_ageing(self, data):
        """Redirects to the report with the values obtained from the wizard
                'data['form']':  date duration"""
        rec = self.browse(data)
        data = {}
        data['form'] = rec.read(['from_date', 'location_id', 'product_categ', 'interval'])
        return self.env.ref('product_ageing_report.report_product_ageing').report_action(self,data=data)

    @api.model
    def xlsx_ageing_report(self, data):
        rec = self.browse(data)
        data = {}
        data['form'] = rec.read(['from_date', 'location_id', 'product_categ', 'interval', 'filter_by'])
        if not rec.filter_by:
            raise ValidationError('Please select a Expand Option for Report')
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'product.ageing',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Product Ageing report',
                     }
        }

    @api.model
    def ageing_report_values(self, options):
        """we are overwriting this function because we need to show values from other models in the report
                we pass the objects in the docargs dictionary"""

        self.model = self.env.context.get('active_model')
        docs = self.env['product.ageing'].browse(self.env.context.get('active_id'))
        products = self.ageing_xlsx_report(docs.from_date, docs.interval, docs.product_categ, docs.location_id,
                                           docs.filter_by, options)
        interval = ['0-' + str(options[0]['interval']),
                    str(options[0]['interval']) + '-' + str(2 * options[0]['interval']),
                    str(2 * options[0]['interval']) + '-' + str(3 * options[0]['interval']),
                    str(3 * options[0]['interval']) + '-' + str(4 * options[0]['interval']),
                    str(4 * options[0]['interval']) + '+']
        loc = ""
        categ = ""
        for i in docs.location_id:
            if i.location_id.name and i.name:
                loc += i.location_id.name + " / " + i.name + ", "
        for i in docs.product_categ:
            if i.name:
                categ += i.name + ", "
        loc = loc[:-2]
        categ = categ[:-2]
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'loc': loc,
            'categ': categ,
            'interval': interval,
            'products': products,
        }
        return docargs, products

    def ageing_xlsx_report(self, from_date, interval, product_categ, location_id,filter_by, options):
        location_id = options[0]['location_id']
        product_categ = options[0]['product_categ']
        from_date = options[0]['from_date']
        interval = options[0]['interval']
        cr = self._cr
        if location_id and product_categ:
            cr.execute("select sq.id as quant,pp.id as product from stock_quant sq "
                       "join product_product pp on (pp.id = sq.product_id) "
                       "join product_template pt on (pt.id=pp.product_tmpl_id and pt.categ_id in %s) "
                       "join stock_location st on st.id = sq.location_id"
                       " where sq.location_id in %s and sq.quantity > 0 and sq.in_date <=%s and st.usage ='internal'"
                       ,
                       (tuple(product_categ),
                        tuple(location_id), from_date))
        elif location_id:
            cr.execute(
                "select sq.id as quant ,sq.product_id as product from stock_quant sq "
                "join stock_location st on st.id = sq.location_id"
                " where sq.location_id in %s and sq.quantity > 0 and st.usage ='internal'"
                "and sq.in_date <=%s ",
                (tuple(location_id), from_date))
        elif product_categ:
            cr.execute("select sq.id as quant,pp.id as product from stock_quant sq "
                       "join product_product pp on(pp.id=sq.product_id) "
                       "join product_template pt on(pt.id=pp.product_tmpl_id and pt.categ_id in %s)"
                       " join stock_location st on st.id = sq.location_id"
                       " where sq.quantity > 0  and sq.in_date <=%s and st.usage ='internal'"
                       "", (tuple(product_categ), from_date))
        else:
            cr.execute("select sq.id as quant,sq.product_id as product from stock_quant sq"
                       " join stock_location st on st.id = sq.location_id"
                       " where quantity > 0  and in_date <=%s  and st.usage ='internal'"
                       , (from_date,))
        product_ids = cr.dictfetchall()
        products = {}
        product = []
        for i in product_ids:
            if i['product'] not in product:
                product.append(i['product'])
        for pr in product:
            quant = []
            for val in product_ids:
                if val['product'] == pr:
                    quant.append(val['quant'])
            cr.execute(" select pt.name as product,sq.quantity as quantity ,st.name as location,lot.name as lot ,"
                       " sq.in_date as in_date"
                       " from stock_quant sq "
                        "join product_product pp on (pp.id = sq.product_id)"
                       " join product_template pt on (pt.id=pp.product_tmpl_id)"
                       " join stock_production_lot lot on lot.id=sq.lot_id"  
                        " join stock_location st on st.id = sq.location_id"
                        " where sq.lot_id IS NOT NULL  and sq.id in %s",
                       (tuple(quant),))
            rec_with_lot = cr.dictfetchall()
            cr.execute(" select pt.name as product,sq.quantity as quantity ,st.name as location,sq.in_date as in_date "
                       " from stock_quant sq "
                       "join product_product pp on (pp.id = sq.product_id)"
                       "join product_template pt on (pt.id=pp.product_tmpl_id)"
                       " join stock_location st on st.id = sq.location_id"
                       " where sq.lot_id IS NULL  and sq.id in %s",
                       (tuple(quant),))
            rec_without_lot = cr.dictfetchall()
            vals = []
            date1 = datetime.datetime.strptime(str(from_date), '%Y-%m-%d %H:%M:%S').date()
            if rec_with_lot:
                for re in rec_with_lot:
                    flag = 0
                    if vals:
                        for val in vals:
                            if val['location'] == re['location'] and val['lot'] == re['lot']:
                                date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                                no_days = (date1 - date2).days
                                t1 = 0
                                t2 = interval
                                for j in range(0, 5):
                                    if no_days >= 4 * interval:
                                        val['quantity'][4] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    elif no_days in range(t1, t2):
                                        val['quantity'][j] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    t1 = t2
                                    t2 += interval
                                age_range = len([x for x in val['quantity'] if x != 0])
                                if age_range > 1:
                                    val['age'] = ''
                                else:
                                    val['age'] = no_days
                                flag = 1
                        if not flag:
                            temp = {
                                'product': re['product'],
                                'location': re['location'],
                                'lot': re['lot'],
                                'total_qty': re['quantity']
                            }
                            quantity = [0, 0, 0, 0, 0]

                            date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                            no_days = (date1 - date2).days
                            t1 = 0
                            t2 = interval
                            for j in range(0, 5):
                                if no_days >= 4 * interval:
                                    quantity[4] += re['quantity']
                                    break
                                elif no_days in range(t1, t2):
                                    quantity[j] += re['quantity']
                                    break

                                t1 = t2
                                t2 += interval
                            temp['quantity'] = quantity
                            age_range = len([x for x in temp['quantity'] if x != 0])
                            if age_range > 1:
                                temp['age'] = ''
                            else:
                                temp['age'] = no_days
                            vals.append(temp)

                    else:
                        temp = {
                            'product': re['product'],
                            'location': re['location'],
                            'lot': re['lot'],
                            'total_qty': re['quantity']
                        }
                        quantity = [0, 0, 0, 0, 0]
                        date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                        no_days = (date1 - date2).days
                        t1 = 0
                        t2 = interval
                        for j in range(0, 5):
                            if no_days >= 4 * interval:
                                quantity[4] += re['quantity']
                                break
                            elif no_days in range(t1, t2):
                                quantity[j] += re['quantity']
                                break

                            t1 = t2
                            t2 += interval
                        temp['quantity'] = quantity
                        age_range = len([x for x in temp['quantity'] if x != 0])
                        if age_range > 1:
                            temp['age'] = ''
                        else:
                            temp['age'] = no_days
                        vals.append(temp)
            vals_without_lot = []
            if rec_without_lot:
                for re in rec_without_lot:
                    flag = 0
                    if vals_without_lot:
                        for val in vals_without_lot:
                            if val['location'] == re['location']:
                                date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                                no_days = (date1 - date2).days
                                t1 = 0
                                t2 = interval
                                for j in range(0, 5):
                                    if no_days >= 4 * interval:
                                        val['quantity'][4] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    elif no_days in range(t1, t2):
                                        val['quantity'][j] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    t1 = t2
                                    t2 += interval
                                flag = 1
                        if not flag:
                            temp = {
                                'product': re['product'],
                                'location': re['location'],
                                'lot': '',
                                'total_qty': re['quantity'],
                                'age': ''
                            }
                            quantity = [0, 0, 0, 0, 0]

                            date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                            no_days = (date1 - date2).days
                            t1 = 0
                            t2 = interval
                            for j in range(0, 5):
                                if no_days >= 4 * interval:
                                    quantity[4] += re['quantity']
                                    break
                                elif no_days in range(t1, t2):
                                    quantity[j] += re['quantity']
                                    break

                                t1 = t2
                                t2 += interval
                            temp['quantity'] = quantity
                            vals_without_lot.append(temp)

                    else:
                        temp = {
                            'product': re['product'],
                            'location': re['location'],
                            'lot': '',
                            'total_qty': re['quantity'],
                            'age': ''
                        }
                        quantity = [0, 0, 0, 0, 0]

                        date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                        no_days = (date1 - date2).days
                        t1 = 0
                        t2 = interval
                        for j in range(0, 5):
                            if no_days >= 4 * interval:
                                quantity[4] += re['quantity']
                                break
                            elif no_days in range(t1, t2):
                                quantity[j] += re['quantity']
                                break

                            t1 = t2
                            t2 += interval
                        temp['quantity'] = quantity
                        vals_without_lot.append(temp)
            products[pr] = vals + vals_without_lot
        return products

    def get_xlsx_report(self, data, response):

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Product Ageing Report')
        # formats
        format1 = workbook.add_format({'font_size': 15, 'align': 'center', 'bg_color': '#8a98a8', 'bold': True})
        formt11 = workbook.add_format({'align': 'left', 'font_size': 10, 'bottom': 1})
        formt112 = workbook.add_format({'align': 'left', 'font_size': 10, 'bottom': 1,'right':1})
        format5 = workbook.add_format({'align': 'left', 'font_size': 10})
        format6 = workbook.add_format({'align': 'left', 'font_size': 10, 'bg_color': '#8a98a8', 'bottom': 1})
        format61 = workbook.add_format({'align': 'center', 'font_size': 10, 'bg_color': '#8a98a8', 'bottom': 1,'bold':True})
        format62 = workbook.add_format(
            {'align': 'left', 'font_size': 10, 'bg_color': '#8a98a8', 'bottom': 1, 'bold': True})
        format51 = workbook.add_format({'align': 'left', 'font_size': 10, 'bg_color': '#a7b2be', 'bottom': 1})
        format512 = workbook.add_format(
            {'align': 'left', 'font_size': 10, 'bg_color': '#a7b2be', 'bottom': 1, 'right': 1})
        format52 = workbook.add_format({'align': 'left', 'font_size': 10, 'bg_color': '#c4ccd4', 'bottom': 1})
        format521 = workbook.add_format({'align': 'left', 'font_size': 10, 'bg_color': '#c4ccd4', 'bottom': 1, 'right': 1})
        format7 = workbook.add_format({'font_size': 10, 'bg_color': '#a7b2be',  'align': 'right', 'bottom': 1, 'bold':True})
        format72 = workbook.add_format(
            {'font_size': 10, 'bg_color': '#a7b2be', 'align': 'right', 'bottom': 1})
        format71 = workbook.add_format(
            {'font_size': 10, 'bg_color': '#c4ccd4', 'align': 'right', 'bottom': 1})
        format73 = workbook.add_format(
            {'font_size': 10, 'bg_color': '#c4ccd4', 'align': 'right', 'bottom': 1, 'bold': True})
        form81 = workbook.add_format({'font_size': 10, 'align': 'right', 'bottom': 1})
        sheet.set_row(0, 30)
        vals, products = self.ageing_report_values(data['form'])
        sheet.merge_range('A1:K1', 'PRODUCT AGEING REPORT', format1)
        sheet.write('A3', 'From Date', format6)
        sheet.write('A4',data['form'][0]['from_date'], format5)
        sheet.write('B3', '', format6)
        sheet.write('B4', '', format5)
        sheet.write('C3', 'Locations', format6)
        location_names = self.env['stock.location'].search([('id', 'in', data['form'][0]['location_id'])]).mapped('name')
        if location_names:
            sheet.write('C4', ','.join(map(str, location_names)), format5)
        else:
            sheet.write('C4', '', format5)
        sheet.write('D3', '', format6)
        sheet.write('D4', '', format5)
        sheet.write('E3', 'Categories', format6)
        category_names = self.env['product.category'].search([('id', 'in', data['form'][0]['product_categ'])]).mapped('name')
        if category_names:
            sheet.write('E4',  ','.join(map(str, category_names)), format5)
        else:
            sheet.write('E4', '', format5)
        sheet.write('F3', '', format6)
        sheet.write('F4', '', format5)
        sheet.write('G3', 'Report Date', format6)
        sheet.write('H3', '', format6)
        sheet.write('I3', '', format6)
        sheet.write('J3', '', format6)
        sheet.write('K3', '', format6)
        report_date = datetime.datetime.now().strftime("%Y-%m-%d")
        sheet.write('G4', report_date, format5)
        sheet.write('A6', 'SL NO', format61)
        sheet.write('B6', 'PRODUCT', format61)
        sheet.write('C6', 'LOCATION', format61)
        sheet.write('D6', 'LOT', format61)
        sheet.write('E6', 'AGE', format62)
        sheet.write('F6', str(vals['interval'][0]), format61)
        sheet.write('G6', str(vals['interval'][1]), format61)
        sheet.write('H6', str(vals['interval'][2]), format61)
        sheet.write('I6', str(vals['interval'][3]), format61)
        sheet.write('J6', str(vals['interval'][4]), format61)
        sheet.write('K6', 'TOTAL', format61)
        row_num = 6
        col_num = 0
        s_no = 1
        for i in products:
            g_sum = 0
            gsum_col1 = gsum_col2 = gsum_col3 = gsum_col4 = gsum_col5 = 0
            locations = list({v['location']: v for v in products[i]}.values())
            product_o = self.env['product.product'].search([('id', '=', i)], limit=1)
            product = product_o.display_name if product_o else 'Unknown'
            if len(locations) > 1:
                row_num_old = row_num
                row_num += 1
                for loc in locations:
                    total_sum = 0
                    sum_col1 = sum_col2 = sum_col3 = sum_col4 = sum_col5 = 0
                    vals = []
                    for val1 in products[i]:
                        if val1['location'] == loc['location']:
                            total_sum += val1['total_qty']
                            sum_col1 += val1['quantity'][0]
                            sum_col2 += val1['quantity'][1]
                            sum_col3 += val1['quantity'][2]
                            sum_col4 += val1['quantity'][3]
                            sum_col5 += val1['quantity'][4]
                            vals.append(val1)

                    sheet.write(row_num, col_num, '', format52)
                    sheet.write(row_num, col_num + 1, '', format52)
                    sheet.write(row_num, col_num + 2, loc['location'], format52)
                    sheet.write(row_num, col_num + 3, '', format52)
                    sheet.write(row_num, col_num + 4, '', format521)
                    sheet.write(row_num, col_num + 5, sum_col1, format71)
                    sheet.write(row_num, col_num + 6, sum_col2, format71)
                    sheet.write(row_num, col_num + 7, sum_col3, format71)
                    sheet.write(row_num, col_num + 8, sum_col4, format71)
                    sheet.write(row_num, col_num + 9, sum_col5, format71)
                    sheet.write(row_num, col_num + 10, total_sum, format73)
                    row_num = row_num + 1
                    if data['form'][0]['filter_by'] == 'lot':
                        for val in vals:

                            sheet.write(row_num, col_num, '', formt11)
                            sheet.write(row_num, col_num + 1, '', formt11)
                            sheet.write(row_num, col_num + 2, '', formt11)
                            sheet.write(row_num, col_num + 3, val['lot'], formt11)
                            sheet.write(row_num, col_num + 4, val['age'], formt112)
                            sheet.write(row_num, col_num + 5, val['quantity'][0], form81)
                            sheet.write(row_num, col_num + 6, val['quantity'][1], form81)
                            sheet.write(row_num, col_num + 7, val['quantity'][2], form81)
                            sheet.write(row_num, col_num + 8, val['quantity'][3], form81)
                            sheet.write(row_num, col_num + 9, val['quantity'][4], form81)
                            sheet.write(row_num, col_num + 10, val['total_qty'], form81)
                            row_num = row_num + 1
                    g_sum += total_sum
                    gsum_col1 += sum_col1
                    gsum_col2 += sum_col2
                    gsum_col3 += sum_col3
                    gsum_col4 += sum_col4
                    gsum_col5 += sum_col5
                sheet.write(row_num_old, col_num, s_no, format51)
                sheet.write(row_num_old, col_num + 1, product, format51)
                sheet.write(row_num_old, col_num + 2, '', format51)
                sheet.write(row_num_old, col_num + 3, '', format51)
                sheet.write(row_num_old, col_num + 4, '', format512)
                sheet.write(row_num_old, col_num + 5, gsum_col1, format72)
                sheet.write(row_num_old, col_num + 6, gsum_col2, format72)
                sheet.write(row_num_old, col_num + 7, gsum_col3, format72)
                sheet.write(row_num_old, col_num + 8, gsum_col4, format72)
                sheet.write(row_num_old, col_num + 9, gsum_col5, format72)
                sheet.write(row_num_old, col_num + 10, g_sum, format7)
                s_no = s_no + 1
            else:
                for val in products[i]:
                    sheet.write(row_num, col_num, s_no, format51)
                    sheet.write(row_num, col_num + 1, product, format51)
                    sheet.write(row_num, col_num + 2, val['location'], format51)
                    sheet.write(row_num, col_num + 3, val['lot'], format51)
                    sheet.write(row_num, col_num + 4, val['age'], format512)
                    sheet.write(row_num, col_num + 5, val['quantity'][0], format72)
                    sheet.write(row_num, col_num + 6, val['quantity'][1], format72)
                    sheet.write(row_num, col_num + 7, val['quantity'][2], format72)
                    sheet.write(row_num, col_num + 8, val['quantity'][3], format72)
                    sheet.write(row_num, col_num + 9, val['quantity'][4], format72)
                    sheet.write(row_num, col_num + 10, val['total_qty'], format7)
                    row_num = row_num + 1
                    s_no = s_no + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

