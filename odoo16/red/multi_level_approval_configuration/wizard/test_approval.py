# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import fields, models, _


class TestApproval(models.TransientModel):
    _name = 'test.approval'
    _description = 'Test Approval'

    name = fields.Char()
    state = fields.Selection([
        ("draft", "Draft"),
        ("to_approve", "To Approved"),
        ("to_approve_2", "To Approved 2"),
        ("approve", "Approved"),
        ("refuse", "Refused")
    ])

    def btn_approve(self):
        self.filtered(lambda r: r.state == "to_approve").state = "approve"

    def btn_refuse(self):
        self.filtered(lambda r: r.state == "to_approve").state = "refuse"
