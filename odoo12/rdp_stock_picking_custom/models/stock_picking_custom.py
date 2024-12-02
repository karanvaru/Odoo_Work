# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _



class StockPickingCustom(models.Model):
    _inherit = "stock.picking"

    def action_to_set_to_draft(self):
        self.state="draft"













