# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class PosSessionBranch(models.Model):
    _inherit = 'pos.session'

    branch_id = fields.Many2many(
        'res.branch', string="Branch",readonly=True, store=True, default=lambda self: self.env.user.allowed_branch_ids)
    
    def _loader_params_res_users(self):
        result = super()._loader_params_res_users()
        if result:
            if result.get('search_params') and result.get('search_params').get('fields'):
                result.get('search_params').get('fields').append('branch_id')
        return result

    def _get_pos_ui_res_users(self, params):
        user = self.env['res.users'].search_read(**params['search_params'])[0]
        user['role'] = 'manager' if any(id == self.config_id.group_pos_manager_id.id for id in user['groups_id']) else 'cashier'
        return user
