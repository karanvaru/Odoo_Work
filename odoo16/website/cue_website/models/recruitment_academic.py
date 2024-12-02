from odoo import api, models, fields, _


class RecruitmentAcademic(models.Model):
    _name = "recruitment.academic"

    name = fields.Char(
        'name'
    )