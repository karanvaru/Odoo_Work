# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import api, SUPERUSER_ID, _
from . import models


def uninstall_hook(cr, registry):
    ''' Need to reenable the `product` pricelist multi-company rule that were
        disabled to be 'overridden' for multi-website purpose
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})

    account_move_rule = env.ref(
        'account.account_move_comp_rule', raise_if_not_found=False)
    account_move_line_rule = env.ref(
        'account.account_move_line_comp_rule', raise_if_not_found=False)
    payment_rule = env.ref(
        'account.account_payment_comp_rule', raise_if_not_found=False)

    tax_comp_rule = env.ref(
        'account.tax_comp_rule', raise_if_not_found=False)
    
    journal_comp_rule = env.ref(
        'account.journal_comp_rule', raise_if_not_found=False)
    
    account_payment_term_comp_rule = env.ref(
        'account.account_payment_term_comp_rule', raise_if_not_found=False)
    
    account_fiscal_position_comp_rule = env.ref(
        'account.account_fiscal_position_comp_rule', raise_if_not_found=False)

    multi_company_rules = account_move_rule or env['ir.rule']
    multi_company_rules += account_move_line_rule or env['ir.rule']
    multi_company_rules += payment_rule or env['ir.rule']
    multi_company_rules += tax_comp_rule or env['ir.rule']
    multi_company_rules += journal_comp_rule or env['ir.rule']
    multi_company_rules += account_payment_term_comp_rule or env['ir.rule']
    multi_company_rules += account_fiscal_position_comp_rule or env['ir.rule']

    multi_company_rules.write({'active': True})
