from odoo import api, fields, models, _
from datetime import date, datetime
import time

class SalesOpenDays(models.Model):
    _inherit = "rma.issue"

    open_days = fields.Char(string='Open Days', compute="cal_sales_open_days")

    @api.model
    def cal_sales_open_days(self):
        for rec in self:
            if rec.done_date:
                rec.open_days = str((rec.done_date - rec.create_date).days) + " Days"
            elif rec.cancel_date:
                rec.open_days = str((rec.cancel_date - rec.create_date).days) + " Days"
            elif rec.reject_date:
                rec.open_days = str((rec.reject_date - rec.create_date).days) + " Days"
            else:
                rec.open_days = str((datetime.today() - rec.create_date).days) + "Days"


