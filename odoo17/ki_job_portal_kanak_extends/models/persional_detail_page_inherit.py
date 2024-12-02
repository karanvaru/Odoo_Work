from odoo import api, fields, models


class PersonalDetails(models.Model):
    _inherit = 'personal.detail'
    _description = 'Applicant Educational Information'

    marks = fields.Char("Marks Obtained")