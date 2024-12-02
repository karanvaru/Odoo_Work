from odoo import api, fields, models


class ApplicationDocument(models.Model):
    _name = "application.document"

    document_type_id = fields.Many2one(
        'recruitment.document.type',
        string="Document Type",
        tracking=True
    )
    document = fields.Binary(
        'Document'
    )
    document_name = fields.Char(
        string='Name'
    )
    hr_applicant_id = fields.Many2one(
        'hr.applicant',
        string="Applicant",
    )