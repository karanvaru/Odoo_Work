import time
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class report_request_history(models.Model):
    _name = "report.request.history"
    _description = 'report.request.history'
    _rec_name = 'report_request_id'

    @api.multi
    @api.depends('seller_id')
    def get_company(self):
        for record in self:
            company_id = record.seller_id and record.seller_id.company_id.id or False
            if not company_id:
                company_id = self.env.user.company_id.id
            record.company_id = company_id

    report_request_id = fields.Char(size=256, string='Report Request ID')
    report_id = fields.Char(size=256, string='Report ID')
    report_type = fields.Char(size=256, string='Report Type')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    requested_date = fields.Datetime('Requested Date', default=time.strftime("%Y-%m-%d %H:%M:%S"))
    state = fields.Selection(
        [('draft', 'Draft'), ('_SUBMITTED_', 'SUBMITTED'), ('_IN_PROGRESS_', 'IN_PROGRESS'),
         ('_CANCELLED_', 'CANCELLED'), ('_DONE_', 'DONE'),
         ('_DONE_NO_DATA_', 'DONE_NO_DATA'), ('processed', 'PROCESSED'), ('imported', 'Imported'),
         ('partially_processed', 'Partially Processed'), ('closed', 'Closed')
         ],
        string='Report Status', default='draft')
    seller_id = fields.Many2one('amazon.seller.ept', string='Seller', copy=False)
    user_id = fields.Many2one('res.users', string="Requested User")
    company_id = fields.Many2one('res.company', string="Company", copy=False, compute=get_company,
                                 store=True)
    instance_id = fields.Many2one('amazon.instance.ept', string='Instance')

    @api.multi
    def _check_duration(self):
        if self.start_date and self.end_date < self.start_date:
            return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe start date must be precede its end date.',
         ['start_date', 'end_date'])
    ]
