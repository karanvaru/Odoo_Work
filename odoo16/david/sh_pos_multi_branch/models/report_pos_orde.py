# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class PosOrderReportBranch(models.Model):
    _inherit = "report.pos.order"
    
    branch_id = fields.Many2one(
        'res.branch', string="Branch")
    
    def _select(self):
        return super(PosOrderReportBranch, self)._select() + ',pt.branch_id AS branch_id'
    
    def _group_by(self):
        return super(PosOrderReportBranch, self)._group_by() + ',pt.branch_id'
            