from odoo import models, fields, api
from datetime import datetime,date

class InventoryExternal(models.Model):

    _inherit = 'stock.picking'

    # date = fields.Date(string='Date', default=fields.Date.today)
    open_days = fields.Char(string='Open Days')

    # @api.depends('create_date')
    # def _compute_open_days(self):
    #     for rec in self:
    #         if rec.create_date:
    #             if not rec.state == 'done':
    #                 print("The create_date date is", rec.create_date)
    #                 print("The date of today", datetime.today())
    #                 today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
    #                 date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
    #                 rec.open_days = str((date - rec.create_date).days + 1) + "  days"
    #         else:
    #             rec.open_days = (datetime.today() - rec.create_date).days

class InventoryBachPicking(models.Model):

    _inherit = 'stock.picking.batch'

    date = fields.Date(string='Date', default=fields.Date.today)
    open_days = fields.Char(compute='_compute_open_days',string='Open Days')

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

class InventoryStockCycleCount(models.Model):

    _inherit = 'stock.cycle.count'

    date = fields.Date(string='Date', default=fields.Date.today)
    open_days = fields.Char(compute='_compute_open_days',string='Open Days')

    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'done':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days

class InventoryAdjustment(models.Model):

    _inherit = 'stock.inventory'

    date = fields.Date(string='Date', default=fields.Date.today)
    open_days = fields.Char(compute='_compute_open_days',string='Open Days')

    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'done':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days



class InventoryScrap(models.Model):

    _inherit = 'stock.scrap'

    date = fields.Date(string='Date', default=fields.Date.today)
    open_days = fields.Char(compute='_compute_open_days',string='Open Days')

    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'done':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days


class InventoryLanded(models.Model):

    _inherit = 'stock.landed.cost'

    date = fields.Date(string='Date', default=fields.Date.today)
    open_days = fields.Char(compute='_compute_open_days',string='Open Days')

    @api.depends('create_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.create_date:
                if not rec.state == 'done':
                    print("The create_date date is", rec.create_date)
                    print("The date of today", datetime.today())
                    today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
                    date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
                    rec.open_days = str((date - rec.create_date).days + 1) + "days"
            else:
                rec.open_days = (datetime.today() - rec.create_date).days

