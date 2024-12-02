from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class CommissionClosePeriod(models.Model):
    _name = "commission.close.period"

    number_of_days = fields.Integer(
        string="Days After",
    )

    @api.model
    def create(self, vals):
        if self.search([]):
            raise ValidationError(_('You can setup only one close period type!'))
        return super(CommissionClosePeriod, self).create(vals)
    
    def unlink(self):
        for rec in self:
            raise ValidationError(_('You must have one close period type!'))
        return super(CommissionClosePeriod, self).unlink()