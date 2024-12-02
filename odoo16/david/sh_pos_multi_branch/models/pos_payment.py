# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api

class PosPaymentBranch(models.Model):
    _inherit = 'pos.payment'

    branch_id = fields.Many2one(
        'res.branch', string="Branch",readonly=True ,related='pos_order_id.branch_id', store=True)     

    @api.model
    def create(self, vals):
        res = super(PosPaymentBranch, self).create(vals)
        if res and res.pos_order_id and res.pos_order_id.branch_id:
            res.write({
                'branch_id': res.pos_order_id.branch_id.id,
            })
        return res
