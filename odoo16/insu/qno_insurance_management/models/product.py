# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_policy_product = fields.Boolean(
        copy=True,
        string="Is Policy Product?",
    )
    insurance_company_id = fields.Many2one(
        'res.partner',
        string='Insurance Company',
    )
    product_counts = fields.Integer(
        compute='compute_count',
        string="Number of Costing"
    )

    def compute_count(self):
        for record in self:
            record.product_counts = self.env['insurance.policy'].search_count(
                [('policy_product_id', '=', self.product_variant_id.id)])


# class ProductProduct(models.Model):
#     _inherit = "product.product"
# 
#     is_policy_product = fields.Boolean(
#         copy=True,
#         string="Is Policy Product?",
#     )
#     insurance_company_id = fields.Many2one(
#         'res.partner',
#         string='Insurance Agency',
#     )

    def action_view_agent_policies(self):
        act = self.env.ref('qno_insurance_management.action_view_insurance_policy').sudo().read([])[0]
        act['domain'] = [('policy_product_id', '=', self.product_variant_id.id)]
        return act

class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        res = []
        for line in self:
            name = line.name
            if line.insurance_company_id:
                name = "[ " + line.insurance_company_id.name + '] ' + name
            res.append((line.id, name))
        return res

