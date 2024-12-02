# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import api, fields, models


class StockWarehouseBranch(models.Model):
    _inherit = 'stock.warehouse'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)


class StockPickingBranch(models.Model):
    _inherit = 'stock.picking'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)


class StockLocationBranch(models.Model):
    _inherit = 'stock.location'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id and self.location_id.branch_id:
            self.branch_id = self.location_id.branch_id.id


class StockScrapBranch(models.Model):
    _inherit = 'stock.scrap'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)
