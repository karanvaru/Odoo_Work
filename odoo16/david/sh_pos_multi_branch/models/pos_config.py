# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    sh_allow_branch_user = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Disable Branch')
    
    branch_id = fields.Many2many(
        'res.branch', string="Allow Branches", required=True)
    
    def _compute_access_rights(self):
        for rec in self:
            rec.sh_allow_branch_user = self.env.ref(
                'sh_base_branch.sh_multi_branch_group')
