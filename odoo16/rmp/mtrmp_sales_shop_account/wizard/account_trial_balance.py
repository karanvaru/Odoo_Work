# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    group_summary = fields.Boolean(
        string="Show Group Summary?"
    )
    
    
    def pre_print_report(self, data):
        return_data = super(AccountBalanceReport, self).pre_print_report(data)
        return_data['form']['used_context'].update({
            'group_summary': self.group_summary
        })
        return return_data
