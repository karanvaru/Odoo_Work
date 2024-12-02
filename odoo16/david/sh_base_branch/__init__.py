# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import api, SUPERUSER_ID, _
from . import models


def uninstall_hook(cr, registry):
    ''' Need to reenable the `product` pricelist multi-company rule that were
        disabled to be 'overridden' for multi-website purpose
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})
    partner_rule = env.ref('base.res_partner_rule', raise_if_not_found=False)

    multi_company_rules = partner_rule or env['ir.rule']

    multi_company_rules.write({'active': True})
