# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import api, SUPERUSER_ID, _ 
from . import models


def uninstall_hook(cr, registry):
    ''' Need to reenable the `product` pricelist multi-company rule that were
        disabled to be 'overridden' for multi-website purpose
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})

    product_rule = env.ref('product.product_comp_rule',
                           raise_if_not_found=False)
    pricelist_rule = env.ref(
        'product.product_pricelist_comp_rule', raise_if_not_found=False)
    pricelist_item_rule = env.ref(
        'product.product_pricelist_item_comp_rule', raise_if_not_found=False)
    product_supplier_rule = env.ref(
        'product.product_supplierinfo_comp_rule', raise_if_not_found=False)

    multi_company_rules = product_rule or env['ir.rule']
    multi_company_rules += pricelist_rule or env['ir.rule']
    multi_company_rules += pricelist_item_rule or env['ir.rule']
    multi_company_rules += product_supplier_rule or env['ir.rule']

    multi_company_rules.write({'active': True})