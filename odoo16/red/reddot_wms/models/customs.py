from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class CustomsRestrictions(models.Model):
    _name = "customs.restrictions"
    _description = "Customs Restrictions"

    release_ref = fields.Char('Release Reference')
    agency = fields.Char('Agency')


class DutyExemptions(models.Model):
    _name = "duty.exceptions"
    _description = "Customs Restrictions"

    beneficiary = fields.Char('Beneficiary')
    sources = fields.Char('Sources')
    code = fields.Char('Code')
