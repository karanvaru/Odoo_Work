# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    departure_date = fields.Date(
        string="Departure Date",
        default=fields.Date.today(),
    )

    ship_flight = fields.Char(
        string="Ship/Flight",
        copy=False
    )

    ed_no = fields.Char(
        string="E.D No",
        copy=False
    )

    is_duty_free_confirm = fields.Boolean(
        string="Is Duty Free Confirm",
        copy=False
    )

    is_duty_free = fields.Boolean(
        string="Is Duty Free",
        copy=False
    )

    # third_schedule = fields.Date(
    #     string="Third Schedule",
    # )

    staying_at = fields.Char(
        string="Staying at",
        copy=False
    )

    @api.model
    def _prepare_invoice(self):
        invoice = super(SaleOrderInherit, self)._prepare_invoice()
        invoice.update({
            'departure_date': self.departure_date,
            'ship_flight': self.ship_flight,
            'ed_no': self.ed_no,
            'is_duty_free_confirm': self.is_duty_free_confirm,
            # 'third_schedule': self.third_schedule,
            'staying_at': self.staying_at,
        })
        return invoice



class Saleorderline(models.Model):
    _inherit = "sale.order.line"

    item_code = fields.Char(
        string="Item Code",
    )

    @api.onchange('product_template_id')
    def onchange_item_code(self):
        if self.product_template_id:
            if self.product_template_id.default_code:
                self.item_code = self.product_template_id.default_code
        else:
            self.item_code = ''

    @api.depends('product_id')
    def _compute_name(self):
        res = super()._compute_name()
        for rec in self:
            if rec.product_template_id.name:
                rec.name = rec.product_template_id.name
            else:
                rec.name = ''
        return res

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({
            'item_code': self.item_code
        })
        return res

