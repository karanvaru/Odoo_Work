from odoo import api, fields, models


class RecruitingAgent(models.Model):
    _name = "recruiting.agent"

    name = fields.Char(
        string="Name",
        required=True
    )