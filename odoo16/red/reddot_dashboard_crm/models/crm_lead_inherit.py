from docutils.nodes import status
from odoo import models, api, fields, _
from datetime import datetime, date
import datetime
from dateutil.relativedelta import relativedelta


class CrmLead(models.Model):
    _inherit = "crm.lead"

    color_list = [
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

    @api.model
    def get_lead_count(self, *post):
        user = self.env.user
        print("________________  useeee", user)
        revenue_data = {}
        revenue_sum = 0
        my_revenue_sum = 0
        all_leads = self.search_count([])
        my_leads = self.search_count([('user_id', '=', user.id)])
        print("_______________  my lead", my_leads)
        for rec in self.search([]):
            revenue_sum += rec.expected_revenue
        for rec in self.search([('user_id', '=', user.id)]):
            my_revenue_sum += rec.expected_revenue
        revenue_data.update({
            'all_leads': all_leads,
            'my_leads': my_leads,
            'revenue_sum': revenue_sum,
            'my_revenue_sum': my_revenue_sum,
        })
        return revenue_data

    @api.model
    def click_open_all_lead(self, **kwargs):
        all_leads = self.search([])

        return {
            'type': 'ir.actions.act_window',
            'name': _("All Leads"),
            'res_model': 'crm.lead',
            'view_mode': 'tree',
            'domain': [('id', 'in', all_leads.ids)],
            'views': [(self.env.ref('crm.crm_case_tree_view_oppor').id, 'tree'),
                      (False, 'form')],
        }

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     user = self.env.user
    #     args += ['|', ('company_branch_id', '=', False),
    #              ('company_branch_id', 'in', user.allowed_branch_ids.ids)]
    #     return super(ResPartnerBank, self)._search(args, offset, limit, order, count, access_rights_uid)

    @api.model
    def click_open_my_lead(self):
        domain = []
        user = self.env.user
        if not self.env.user.has_group('base.group_system'):
            domain += [['user_id', '=', user.id]]
        my_leads = self.search(domain)
        return {
            'type': 'ir.actions.act_window',
            'name': _("My Leads"),
            'res_model': 'crm.lead',
            'view_mode': 'tree',
            'domain': [('id', 'in', my_leads.ids)],
            'views': [(self.env.ref('crm.crm_case_tree_view_oppor').id, 'tree'),
                      (False, 'form')],
        }

    # @api.model
    # def status_wise_leads(self, **kwargs):
    #     status_type_label = ['t1']
    #     status_type_value = [1, 45]
    #
    #     return {
    #         'status_type_label': status_type_label,
    #         'status_type_value': status_type_value,
    #         'backgroundColor': self.color_list,
    #     }
