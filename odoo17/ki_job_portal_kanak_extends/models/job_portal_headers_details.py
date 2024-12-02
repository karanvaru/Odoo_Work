from odoo import api, fields, models


class JobPortalHeadersDetails(models.Model):
    _name = "job.portal.headers.details"

    section_type = fields.Selection([
        ('applicant', 'Applicant Information'),
        ('applicant_address', 'Applicant Address'),
        ('academics', 'Academics'),
        ('certifications', 'Certifications'),
        ('work_history', 'Work History'),
        ('applicant_summary', 'Applicant Summary'),
        ('trade_assesment_questionare', 'Trades Assessment Questionnaire'),
        ('documents', 'Documents'),
    ],
        string='Section',
        required=True
    )
    header = fields.Html(
        "Header"
    )
