# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class ResConfigSettingInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_allow_branch_user = fields.Many2one(
        'res.groups', related="pos_config_id.sh_allow_branch_user", string='POS - Disable Branch')
    pos_branch_id = fields.Many2many(related="pos_config_id.branch_id", string="Allow Branches", required=True, readonly=False)
