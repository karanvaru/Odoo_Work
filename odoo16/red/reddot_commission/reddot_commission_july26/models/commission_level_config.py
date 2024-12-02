# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CommissionLevelConfig(models.Model):
    _name = 'commission.level.config'
    _description = "Level Config"

    level_no = fields.Integer(
        string="Level",
        readonly=True
    )
    percentage = fields.Float(
        string="Percentage(%)",
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
    )

    @api.constrains('percentage')
    def _check_percentage(self):
        for rec in self:
            if rec.percentage > 100.00 or rec.percentage < 0.0:
                raise ValidationError("greater then 0.0 and less then 100.0...")
