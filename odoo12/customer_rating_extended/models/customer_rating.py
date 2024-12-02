from odoo import api, fields, models
import datetime
from datetime import datetime

class CustomerRatingExtended(models.Model):
    _inherit = "rating.rating"

    submitted_date = fields.Datetime(string="Submitted On",compute="_compute_submitted_on",store="True")

    # @api.multi
    # def _compute_created_on_date(self):
    #     for rec in self:
    #         if rec.rating_text == 'satisfied':
    #             rec.submitted_on = datetime.today()
    #         elif rec.rating_text == 'not_satisfied':
    #             rec.submitted_on = datetime.today()
    #         elif rec.rating_text == 'highy_dissatisfied':
    #             rec.submitted_on = datetime.today()
    #         else:
    #             rec.submitted_on = None
    # @api.multi
    # def _compute_created_on_date(self):
    #     for rec in self:
    #         if rec.rating_text == 'no_rating':
    #             rec.submitted_on = None
    #         else:
    #             rec.submitted_on = fields.Datetime.now()

    @api.depends('create_date','write_date')
    def _compute_submitted_on(self):
        for rec in self:
            if rec.create_date == rec.write_date:
                rec.submitted_date = ''   
            else:
                 rec.submitted_date = rec.write_date

    # @api.onchange('rating_text')
    # def onchange_rating_text(self):
    #      for rec in self:
    #         if rec.create_date == rec.write_date:
    #             rec.submitted_on = ''   
    #         else:
    #              rec.submitted_on = rec.write_date
