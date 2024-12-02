from odoo import api, models, fields, _


class JobRequests(models.Model):
    _name = "job.requests"

    name = fields.Char(
        'Name',
        readonly=True
    )
    date_of_birth = fields.Date(
        'Date of Birth',
        readonly=True
    )
    phone = fields.Char(
        'Phone',
        readonly=True
    )
    email = fields.Char(
        'Email',
        readonly=True
    )
    specialization = fields.Char(
        'Specialization',
        readonly=True
    )
    description = fields.Text(
        'Description',
        readonly=True
    )
    resume = fields.Binary(
        'Resume',
        readonly=True
    )
    attachment_name = fields.Char(
        'Attachment Name',
    )
    academic_id = fields.Many2one(
        'recruitment.academic',
        string='Academy',
        readonly=True
    )
