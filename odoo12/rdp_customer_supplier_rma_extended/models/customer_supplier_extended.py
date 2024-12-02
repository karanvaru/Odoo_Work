# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date

class CustomerSupplierRmaExtended(models.Model):
    _inherit = 'rma.supplier'

    closing_date = fields.Datetime(string="Closing Date", compute="_compute_closing_date")
    open_days = fields.Char(string="Open Days", compute="_compute_open_days")
    current_stage_opendays = fields.Char('Current Stage OD',compute="_compute_current_stage_opendays")

    @api.depends('__last_update')
    def _compute_closing_date(self):
        for record in self:
            if record['state'] == 'close':
                record['closing_date'] = record['__last_update']

    @api.depends('create_date')
    def _compute_open_days(self):
        for record in self:
            if record['closing_date']:
                record['open_days'] = str((record['closing_date'] - record['create_date']).days) + ' Days'
                # record['open_days'] = record['open_days'][0:-13] + ' Hours'
            else:
                record['open_days'] = str((datetime.now().replace(microsecond=0) - record['create_date']).days) + ' Days'
                # record['open_days'] = record['open_days'][0:-13] + ' Hours'

    def _compute_current_stage_opendays(self):
        for rec in self:
            rec.current_stage_opendays = 0


