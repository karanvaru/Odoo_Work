from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date
import datetime


class InsurancePolicyInherit(models.Model):
    _inherit = "insurance.policy"

    def formatINR(self, number):
        s, *d = str(number).partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        amt = "".join([r])
        return amt

    @api.model
    def get_all_policy_type_count(self):
        policy_types = self.search([])
        vehicle_total_counts = 0
        health_total_counts = 0
        corporate_total_counts = 0

        vehicle_len_counts = 0
        health_len_counts = 0
        corporate_len_counts = 0

        vehicle_counts = policy_types.search([
            ('policy_type', '=', 'vehicle'),
        ])
        health_counts = policy_types.search([
            ('policy_type', '=', 'health'),
        ])
        corporate_counts = policy_types.search([
            ('policy_type', '=', 'corporate'),
        ])

        for rec in vehicle_counts:
            vehicle_total_counts += rec.net_amount
            vehicle_len_counts += 1
        for rec in health_counts:
            health_total_counts += rec.net_amount
            health_len_counts += 1
        for rec in corporate_counts:
            corporate_total_counts += rec.net_amount
            corporate_len_counts += 1

        data_dct = {
            'vehicle_total_counts': self.formatINR(vehicle_total_counts),
            'health_total_counts': self.formatINR(health_total_counts),
            'corporate_total_counts': self.formatINR(corporate_total_counts),
            'vehicle_len_counts': vehicle_len_counts,
            'health_len_counts': health_len_counts,
            'corporate_len_counts': corporate_len_counts,
            'currency': self.env.user.company_id.currency_id.symbol,

        }
        return data_dct

    @api.model
    def get_all_agent(self):
        agent_list = []
        read_agent = self.read_group(
            [], ['agent_id', 'net_amount'],
            ['agent_id', 'net_amount'], )
        for rec in read_agent:
            agent_dct = {}
            if rec['agent_id'] != False:
                agent_dct['agent_id'] = str(rec['agent_id'][0])
                agent_dct['agent'] = str(rec['agent_id'][1])
                agent_dct['count'] = rec['agent_id_count']
                agent_dct['amount'] = self.formatINR(rec['net_amount'] or 0)
                agent_list.append(agent_dct)
        return agent_list

    @api.model
    def get_policy_category(self):
        category_list = []
        policy_category = self.read_group([], ['policy_category_id', 'net_amount'],
                                          ['policy_category_id', 'net_amount'])
        for policy in policy_category:
            category_dct = {}
            if policy['policy_category_id'] != False:
                category_dct['category_id'] = str(policy['policy_category_id'][0])
                category_dct['category'] = str(policy['policy_category_id'][1])
                category_dct['count'] = policy['policy_category_id_count']
                category_dct['amount'] = self.formatINR(policy['net_amount']) or 0
                category_list.append(category_dct)
        return category_list

    @api.model
    def get_policy_invoice_status(self):
        invoice_types = self.search([])
        invoice_total_counts = 0
        to_invoice_total_counts = 0

        invoice_len_counts = 0
        to_invoice_len_counts = 0

        invoiced_counts = invoice_types.search([
            ('invoice_status', '=', 'invoiced'),
        ])
        to_invoice_counts = invoice_types.search([
            ('invoice_status', '=', 'to_invoice'),
        ])

        for rec in invoiced_counts:
            invoice_total_counts += rec.net_amount
            invoice_len_counts += 1
        for rec in to_invoice_counts:
            to_invoice_total_counts += rec.net_amount
            to_invoice_len_counts += 1

        invoice_status_data_dct = {
            'invoice_total_counts': self.formatINR(invoice_total_counts),
            'to_invoice_total_counts': self.formatINR(to_invoice_total_counts),
            'to_invoice_len_counts': to_invoice_len_counts,
            'invoice_len_counts': invoice_len_counts,
            'currency': self.env.user.company_id.currency_id.symbol,

        }
        return invoice_status_data_dct

    @api.model
    def get_policy_by_company(self):
        company_list = []
        read_insurance_company = self.read_group(
            [], ['insurance_company_id', 'net_amount'],
            ['insurance_company_id', 'net_amount'], )
        for rec in read_insurance_company:
            company_dct = {}
            if rec['insurance_company_id'] != False:
                company_dct['insurance_company_id'] = str(rec['insurance_company_id'][0])
                company_dct['company'] = str(rec['insurance_company_id'][1])
                company_dct['count'] = rec['insurance_company_id_count']
                company_dct['amount'] = self.formatINR(rec['net_amount'] or 0)
                company_list.append(company_dct)
        return company_list

    @api.model
    def get_policy_expire_30_days(self):
        insurance_list = []
        start_date = date.today()
        end_date = date.today() + relativedelta(days=30)
        insurance = self.search([('end_date', '>=', start_date), ('end_date', '<=', end_date)])
        for rec in insurance:
            insurance_list.append(
                {'id': rec.id, 'name': rec.partner_id.name, 'date': rec.end_date.strftime("%d/%m/%Y"),
                 'net_amount': self.formatINR(rec.net_amount)})
        return insurance_list
