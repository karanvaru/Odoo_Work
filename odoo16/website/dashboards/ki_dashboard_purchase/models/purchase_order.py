from odoo import models, fields, api, _
import calendar
import datetime
from datetime import datetime
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta


class Purchaseorder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_financial_year(self):
        date = fields.date.today()
        end_date = fields.Date.today()
        # initialize the current year
        year_of_date = date.year
        # initialize the current financial year start date
        financial_year_start_date = datetime.strptime(str(year_of_date) + "-04-01", "%Y-%m-%d").date()
        if date < financial_year_start_date:
            financial_year_start_date = financial_year_start_date + relativedelta(months=-12)

        financial_year_end_date = financial_year_start_date + relativedelta(months=12, days=-1)
        return financial_year_start_date, financial_year_end_date

    @api.model
    def get_year_finience(self):
        date = fields.date.today()
        end_date = fields.Date.today()
        # initialize the current year
        year_of_date = date.year
        # initialize the current financial year start date
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

    def formatINR(self, number):
        s, *d = str(number).partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        amt = "".join([r])
        return amt

    def state_count_purchase(self, start_date, end_date):
        res_obj = self.env['purchase.order'].sudo().search([])
        draft_total_counts = 0
        done_total_counts = 0
        sale_total_counts = 0
        sent_total_counts = 0

        inbox_len_counts = 0
        done_len_counts = 0
        sale_len_counts = 0
        sent_len_counts = 0
        data_dct = {}
        draft_counts = res_obj.search([
            ('state', '=', 'draft'),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        done_counts = res_obj.search([
            ('state', '=', 'done'),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        purchase_counts = res_obj.search([
            ('state', '=', 'purchase'),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        sent_counts = res_obj.search([
            ('state', '=', 'sent'),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        data_dct['draft'] = []
        data_dct['done'] = []
        data_dct['purchase'] = []
        data_dct['sent'] = []

        for rec in draft_counts:
            draft_total_counts += rec.amount_total
            inbox_len_counts += 1
        data_dct['draft'].append(self.formatINR(draft_total_counts))
        data_dct['draft'].append(inbox_len_counts)
        for rec in done_counts:
            done_total_counts += rec.amount_total
            done_len_counts += 1
        data_dct['done'].append(self.formatINR(done_total_counts))
        data_dct['done'].append(done_len_counts)
        for rec in purchase_counts:
            sale_total_counts += rec.amount_total
            sale_len_counts += 1
        data_dct['purchase'].append(self.formatINR(sale_total_counts))
        data_dct['purchase'].append(sale_len_counts)
        for rec in sent_counts:
            sent_total_counts += rec.amount_total
            sent_len_counts += 1
        data_dct['sent'].append(self.formatINR(sent_total_counts))
        data_dct['sent'].append(sent_len_counts)
        # data_dct['currency'] = self.env.user.company_id.currency_id.symbol

        # data_dct = {
        #     'inbox_count': self.formatINR(draft_total_counts),
        #     'done_count': self.formatINR(done_total_counts),
        #     'sale_count': self.formatINR(sale_total_counts),
        #     'sent_count': self.formatINR(sent_total_counts),
        #     'inbox_len_counts': inbox_len_counts,
        #     'done_len_counts': done_len_counts,
        #     'sale_len_counts': sale_len_counts,
        #     'sent_len_counts': sent_len_counts,
        #     'currency': self.env.user.company_id.currency_id.symbol,
        #
        # }
        print("_______________  data_dct", data_dct)
        return data_dct

    @api.model
    def get_all_state_count(self):
        start_date, end_date = self._get_financial_year()
        state = self.state_count_purchase(start_date, end_date)
        return state

        # res_obj = self.env['purchase.order']
        # draft_total_counts = 0
        # done_total_counts = 0
        # sale_total_counts = 0
        # sent_total_counts = 0
        #
        # inbox_len_counts = 0
        # done_len_counts = 0
        # sale_len_counts = 0
        # sent_len_counts = 0
        #
        # draft_counts = res_obj.search([
        #     ('state', '=', 'draft'),
        # ])
        # done_counts = res_obj.search([
        #     ('state', '=', 'done'),
        # ])
        # purchase_counts = res_obj.search([
        #     ('state', '=', 'purchase'),
        # ])
        # sent_counts = res_obj.search([
        #     ('state', '=', 'sent'),
        # ])
        # for rec in draft_counts:
        #     draft_total_counts += rec.amount_total
        #     inbox_len_counts += 1
        # for rec in done_counts:
        #     done_total_counts += rec.amount_total
        #     done_len_counts += 1
        # for rec in purchase_counts:
        #     sale_total_counts += rec.amount_total
        #     sale_len_counts += 1
        # for rec in sent_counts:
        #     sent_total_counts += rec.amount_total
        #     sent_len_counts += 1
        #
        # data_dct = {
        #     'inbox_count': self.formatINR(draft_total_counts),
        #     'done_count': self.formatINR(done_total_counts),
        #     'sale_count': self.formatINR(sale_total_counts),
        #     'sent_count': self.formatINR(sent_total_counts),
        #     'inbox_len_counts': inbox_len_counts,
        #     'done_len_counts': done_len_counts,
        #     'sale_len_counts': sale_len_counts,
        #     'sent_len_counts': sent_len_counts,
        #     'currency': self.env.user.company_id.currency_id.symbol,
        #
        # }
        # return data_dct

    @api.model
    def top_10_product_by_qty(self):
        # start_date = date.today().replace(day=1)
        # end_date = date.today() + relativedelta(day=31)
        start_date, end_date = self._get_financial_year()
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
        top_10_entities = dict(list(top_10_product_qty.items()))
        return top_10_entities

    @api.model
    def top_10_product(self):
        start_date, end_date = self._get_financial_year()
        # start_date = date.today().replace(day=1)
        # end_date = date.today() + relativedelta(day=31)
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
        top_10_entities = dict(list(top_10_customer.items()))
        return top_10_entities

    @api.model
    def top_10_customer(self):
        # start_date = date.today().replace(day=1)
        # end_date = date.today() + relativedelta(day=31)
        start_date, end_date = self._get_financial_year()
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
        # top_10_entities = sorted_entities[:10]
        converted_dict = {key: value for key, value in sorted_entities}
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
            product = self.purchase_product(start_date, end_date)
            customer = self.customer_on_purchase(start_date, end_date)
            state = self.state_count_purchase(start_date, end_date)
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
            # top_10_entities = sorted_entities[:10]
            converted_dict = {key: value for key, value in sorted_entities}
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
            top_10_product_entities = dict(list(top_10_amount.items()))
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
            top_10_product_qty = dict(list(top_10_qty.items()))
            for rec in top_10_product_qty:
                top_product_qty = {}
                top_product_qty[rec] = top_10_product_qty[rec]
                data_product_qty.append(top_product_qty)
        return data_list, data_product_amount, data_product_qty, currency, product, customer, state

    def get_financial_quarter_dates(self, year, quarter, fiscal_start_month):
        start_date = datetime(year, fiscal_start_month, 1)
        end_date = datetime(year, fiscal_start_month + 2, calendar.monthrange(year, fiscal_start_month + 2)[1])

        return start_date, end_date

    @api.model
    def purchase_product_graph(self, **kwargs):
        start_date, end_date = self._get_financial_year()
        data = self.purchase_product(start_date, end_date)
        return data

    @api.model
    def purchase_product(self, start_date, end_date):
        read_group_res = self.env['purchase.order.line'].read_group(
            [('order_id.date_order', '<=', end_date),
             ('order_id.date_order', '>=', start_date)], ['product_id', 'product_qty'],
            ['product_id', 'product_qty'], orderby='product_qty desc')
        products_name = []
        products_qty = []
        graph_product = {}
        graph_list = []
        for rec in read_group_res:
            if rec['product_id'] != False:
                products_name.append(str(rec['product_id'][1]))
                products_qty.append(rec['product_qty'])
                stage_name = str(rec['product_id'][1])
                if stage_name not in graph_product:
                    graph_product[stage_name] = 0
                graph_product[stage_name] += rec['product_qty']
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
    def customer_on_graph_purchase(self, **kwargs):
        start_date, end_date = self._get_financial_year()
        data = self.customer_on_purchase(start_date, end_date)
        return data

    @api.model
    def customer_on_purchase(self, start_date, end_date):
        read_group_res = self.env['purchase.order'].read_group(
            [('date_order', '<=', end_date),
             ('date_order', '>=', start_date)],
            ['partner_id', 'amount_total'], ['partner_id', 'amount_total'])
        partner_name = []
        partner_amount = []
        graph_customer = {}
        graph_customer_list = []
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
            graph_customer_list.append(graph_dct)
        graph_customer_list.sort(key=lambda x: x['value'], reverse=True)
        return graph_customer_list
