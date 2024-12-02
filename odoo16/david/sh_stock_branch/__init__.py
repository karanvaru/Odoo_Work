# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import api, SUPERUSER_ID, _
from . import models


def uninstall_hook(cr, registry):
    ''' Need to reenable the `product` pricelist multi-company rule that were
        disabled to be 'overridden' for multi-website purpose
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})

    warehouse_rule = env.ref(
        'stock.stock_warehouse_comp_rule', raise_if_not_found=False)
    picking_rule = env.ref('stock.stock_picking_rule',
                           raise_if_not_found=False)
    location_rule = env.ref(
        'stock.stock_location_comp_rule', raise_if_not_found=False)
    quant_rule = env.ref('stock.stock_quant_rule', raise_if_not_found=False)
    scrap_rule = env.ref('stock.stock_scrap_company_rule',
                         raise_if_not_found=False)
    stock_move_rule = env.ref('stock.stock_move_rule',
                              raise_if_not_found=False)
    stock_move_line_rule = env.ref(
        'stock.stock_move_line_rule', raise_if_not_found=False)

    multi_company_rules = warehouse_rule or env['ir.rule']
    multi_company_rules += picking_rule or env['ir.rule']
    multi_company_rules += location_rule or env['ir.rule']
    multi_company_rules += quant_rule or env['ir.rule']
    multi_company_rules += scrap_rule or env['ir.rule']
    multi_company_rules += stock_move_rule or env['ir.rule']
    multi_company_rules += stock_move_line_rule or env['ir.rule']

    multi_company_rules.write({'active': True})
