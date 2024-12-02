from odoo import models, fields, api, _
import calendar
import datetime
from datetime import date
from datetime import datetime
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils, email_split, is_html_empty, groupby


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def formatINR(self, number):
        s, *d = str(number).partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        amt = "".join([r])
        return amt

    def get_financial_quarter_dates(self, year, quarter, fiscal_start_month):
        # start_month = (quarter - 1) * 3 + fiscal_start_month
        start_date = datetime(year, fiscal_start_month, 1)
        end_date = datetime(year, fiscal_start_month + 2, calendar.monthrange(year, fiscal_start_month + 2)[1])

        return start_date, end_date

    @api.model
    def get_crm_state(self):
        crm_lead_stage = self.read_group([], ['stage_id', 'expected_revenue'], ['stage_id', 'expected_revenue'])
        crm_stage_dict = {}
        for rec in crm_lead_stage:
            if rec['stage_id'] != False:
                stage_name = str(rec['stage_id'][1])
                if stage_name not in crm_stage_dict:
                    crm_stage_dict[stage_name] = []
                crm_stage_dict[stage_name].append(rec['expected_revenue'] or 0)
                crm_stage_dict[stage_name].append(rec['stage_id_count'])
        return crm_stage_dict

    @api.model
    def crm_top_10_customer(self):
        s_date = datetime.today().replace(day=1)
        e_date = datetime.today() + relativedelta(day=31)
        start_date = datetime.strftime(s_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strftime(e_date, '%Y-%m-%d %H:%M:%S')
        top_crm_partner = self.read_group(
            [('create_date', '<=', end_date),
             ('create_date', '>=', start_date)],
            ['partner_id', 'expected_revenue'], ['partner_id', 'expected_revenue'])
        top_10_crm_customer = {}

        for rec in top_crm_partner:
            if rec['partner_id'] != False:
                customer_name = str(rec['partner_id'][1])
                if customer_name not in top_10_crm_customer:
                    top_10_crm_customer[customer_name] = []
                top_10_crm_customer[customer_name].insert(0, rec['partner_id_count'])
                top_10_crm_customer[customer_name].insert(1, self.formatINR(rec['expected_revenue']))
        sorted_entities = sorted(top_10_crm_customer.items(), key=lambda x: x[1], reverse=True)
        top_10_crm_entities = sorted_entities[:10]
        crm_customer_dict = {key: value for key, value in top_10_crm_entities}
        for key in crm_customer_dict:
            crm_customer_dict[key] = crm_customer_dict[key][1:]
        return crm_customer_dict

    @api.model
    def crm_customer_graph(self, **kwargs):
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
        read_group_res = self.read_group(
            [('create_date', '<=', end_date),
             ('create_date', '>=', start_date)],
            ['partner_id', 'expected_revenue'], ['partner_id', 'expected_revenue'])
        crm_partner_name = []
        crm_partner_amount = []
        crm_graph_customer = {}

        for rec in read_group_res:
            if rec['partner_id'] != False:
                crm_partner_name.append(str(rec['partner_id'][1]))
                crm_partner_amount.append(rec['expected_revenue'])
                partner_name = str(rec['partner_id'][1])
                if partner_name not in crm_graph_customer:
                    crm_graph_customer[partner_name] = 0
                crm_graph_customer[partner_name] += rec['expected_revenue']

        crm_customer_name_list = []
        customer_crm_dict = {}
        crm_final_list = []
        customer_crm_dict['data'] = []
        customer_crm_dict['backgroundColor'] = [
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
        customer_crm_dict['label'] = 'Customer'

        for recs in crm_graph_customer:
            crm_customer_name_list.append(recs)
            customer_crm_dict['data'].append(crm_graph_customer[recs])
        crm_final_list.append(customer_crm_dict)
        return crm_customer_name_list, crm_final_list

    @api.model
    def top_10_crm_filter(self, **kwargs):
        data_list = []
        data_lead_amount = []
        data_lead_qty = []
        currency = [self.env.user.company_id.currency_id.symbol]

        if kwargs['0']['customer_from_date'] and kwargs['0']['customer_to_date']:
            start_date = kwargs['0']['customer_from_date']
            end_date = kwargs['0']['customer_to_date']

            ### for top 10 customer  ###
            top_10_customer = {}
            read_group_res = self.read_group(
                [('create_date', '<=', end_date),
                 ('create_date', '>=', start_date)],
                ['partner_id', 'expected_revenue'], ['partner_id', 'expected_revenue'])
            for rec in read_group_res:
                if rec['partner_id'] != False:
                    partner_name = str(rec['partner_id'][1])
                    if partner_name not in top_10_customer:
                        top_10_customer[partner_name] = []
                    top_10_customer[partner_name].insert(0, rec['partner_id_count'])
                    top_10_customer[partner_name].insert(1, self.formatINR(rec['expected_revenue']))
            sorted_entities = sorted(top_10_customer.items(), key=lambda x: x[1], reverse=True)
            top_10_entities = sorted_entities[:10]
            converted_dict = {key: value for key, value in top_10_entities}
            for key in converted_dict:
                converted_dict[key] = converted_dict[key][1:]
            for rec in converted_dict:
                top_1 = {}
                top_1[rec] = converted_dict[rec]
                data_list.append(top_1)

            ### For Top 10 Team By Count ###

            sale_team_data_filter = self.read_group(
                [('create_date', '<=', end_date),
                 ('create_date', '>=', start_date)],
                ['team_id'],
                ['team_id'])

            top_10_count = {}
            for rec in sale_team_data_filter:
                if rec['team_id'] != False:
                    team_name = str(rec['team_id'][1])
                    if team_name not in top_10_count:
                        top_10_count[team_name] = 0
                    top_10_count[team_name] += rec['team_id_count']
            top_10_crm_count = dict(list(top_10_count.items())[:10])
            sorted_entities = sorted(top_10_crm_count.items(), key=lambda x: x[1], reverse=True)
            top_10_entities = sorted_entities[:10]
            converted_dict = {key: value for key, value in top_10_entities}

            for rec in converted_dict:
                top_product_qty = {}
                top_product_qty[rec] = top_10_crm_count[rec]
                data_lead_qty.append(top_product_qty)

            ### For Top 10 Team By Amount ###

            # start_date = date.today().replace(day=1)
            # end_date = date.today() + relativedelta(day=31)

            team_by_amount_filter = self.read_group(
                [('create_date', '<=', end_date),
                 ('create_date', '>=', start_date)],
                ['team_id', 'expected_revenue'],
                ['team_id', 'expected_revenue'], )
            top_10_product_qty = {}
            for rec in team_by_amount_filter:
                if rec['team_id'] != False:
                    team_name = str(rec['team_id'][1])
                    if team_name not in top_10_product_qty:
                        top_10_product_qty[team_name] = 0
                    top_10_product_qty[team_name] += rec['expected_revenue']

            top_10_crm_amount = dict(list(top_10_product_qty.items())[:10])
            sorted_entities = sorted(top_10_crm_amount.items(), key=lambda x: x[1], reverse=True)
            top_10_entities_amount = sorted_entities[:10]
            converted_dict_amount = {key: value for key, value in top_10_entities_amount}
            data_lead_amount.append(converted_dict_amount)

        return data_list, data_lead_qty, data_lead_amount, currency

    @api.model
    def top_10_sales_team(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)
        sale_team_data = self.read_group(
            [('create_date', '<=', end_date),
             ('create_date', '>=', start_date)],
            ['team_id'],
            ['team_id'], )
        top_10_sales_team = {}
        for rec in sale_team_data:
            if rec['team_id'] != False:
                team_name = str(rec['team_id'][1])
                if team_name not in top_10_sales_team:
                    top_10_sales_team[team_name] = rec['team_id_count']
                # top_10_sales_team[stage_name] += rec['team_id_count']
        sorted_entities = sorted(top_10_sales_team.items(), key=lambda x: x[1], reverse=True)
        top_10_entities = sorted_entities[:10]
        converted_dict = {key: value for key, value in top_10_entities}
        # top_10_team = dict(list(top_10_sales_team.items())[:10])
        return converted_dict

    @api.model
    def top_10_sales_team_by_amount(self):
        start_date = date.today().replace(day=1)
        end_date = date.today() + relativedelta(day=31)
        read_group_res = self.read_group(
            [('create_date', '<=', end_date),
             ('create_date', '>=', start_date)],
            ['team_id', 'expected_revenue'],
            ['team_id', 'expected_revenue'], )
        top_10_product_qty = {}
        for rec in read_group_res:
            if rec['team_id'] != False:
                team_name = str(rec['team_id'][1])
                if team_name not in top_10_product_qty:
                    top_10_product_qty[team_name] = 0
                top_10_product_qty[team_name] += rec['expected_revenue']

        sorted_entities = sorted(top_10_product_qty.items(), key=lambda x: x[1], reverse=True)
        top_10_entities = sorted_entities[:10]
        converted_dict = {key: value for key, value in top_10_entities}
        currency = [self.env.user.company_id.currency_id.symbol]
        return converted_dict,currency

    @api.model
    def crm_team_graph(self, **kwargs):
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

        crm_team_graph = self.read_group(
            [('create_date', '<=', end_date),
             ('create_date', '>=', start_date)],
            ['team_id'],
            ['team_id'], )
        team_name = []
        team_count = []
        graph_data = {}
        for rec in crm_team_graph:
            if rec['team_id'] != False:
                team_name.append(str(rec['team_id'][1]))
                team_count.append(rec['team_id_count'])
                stage_name = str(rec['team_id'][1])
                if stage_name not in graph_data:
                    graph_data[stage_name] = 0
                graph_data[stage_name] += rec['team_id_count']

        team_name_list = []
        team_data = {}
        team_count_list = []
        team_data['data'] = []
        team_data['backgroundColor'] = [
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
        team_data['label'] = 'Sales Team'
        for recs in graph_data:
            team_name_list.append(recs)
            team_data['data'].append(graph_data[recs])
        team_count_list.append(team_data)
        return team_name_list, team_count_list
