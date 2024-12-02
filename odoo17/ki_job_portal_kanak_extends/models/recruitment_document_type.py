from odoo import api, fields, models


class RecruitmentDocumentType(models.Model):
    _name = "recruitment.document.type"

    name = fields.Char(
        string="Name",
        required=True
    )
    is_default = fields.Boolean(
        string="Default",
    )
    is_required = fields.Boolean(
        string="Required",
    )
