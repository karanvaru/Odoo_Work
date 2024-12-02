from odoo import models, fields, api, _
import calendar
import datetime
from datetime import datetime
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta


class Saleorder(models.Model):
    _inherit = 'sale.order'


    @api.model
    def _get_financial_year(self):
        date = fields.date.today()
        year_of_date = date.year
        financial_year_start_date = datetime.strptime(str(year_of_date) + "-04-01", "%Y-%m-%d").date()
        if date < financial_year_start_date:
            financial_year_start_date = financial_year_start_date + relativedelta(months=-12)

        financial_year_end_date = financial_year_start_date + relativedelta(months=12, days=-1)
        return financial_year_start_date, financial_year_end_date

    def formatINR(self, number):
        s, *d = str(number).partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        amt = "".join([r])
        return amt

    def state_count(self, start, end):
        res_obj = self.env['sale.order'].sudo().search([('date_order', '>=', start),
                                                        ('date_order', '<=', end)], )

        inbox_total_counts = 0
        done_total_counts = 0
        sale_total_counts = 0
        sent_total_counts = 0

        inbox_len_counts = 0
        done_len_counts = 0
        sale_len_counts = 0
        sent_len_counts = 0
        data_dct = {}
        inbox_counts = res_obj.search([
            ('state', '=', 'draft'),
            ('date_order', '>=', start),
            ('date_order', '<=', end)
        ])
        done_counts = res_obj.search([
            ('state', '=', 'done'),
            ('date_order', '>=', start),
            ('date_order', '<=', end)
        ])
        sale_counts = res_obj.search([
            ('state', '=', 'sale'),
            ('date_order', '>=', start),
            ('date_order', '<=', end)

        ])
        sent_counts = res_obj.search([
            ('state', '=', 'sent'),
            ('date_order', '>=', start),
            ('date_order', '<=', end)
        ])
        data_dct['draft'] = []
        data_dct['sent'] = []
        data_dct['done'] = []
        data_dct['sale'] = []
        for rec in inbox_counts:
            # data_dct['draft'] = []
            inbox_total_counts += rec.amount_total
            inbox_len_counts += 1
        data_dct['draft'].append(self.formatINR(inbox_total_counts))
        data_dct['draft'].append(inbox_len_counts)
        for rec in done_counts:
            # data_dct['Done'] = []
            done_total_counts += rec.amount_total
            done_len_counts += 1
        data_dct['done'].append(self.formatINR(done_total_counts))
        data_dct['done'].append(done_len_counts)
        for rec in sale_counts:
            # data_dct['sale'] = []
            sale_total_counts += rec.amount_total
            sale_len_counts += 1
        data_dct['sale'].append(self.formatINR(sale_total_counts))
        data_dct['sale'].append(sale_len_counts)
        for rec in sent_counts:
            sent_total_counts += rec.amount_total
            sent_len_counts += 1
        data_dct['sent'].append(self.formatINR(sent_total_counts or 0))
        data_dct['sent'].append(sent_len_counts or 0)

        # data_dct = {
        #     'inbox_count': self.formatINR(inbox_total_counts),
        #     'done_count': self.formatINR(done_total_counts),
        #     'sale_count': self.formatINR(sale_total_counts),
        #     'sent_count': self.formatINR(sent_total_counts),
        #     'inbox_len_counts': inbox_len_counts,
        #     'done_len_counts': done_len_counts,
        #     'sale_len_counts': sale_len_counts,
        #     'sent_len_counts': sent_len_counts,
        #     'currency': self.env.user.company_id.currency_id.symbol,
        # }
        print("__________________  dataaa",data_dct)
        return data_dct

    @api.model
    def get_tickets_all_count(self):
        start_date, end_date = self._get_financial_year()
        state = self.state_count(start_date, end_date)
        return state


    @api.model
    def top_10_by_filter(self, **kwargs):
        data_list = []
        data_product_amount = []
        data_product_qty = []

        state_list = []
        product_list = []
        currency = [self.env.user.company_id.currency_id.symbol]
        if kwargs['0']['customer_from_date'] and kwargs['0']['customer_to_date']:
            start_date = kwargs['0']['customer_from_date']
            end_date = kwargs['0']['customer_to_date']
            state = self.state_count(start_date, end_date)

            product = self.sale_product(start_date, end_date)
            customer = self.sale_customer(start_date, end_date)
            # product_list.append(product)
            ### for top 10 customer  ###
            top_10_customer = {}
            read_group_res = self.env['sale.order'].read_group(
                [('date_order', '<=', end_date),
                 ('date_order', '>=', start_date)],
                ['partner_id', 'amount_total'], ['partner_id', 'amount_total'])
            for rec in read_group_res:
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

            read_group_res = self.env['sale.order.line'].read_group(
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
            top_10_product_entities = dict(list(top_10_amount.items()))
            for rec in top_10_product_entities:
                top_product_amount = {}
                top_product_amount[rec] = top_10_product_entities[rec]
                data_product_amount.append(top_product_amount)

            ### For Top 10 Product By Quantity###

            read_group_res = self.env['sale.order.line'].read_group(
                [('order_id.date_order', '<=', end_date),
                 ('order_id.date_order', '>=', start_date)], ['product_id', 'product_uom_qty'],
                ['product_id', 'product_uom_qty'], orderby='product_uom_qty desc')

            top_10_qty = {}
            for rec in read_group_res:
                if rec['product_id'] != False:
                    stage_name = str(rec['product_id'][1])
                    if stage_name not in top_10_qty:
                        top_10_qty[stage_name] = 0
                    top_10_qty[stage_name] += rec['product_uom_qty']
            top_10_product_qty = dict(list(top_10_qty.items()))
            for rec in top_10_product_qty:
                top_product_qty = {}
                top_product_qty[rec] = top_10_product_qty[rec]
                data_product_qty.append(top_product_qty)

            date_beween_product = []

        return data_list, data_product_amount, data_product_qty, currency, product, customer,state

    @api.model
    def top_10_customer(self):
        # start_date = date.today().replace(day=1)
        # end_date = date.today() + relativedelta(day=31)
        start_date, end_date = self._get_financial_year()
        read_group_res = self.env['sale.order'].read_group(
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
        # top_10_entities = sorted_entities[:10]
        converted_dict = {key: value for key, value in sorted_entities}
        for key in converted_dict:
            converted_dict[key] = converted_dict[key][1:]
        return converted_dict

    @api.model
    def top_10_product(self):
        start_date, end_date = self._get_financial_year()
        # start_date = date.today().replace(day=1)
        # end_date = date.today() + relativedelta(day=31)
        read_group_res = self.env['sale.order.line'].read_group(
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
        top_10_entities = dict(list(top_10_customer.items()))
        return top_10_entities

    @api.model
    def top_10_product_by_qty(self):
        start_date, end_date = self._get_financial_year()

        read_group_res = self.env['sale.order.line'].read_group(
            [('order_id.date_order', '<=', end_date),
             ('order_id.date_order', '>=', start_date)], ['product_id', 'product_uom_qty'],
            ['product_id', 'product_uom_qty'], orderby='product_uom_qty desc')

        top_10_customer = {}
        for rec in read_group_res:
            if rec['product_id'] != False:
                stage_name = str(rec['product_id'][1])
                if stage_name not in top_10_customer:
                    top_10_customer[stage_name] = 0
                top_10_customer[stage_name] += rec['product_uom_qty']
        top_10_entities = dict(list(top_10_customer.items()))
        return top_10_entities

    def get_financial_quarter_dates(self, year, quarter, fiscal_start_month):
        # start_month = (quarter - 1) * 3 + fiscal_start_month
        start_date = datetime(year, fiscal_start_month, 1)
        end_date = datetime(year, fiscal_start_month + 2, calendar.monthrange(year, fiscal_start_month + 2)[1])

        return start_date, end_date

    @api.model
    def sale_product_graph(self, **kwargs):
        start_date, end_date = self._get_financial_year()
        data = self.sale_product(start_date, end_date)
        return data

    @api.model
    def sale_product(self, start_date, end_date):
        read_group_res = self.env['sale.order.line'].read_group(
            [('order_id.date_order', '<=', end_date),
             ('order_id.date_order', '>=', start_date)], ['product_id', 'product_uom_qty'],
            ['product_id', 'product_uom_qty'], orderby='product_uom_qty desc')
        products_name = []
        graph_list = []
        products_qty = []
        graph_product = {}
        for rec in read_group_res:
            if rec['product_id'] != False:
                products_name.append(str(rec['product_id'][1]))
                products_qty.append(rec['product_uom_qty'])
                stage_name = str(rec['product_id'][1])
                if stage_name not in graph_product:
                    graph_product[stage_name] = 0
                graph_product[stage_name] += rec['product_uom_qty']
        for rec in graph_product:
            graph_dct = {}
            graph_dct.update({
                'name': rec,
                'value': graph_product[rec]
            })
            graph_list.append(graph_dct)
        graph_list.sort(key=lambda x: x['value'], reverse=True)

        return graph_list

    @api.model
    def sale_customer_graph(self, **kwargs):
        start_date, end_date = self._get_financial_year()
        data = self.sale_customer(start_date, end_date)
        return data

    @api.model
    def sale_customer(self, start_date, end_date):
        # start_date, end_date = self._get_financial_year()

        read_group_res = self.env['sale.order'].read_group(
            [('date_order', '<=', end_date),
             ('date_order', '>=', start_date)],
            ['partner_id', 'amount_total'], ['partner_id', 'amount_total'])

        partner_name = []
        partner_amount = []
        graph_list = []
        graph_customer = {}

        for rec in read_group_res:
            if rec['partner_id'] != False:
                partner_name.append(str(rec['partner_id'][1]))
                partner_amount.append(rec['amount_total'])
                stage_name = str(rec['partner_id'][1])
                if stage_name not in graph_customer:
                    graph_customer[stage_name] = 0
                graph_customer[stage_name] += rec['amount_total']
        for rec in graph_customer:
            graph_dct = {}
            graph_dct.update({
                'name': rec,
                'value': graph_customer[rec]
            })
            graph_list.append(graph_dct)
        graph_list.sort(key=lambda x: x['value'], reverse=True)
        return graph_list

    @api.model
    def get_year_finience(self):
        date = fields.date.today()
        year_of_date = date.year
        financial_year_start_date = datetime.strptime(str(year_of_date) + "-04-01", "%Y-%m-%d").date()
        if date < financial_year_start_date:
            financial_year_start_date = financial_year_start_date + relativedelta(months=-12)

        financial_year_end_date = financial_year_start_date + relativedelta(months=12, days=-1)
        # date_list = []
        data_dct = {
            'start_date': financial_year_start_date,
            'end_date': financial_year_end_date,
        }
        return data_dct
