from odoo import models, fields, api, _
import calendar
from odoo.tools import populate, groupby
from odoo.tools import OrderedSet, groupby
import datetime
from dateutil import relativedelta
from odoo.http import request
from datetime import date
from datetime import datetime
from dateutil import relativedelta
from odoo.http import request
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils, email_split, is_html_empty, groupby


class Purchaseorder(models.Model):
    _inherit = 'purchase.order'


    def formatINR(self, number):
        s, *d = str(number).partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        amt = "".join([r])
        return amt

    @api.model
    def get_all_state_count(self):
        res_obj = self.env['purchase.order']
        draft_total_counts = 0
        done_total_counts = 0
        sale_total_counts = 0
        sent_total_counts = 0

        inbox_len_counts = 0
        done_len_counts = 0
        sale_len_counts = 0
        sent_len_counts = 0


        draft_counts = res_obj.search([
            ('state', '=', 'draft'),
        ])
        done_counts = res_obj.search([
            ('state', '=', 'done'),
        ])
        purchase_counts = res_obj.search([
            ('state', '=', 'purchase'),
        ])
        sent_counts = res_obj.search([
            ('state', '=', 'sent'),
        ])
        for rec in draft_counts:
            draft_total_counts += rec.amount_total
            inbox_len_counts += 1
        for rec in done_counts:
            done_total_counts += rec.amount_total
            done_len_counts += 1
        for rec in purchase_counts:
            sale_total_counts += rec.amount_total
            sale_len_counts += 1
        for rec in sent_counts:
            sent_total_counts += rec.amount_total
            sent_len_counts += 1

        data_dct = {
            'inbox_count': self.formatINR(draft_total_counts),
            'done_count': self.formatINR(done_total_counts),
            'sale_count': self.formatINR(sale_total_counts),
            'sent_count': self.formatINR(sent_total_counts),
            'inbox_len_counts': inbox_len_counts,
            'done_len_counts': done_len_counts,
            'sale_len_counts': sale_len_counts,
            'sent_len_counts': sent_len_counts,
            'currency': self.env.user.company_id.currency_id.symbol,

        }
        return data_dct

    @api.model
    def top_10_product_by_qty(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)
        read_group_res = self.env['purchase.order.line'].read_group(
            [('date_order', '<=', end_date),
             ('date_order', '>=', start_date)], ['product_id', 'product_qty'],
            ['product_id', 'product_qty'], orderby='product_qty desc')
        top_10_product_qty = {}
        for rec in read_group_res:
            if rec['product_id'] != False:
                stage_name = str(rec['product_id'][1])
                if stage_name not in top_10_product_qty:
                    top_10_product_qty[stage_name] = 0
                top_10_product_qty[stage_name] += rec['product_qty']
        top_10_entities = dict(list(top_10_product_qty.items())[:10])
        return top_10_entities

    @api.model
    def top_10_product(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)
        read_group_res = self.env['purchase.order.line'].read_group(
            [('order_id.date_order', '<=', end_date),
             ('order_id.date_order', '>=', start_date)], ['product_id', 'price_subtotal'],
            ['product_id', 'price_subtotal'], orderby='price_subtotal desc')
        top_10_customer = {}
        for rec in read_group_res:
            if rec['product_id'] != False:
                stage_name = str(rec['product_id'][1])
                if stage_name not in top_10_customer:
                    total = 0.0
                    top_10_customer[stage_name] = 0
                    total += rec['price_subtotal']
            top_10_customer[stage_name] = self.formatINR(total)
        top_10_entities = dict(list(top_10_customer.items())[:10])
        return top_10_entities

    @api.model
    def top_10_customer(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)

        read_group_res = self.env['purchase.order'].read_group(
            [('date_order', '<=', end_date),
             ('date_order', '>=', start_date)],
            ['partner_id', 'amount_total'], ['partner_id', 'amount_total'])
        top_10_customer = {}

        for rec in read_group_res:
            if rec['partner_id'] != False:
                stage_name = str(rec['partner_id'][1])
                if stage_name not in top_10_customer:
                    top_10_customer[stage_name] = []
                top_10_customer[stage_name].insert(0, rec['partner_id_count'])
                top_10_customer[stage_name].insert(1, self.formatINR(rec['amount_total']))
        sorted_entities = sorted(top_10_customer.items(), key=lambda x: x[1], reverse=True)
        top_10_entities = sorted_entities[:10]
        converted_dict = {key: value for key, value in top_10_entities}
        for key in converted_dict:
            converted_dict[key] = converted_dict[key][1:]
        return converted_dict

    @api.model
    def top_10_by_filter(self, **kwargs):
        data_list = []
        data_product_amount = []
        data_product_qty = []
        currency = [self.env.user.company_id.currency_id.symbol]

        if kwargs['0']['customer_from_date'] and kwargs['0']['customer_to_date']:
            start_date = kwargs['0']['customer_from_date']
            end_date = kwargs['0']['customer_to_date']

            ### for top 10 customer  ###
            top_10_customer = {}
            read_group_res = self.env['purchase.order'].read_group(
                [('date_order', '<=', end_date),
                 ('date_order', '>=', start_date)],
                ['partner_id', 'amount_total'], ['partner_id', 'amount_total'])
            for rec in read_group_res:
                if rec['partner_id'] != False:
                    stage_name = str(rec['partner_id'][1])
                    if stage_name not in top_10_customer:
                        top_10_customer[stage_name] = []
                    top_10_customer[stage_name].insert(0, rec['partner_id_count'])
                    top_10_customer[stage_name].insert(1, self.formatINR(rec['amount_total']))
            sorted_entities = sorted(top_10_customer.items(), key=lambda x: x[1], reverse=True)
            top_10_entities = sorted_entities[:10]
            converted_dict = {key: value for key, value in top_10_entities}
            for key in converted_dict:
                converted_dict[key] = converted_dict[key][1:]
            for rec in converted_dict:
                top_1 = {}
                top_1[rec] = converted_dict[rec]
                data_list.append(top_1)

            ### For Top 10 Product By Amount ###
            read_group_res = self.env['purchase.order.line'].read_group(
                [('order_id.date_order', '<=', end_date),
                 ('order_id.date_order', '>=', start_date)], ['product_id', 'price_subtotal'],
                ['product_id', 'price_subtotal'], orderby='price_subtotal desc')
            top_10_amount = {}
            for rec in read_group_res:
                if rec['product_id'] != False:
                    stage_name = str(rec['product_id'][1])
                    if stage_name not in top_10_amount:
                        total = 0.0
                        top_10_amount[stage_name] = 0
                        total += rec['price_subtotal']
                top_10_amount[stage_name] = self.formatINR(total)
            top_10_product_entities = dict(list(top_10_amount.items())[:10])
            for rec in top_10_product_entities:
                top_product_amount = {}
                top_product_amount[rec] = top_10_product_entities[rec]
                data_product_amount.append(top_product_amount)

            ### For Top 10 Product By Qty ###

            read_group_res = self.env['purchase.order.line'].read_group(
                [('order_id.date_order', '<=', end_date),
                 ('order_id.date_order', '>=', start_date)], ['product_id', 'product_qty'],
                ['product_id', 'product_qty'], orderby='product_qty desc')

            top_10_qty = {}
            for rec in read_group_res:
                if rec['product_id'] != False:
                    stage_name = str(rec['product_id'][1])
                    if stage_name not in top_10_qty:
                        top_10_qty[stage_name] = 0
                    top_10_qty[stage_name] += rec['product_qty']
            top_10_product_qty = dict(list(top_10_qty.items())[:10])
            for rec in top_10_product_qty:
                top_product_qty = {}
                top_product_qty[rec] = top_10_product_qty[rec]
                data_product_qty.append(top_product_qty)
        return data_list, data_product_amount, data_product_qty,currency

    def get_financial_quarter_dates(self, year, quarter, fiscal_start_month):
        # start_month = (quarter - 1) * 3 + fiscal_start_month
        start_date = datetime(year, fiscal_start_month, 1)
        end_date = datetime(year, fiscal_start_month + 2, calendar.monthrange(year, fiscal_start_month + 2)[1])

        return start_date, end_date

    @api.model
    def purchase_product_graph(self, **kwargs):
        today = fields.Datetime.today()
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)

        if kwargs['0']:
            duration = kwargs['0']['time_interval']
            if duration == 'this_month':
                start_date = date.today().replace(day=1)
                end_date = date.today() + relativedelta(day=31)
            if duration == 'last_month':
                start_date = date.today().replace(day=1) - relativedelta(months=1)
                end_date = date.today() + relativedelta(day=31) - relativedelta(months=1)
            if duration == 'quarter_1':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 4

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)
            if duration == 'quarter_2':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 7

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)
            if duration == 'quarter_3':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 10

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)

            if duration == 'quarter_4':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 1

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)

            if duration == 'this_year':
                start_date = date_utils.start_of(today, "year")
                end_date = date_utils.end_of(today, "year").date()

            if duration == 'last_year':
                last_year = today + relativedelta(years=-1)
                start_date = date_utils.start_of(last_year, 'year')
                end_date = date_utils.end_of(last_year, "year").date()

        read_group_res = self.env['purchase.order.line'].read_group(
            [('order_id.date_order', '<=', end_date),
             ('order_id.date_order', '>=', start_date)], ['product_id', 'product_qty'],
            ['product_id', 'product_qty'], orderby='product_qty desc')
        products_name = []
        products_qty = []
        graph_product = {}
        for rec in read_group_res:
            if rec['product_id'] != False:
                products_name.append(str(rec['product_id'][1]))
                products_qty.append(rec['product_qty'])
                stage_name = str(rec['product_id'][1])
                if stage_name not in graph_product:
                    graph_product[stage_name] = 0
                graph_product[stage_name] += rec['product_qty']
        products_name_list = []
        product_qty = {}
        products_qty_list = []
        product_qty['data'] = []
        product_qty['backgroundColor'] =  [
            '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
            '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
            '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
            ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
            '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
            '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
            '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
            '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
            '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
            '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
        ]
        product_qty['label'] = 'Products'

        for recs in graph_product:
            products_name_list.append(recs)
            product_qty['data'].append(graph_product[recs])
        products_qty_list.append(product_qty)
        return products_name_list, products_qty_list

    @api.model
    def customer_on_graph_purchase(self, **kwargs):
        today = fields.Datetime.today()
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)
        if kwargs['0']:
            duration = kwargs['0']['time_interval']
            if duration == 'this_month':
                start_date = date.today().replace(day=1)
                end_date = date.today() + relativedelta(day=31)
            if duration == 'last_month':
                start_date = date.today().replace(day=1) - relativedelta(months=1)
                end_date = date.today() + relativedelta(day=31) - relativedelta(months=1)
            if duration == 'quarter_1':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 4

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)
            if duration == 'quarter_2':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 7

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)
            if duration == 'quarter_3':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 10

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)

            if duration == 'quarter_4':
                current_year = datetime.now().year
                current_quarter = (datetime.now().month - 1) // 3 + 1
                fiscal_start_month = 1

                start_date, end_date = self.get_financial_quarter_dates(current_year, current_quarter,
                                                                        fiscal_start_month)

            if duration == 'this_year':
                start_date = date_utils.start_of(today, "year")
                end_date = date_utils.end_of(today, "year").date()

            if duration == 'last_year':
                last_year = today + relativedelta(years=-1)
                start_date = date_utils.start_of(last_year, 'year')
                end_date = date_utils.end_of(last_year, "year").date()
        read_group_res = self.env['purchase.order'].read_group(
            [('date_order', '<=', end_date),
             ('date_order', '>=', start_date)],
            ['partner_id', 'amount_total'], ['partner_id', 'amount_total'])
        partner_name = []
        partner_amount = []
        graph_customer = {}

        for rec in read_group_res:
            if rec['partner_id'] != False:
                partner_name.append(str(rec['partner_id'][1]))
                partner_amount.append(rec['amount_total'])
                stage_name = str(rec['partner_id'][1])
                if stage_name not in graph_customer:
                    graph_customer[stage_name] = 0
                graph_customer[stage_name] += rec['amount_total']

        customer_name_list = []
        customer_product_qty = {}
        customer_products_qty_list = []
        customer_product_qty['data'] = []
        customer_product_qty['backgroundColor'] = [
            '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
            '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
            '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
            ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
            '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
            '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
            '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
            '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
            '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
            '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
        ]
        customer_product_qty['label'] = 'Vendor'

        for recs in graph_customer:
            customer_name_list.append(recs)
            customer_product_qty['data'].append(graph_customer[recs])
        customer_products_qty_list.append(customer_product_qty)
        return customer_name_list, customer_products_qty_list