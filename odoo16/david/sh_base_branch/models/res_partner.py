# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _

class CustomerBranch(models.Model):
    _inherit = 'res.partner'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    @api.onchange('branch_id', 'parent_id')
    def _onchange_branch_id(self):

        if self._origin.child_ids:

            for child in self._origin.child_ids:
                child.branch_id = self.branch_id.id

        if self.parent_id:
            self.branch_id = self.parent_id.branch_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('parent_id'):
                Parent = self.env['res.partner'].search(
                    [('id', '=', vals.get('parent_id'))], limit=1).branch_id.id
                vals['branch_id'] = Parent
        return super(CustomerBranch, self).create(vals_list)
