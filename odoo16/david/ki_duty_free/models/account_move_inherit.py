# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    departure_date = fields.Date(
        string="Departure Date",
    )

    ship_flight = fields.Char(
        string="Ship/Flight",
        copy=False,
    )

    ed_no = fields.Char(
        string="E.D No",
        copy=False,
    )

    is_duty_free_confirm = fields.Boolean(
        string="Is Duty Free Confirm",
        copy=False,
    )

    # third_schedule = fields.Date(
    #     string="Third Schedule",
    # )

    staying_at = fields.Char(
        string="Staying at",
        copy=False,
    )



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    item_code = fields.Char(
        string="Item Code",
    )

    @api.onchange('product_id')
    def onchange_item_code(self):
        if self.product_id:
            if self.product_id.default_code:
                self.item_code = self.product_id.default_code
            if self.product_id.name:
                self.name = self.product_id.name
        else:
            self.item_code = ''
            self.name = ''

