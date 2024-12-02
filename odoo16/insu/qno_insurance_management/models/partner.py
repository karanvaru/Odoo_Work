# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError



class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_type = fields.Selection(
        selection=[
            ('agent', 'Agent'),
            ('customer', 'Customer'),
            ('insurance_company', 'Insurance Company'),
            ('insurance_company_agent', 'Insurance Company Agent'),
        ],
        copy=True,
        string="Partner Type",
    )
    relative_ids = fields.One2many(
        string="Relatives",
        comodel_name="partner.relative",
        inverse_name="partner_id",
    )

    agent_counts = fields.Integer(
        compute='compute_count',
        string="Agent Policy Count"
    )
    customers_counts = fields.Integer(
        compute='compute_count',
        string="Customer Policy Count"
    )
    agency_counts = fields.Integer(
        compute='compute_count',
        string="Agency Policy Count"
    )

    partner_relation_id = fields.Many2one(
        "partner.relative.relation",
        string="Relation",
    )
    date_of_birth = fields.Date(
        string="Date Of Birth"
    )
    age = fields.Float(
        string="Age"
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')

    def compute_count(self):
        InsurancePolicyObj = self.env['insurance.policy']
        for record in self:
            record.update({
                'agent_counts': InsurancePolicyObj.search_count([
                    ('agent_id', '=', record.id)
                ]),
                'customers_counts': InsurancePolicyObj.search_count([
                    ('partner_id', '=', record.id)
                ]),
                'agency_counts': InsurancePolicyObj.search_count([
                    ('insurance_company_id', '=', record.id)
                ])
            })

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res.update({
            'type': 'contact'
        })
        return res

    @api.onchange('date_of_birth')
    def onchange_date_of_birth(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0


    @api.constrains('date_of_birth')
    def _check_commission_rate(self):
        today = date.today()
        if self.date_of_birth:
            if self.date_of_birth > today:
                raise ValidationError(
                    _('Please Add Valida Date Of Birth')
                )


    def action_view_agent_commissions(self):
        return

    def action_view_agent_policies(self):
        act = self.env.ref(
            'qno_insurance_management.action_view_insurance_policy'
        ).sudo().read([])[0]
        act['domain'] = [('agent_id', '=', self.id)]
        return act

    def action_view_customer_policies(self):
        act = self.env.ref(
            'qno_insurance_management.action_view_insurance_policy'
        ).sudo().read([])[0]
        act['domain'] = [('partner_id', '=', self.id)]
        return act

    def action_view_agency_policies(self):
        act = self.env.ref(
            'qno_insurance_management.action_view_insurance_policy'
        ).sudo().read([])[0]
        act['domain'] = [('insurance_company_id', '=', self.id)]
        return act
