# -*- coding: utf-8 -*-


from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PartnerRelative(models.Model):
    _name = "partner.relative"
    _description = "Customer Relative"

    relation_id = fields.Many2one(
        "partner.relative.relation",
        string="Relation",
        required=True
    )
    name = fields.Char(
        string="Name",
        required=True
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        domain=["&", ("is_company", "=", False), ("type", "=", "contact")],
    )
    gender = fields.Selection(
        string="Gender",
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other")
        ],
    )
    date_of_birth = fields.Date(
        string="Date of Birth"
    )
    age = fields.Float(
        compute="_compute_age"
    )
    job = fields.Char()
    phone_number = fields.Char()
    notes = fields.Text(
        string="Notes"
    )

    @api.depends("date_of_birth")
    def _compute_age(self):
        for record in self:
            age = relativedelta(datetime.now(), record.date_of_birth)
            record.age = age.years + (age.months / 12)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.display_name
