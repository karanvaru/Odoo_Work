from odoo import models, fields, api
from datetime import datetime, date


class PurchaseQuatation(models.Model):

    _inherit = 'purchase.order'

    open_days = fields.Char(compute='_compute_open_days', string='Open Days')
    date = fields.Date(string='Date', default=fields.Date.today)

    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'purchase':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "  days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days


class IncomingProducts(models.Model):

    _inherit = 'stock.move'

    open_days = fields.Char(compute='_compute_open_days', string='Open Days')
    date = fields.Date(string='Date', default=fields.Date.today)


    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'done':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "  days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days


class PurchaseRequest(models.Model):

    _inherit = 'purchase.request'

    open_days = fields.Char(compute='_compute_open_days', string='Open Days')
    date = fields.Date(string='Date', default=fields.Date.today)


    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'done' or rec.state == 'approved' or rec.state == 'rejected':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "  days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days



class PurchaseRequestLine(models.Model):

    _inherit = 'purchase.request.line'

    open_days = fields.Char(compute='_compute_open_days', string='Open Days')
    date = fields.Date(string='Date', default=fields.Date.today)


    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.request_state == 'done' or rec.request_state == 'approved' or rec.request_state == 'rejected':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "  days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days


class PurchaseTender(models.Model):

    _inherit = 'purchase.requisition'

    open_days = fields.Char(compute='_compute_open_days', string='Open Days')
    date = fields.Date(string='Date', default=fields.Date.today)


    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'done' or rec.state == 'cancel':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "  days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days
