# -*- coding: utf-8 -*-

from odoo import api, fields, models

class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    @api.onchange("company_duplicate_id")
    def _onchange_company_duplicate_id(self):
        """
        Onchange method for company_duplicate_id
        """
        for conf in self:
            company_id = conf.company_duplicate_id
            conf.duplicate_fields_partner = company_id.duplicate_fields_partner
            conf.duplicate_fields_partner_soft = company_id.duplicate_fields_partner_soft
            conf.duplicate_fields_lead = company_id.duplicate_fields_lead
            conf.duplicate_fields_lead_soft = company_id.duplicate_fields_lead_soft
            conf.search_duplicates_for_companies_only = company_id.search_duplicates_for_companies_only

    company_duplicate_id = fields.Many2one(
        'res.company',
        string='Company Duplicates',
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    duplicate_fields_partner = fields.Many2many(
        'ir.model.fields',
        'res_partner_rigid_id',
        'ir_model_fileds_rigid_id',
        'ir_model_fileds_res_partner_rigid_rel_table',
        string='Partner Rigid Duplicates Fields',
        domain=[
            ('model', '=', 'res.partner'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search partner duplicates. \
            Odoo would not allow to save a duplicate in comparison to the soft fields.',
    )
    duplicate_fields_partner_soft = fields.Many2many(
        'ir.model.fields',
        'res_partner_soft_id',
        'ir_model_fileds_soft_id',
        'ir_model_fileds_res_partner_soft_rel_table',
        string='Partner Soft Duplicates Fields',
        domain=[
            ('model', '=', 'res.partner'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search partner duplicates. \
            Odoo would show such duplicates on a special button, but would allow to save such object!',
    )
    search_duplicates_for_companies_only = fields.Boolean(
        string="Only companies and stand-alone individuals",
        help="""
            If checked duplicates would be searched only for and among partners without parent.
            In such a way all contacts would be excluded.
        """,
    )
    duplicate_fields_lead = fields.Many2many(
        'ir.model.fields',
        'crm_lead_rigid_id',
        'ir_model_fileds_rigid_id',
        'ir_model_fileds_crm_lead_rigid_rel_table',
        string='Leads Rigid Duplicates Fields',
        domain=[
            ('model', '=', 'crm.lead'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search leads duplicates. \
            Odoo would not allow to save a duplicate in comparison to the soft fields.',
    )
    duplicate_fields_lead_soft = fields.Many2many(
        'ir.model.fields',
        'crm_lead_soft_id',
        'ir_model_fileds_soft_id',
        'ir_model_fileds_crm_lead_soft_rel_table',
        string='Leads Soft Duplicates Fields',
        domain=[
            ('model', '=', 'crm.lead'),
            ('store', '=', True),
            ('ttype', 'not in', ['one2many', 'many2many', 'binary', 'reference', 'serialized']),
        ],
        help='Select criteria, how to search leads duplicates. \
            Odoo would show duplicates on the special button, but it would allow to save a duplicate',
    )

    @api.model
    def set_values(self):
        """
        Overwrite to add new system params
        """
        super(res_config_settings, self).set_values()
        company_id = self.company_duplicate_id.sudo()
        company_id.write({
            "duplicate_fields_partner": [(6, 0, self.duplicate_fields_partner.ids)],
            "duplicate_fields_partner_soft": [(6, 0, self.duplicate_fields_partner_soft.ids)],
            "duplicate_fields_lead": [(6, 0, self.duplicate_fields_lead.ids)],
            "duplicate_fields_lead_soft": [(6, 0, self.duplicate_fields_lead_soft.ids)],
            "search_duplicates_for_companies_only": self.search_duplicates_for_companies_only,
        })
