# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    model_name = fields.Char(
        # related="task_id.model_name",
        store=True,
        string="Model Name"
    )
    serial_number = fields.Char(
        # related="task_id.serial_number",
        store=True,
        string='Serial Number'
    )
    hours = fields.Float(
        # related="task_id.hours",
        store=True,
        string="Hours"
    )
    odometer = fields.Char(
        string="Odometer"
    )

    @api.model
    def create(self, vals):
        result = super(AccountMove, self).create(vals)
        if 'task_id' in vals:
            result.update({
                'model_name': result.task_id.model_name,
                'serial_number': result.task_id.serial_number,
                'hours': result.task_id.hours,
                'odometer': result.task_id.odometer,
            })
        return result


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
