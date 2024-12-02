# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class PosOrderBranch(models.Model):
    _inherit = 'pos.order'

    branch_id = fields.Many2one(
        'res.branch', string="Branch",readonly=True , default=lambda self: self.env.user.branch_id, store=True)    
    