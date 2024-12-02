# -*- coding: utf-8 -*-

from odoo import fields, models


class res_company(models.Model):
    _inherit = 'res.company'

    duplicate_fields_partner = fields.Many2many(
        'ir.model.fields', 'rel_table1', 'rel1x', 'rel1y',
        string='Partner Rigid Duplicates Fields',
        domain=[
            ('model', '=', 'res.partner'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search partner duplicates. Odoo would not allow to save a duplicate!',
    )
    duplicate_fields_partner_soft = fields.Many2many(
        'ir.model.fields', 'rel_table4', 'rel4x', 'rel4y',
        string='Partner Soft Duplicates Fields',
        domain=[
            ('model', '=', 'res.partner'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search partner duplicates. \
            Odoo would show such duplicates on a special button, but would allow to save such object!',
    )
    duplicate_fields_lead = fields.Many2many(
        'ir.model.fields', 'rel_table2', 'rel2x', 'rel2y',
        string='Leads Rigid Duplicates Fields',
        domain=[
            ('model', '=', 'crm.lead'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search leads duplicates. \
            Odoo would not allow to save a duplicate in comparison to the previous field',
    )
    duplicate_fields_lead_soft = fields.Many2many(
        'ir.model.fields', 'rel_table3', 'rel3x', 'rel3y',
        string='Leads Soft Duplicates Fields',
        domain=[
            ('model', '=', 'crm.lead'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search leads duplicates. \
            Odoo would show duplicates on a button, but it would allow to save a duplicate',
    )
    search_duplicates_for_companies_only = fields.Boolean(
        string="Only companies and stand-alone individuals",
        help="""
            If checked duplicates would be searched only for and among partners without parent.
            In such a way all contacts would be excluded.
        """
    )
