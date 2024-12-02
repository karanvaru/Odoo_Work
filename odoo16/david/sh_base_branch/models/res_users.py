# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResUser(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one(
        'res.branch', string="Branch")
    branch_ids = fields.Many2many(
        'res.branch', string="Allow Branches",)
    allowed_branch_ids = fields.Many2many(
        'res.branch', relation="current_users_res_branchs", string="allowed Branches")

    def write(self, vals):
        if 'branch_id' in vals or 'allowed_branch_ids' in vals:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
        user = super(ResUser, self).write(vals)
        return user

    @api.constrains('branch_id', 'branch_ids')
    def _check_branch(self):
        for user in self:
            if user.branch_ids and user.branch_id not in user.branch_ids:
                raise ValidationError(
                    _('Branch %(branch_name)s is not in the allowed branches for user %(user_name)s (%(branch_allowed)s).',
                      branch_name=user.branch_id.name,
                      user_name=user.name,
                      branch_allowed=', '.join(user.mapped('branch_ids.name')))
                )

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            self.allowed_branch_ids = self.branch_id.ids

    @api.model
    def availableBranch(self, kwargs):
        final_list = []
        branch_list = []
        if 'cids' in kwargs:
            for company in kwargs['cids']:
                domain = [('id', '=', kwargs['user_id']),
                          ('company_ids', 'in', company)]
                find_user = self.env['res.users'].sudo().search(domain)
                list_branch = []
                for branch in find_user.branch_ids:
                    if branch.company_id.id == company:
                        if branch.id not in list_branch:
                            list_branch.append(branch.id)
                        vals = {
                            'id': branch.id,
                            'name': branch.name
                        }
                        branch_list.append(vals)
                final_list.append(find_user.allowed_branch_ids.ids)
                final_list.append(branch_list)
                if find_user.allowed_branch_ids and list_branch and find_user.branch_id:
                    for allow_branch in find_user.allowed_branch_ids:
                        if allow_branch.id not in list_branch:
                            find_user.sudo().write({
                                'allowed_branch_ids': [(4, find_user.branch_id.id)]
                            })
                final_list.append({
                    'id': find_user.branch_id.id,
                    'name': find_user.branch_id.name,
                })
        return final_list

    @api.model
    def ChangeDefaultBranch(self, kwargs):
        if kwargs['user_id']:
            domain = [('id', '=', kwargs['user_id'])]
            find_user = self.env['res.users'].search(domain)
            if find_user:
                find_user.sudo().write({
                    'branch_id': kwargs['branch_id'],
                    'allowed_branch_ids': [(4, kwargs['branch_id'])]
                })
                return True
            else:
                return False

    @api.model
    def ChangeAllowedBranch(self, kwargs):
        if kwargs['user_id']:
            domain = [('id', '=', kwargs['user_id'])]
            find_user = self.env['res.users'].sudo().search(domain)
            if find_user:
                for data in find_user.allowed_branch_ids:
                    if data.id == kwargs['branch_id'] and find_user.branch_id.id != kwargs['branch_id']:
                        find_user.sudo().write({
                            'allowed_branch_ids': [(3, kwargs['branch_id'])]
                        })
                        return True
                find_user.sudo().write({
                    'allowed_branch_ids': [(4, kwargs['branch_id'])]
                })
                return True
            else:
                return False
