# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    modify_taxes_line = fields.Boolean(string="Modify Taxes Of Lines")
    taxes_ids = fields.Many2many('account.tax', string="List Taxes", required=1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: