# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
import datetime
from datetime import date, datetime
import time

_logger = logging.getLogger(__name__)

class PurchaseAgreementExtended(models.Model):

    _inherit = 'purchase.agreement'


    
    open_days = fields.Char(string="Open Days",compute="compute_open_days")
    closed_date = fields.Datetime('Closed Date')
    cancelled_date = fields.Datetime('Cancelled Date')
    related_id = fields.Many2one('purchase.tendor.related.category', string="Related To",track_visibility="onchnage")
    # opendays_count = fields.Integer('Open Days',compute="compute_open_days_count",store=True)
    purchase_open_days = fields.Integer(string="Open Days", compute='calculate_open_days_integer')  

    @api.depends('cancelled_date')
    def compute_open_days(self):
        for record in self:
            record.open_days = 0
            if record.closed_date:
                close_date_str = datetime.strftime(record.closed_date, '%Y-%m-%d %H:%M')
                open_date_str = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M')
                close_date = datetime.strptime(close_date_str, '%Y-%m-%d %H:%M')
                open_date = datetime.strptime(open_date_str, '%Y-%m-%d %H:%M')
                
                record.open_days =  close_date - open_date
            else:
                current_date_str = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M')
                current_date= datetime.strptime(current_date_str, '%Y-%m-%d %H:%M')
                open_date_str = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M')
                open_date = datetime.strptime(open_date_str, '%Y-%m-%d %H:%M')

                record.open_days =  current_date - open_date

            if record.cancelled_date:
                cancel_date_str = datetime.strftime(record.cancelled_date, '%Y-%m-%d %H:%M')
                open_dt_str = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M')
                cancel_date = datetime.strptime(cancel_date_str, '%Y-%m-%d %H:%M')
                open_dt = datetime.strptime(open_dt_str, '%Y-%m-%d %H:%M') 

                record.open_days =  cancel_date - open_dt  

    # @api.depends('cancelled_date','closed_date')
    # def compute_open_days_count(self):
    #     for record in self:
    #         # record.opendays_count = 0
    #         if record.closed_date:
    #             close_date_str = datetime.strftime(record.closed_date, '%Y-%m-%d %H:%M')
    #             open_date_str = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M')
    #             close_date = datetime.strptime(close_date_str, '%Y-%m-%d %H:%M')
    #             open_date = datetime.strptime(open_date_str, '%Y-%m-%d %H:%M')
                
    #             record.opendays_count =  close_date - open_date
    #         else:
    #             current_date_str = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M')
    #             current_date= datetime.strptime(current_date_str, '%Y-%m-%d %H:%M')
    #             open_date_str = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M')
    #             open_date = datetime.strptime(open_date_str, '%Y-%m-%d %H:%M')

    #             record.opendays_count =  current_date - open_date   
    @api.multi
    def calculate_open_days_integer(self):
        for rec in self:
            if rec.closed_date:
                rec.purchase_open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.purchase_open_days = (datetime.today() - rec.create_date).days 

            if rec.cancelled_date:
                rec.purchase_open_days = (rec.cancelled_date - rec.create_date).days              

class PurchaseTenderRelatedCategory(models.Model):

    _name = "purchase.tendor.related.category"
    _description = "Purchase Tender Related Category"   


    name = fields.Char('Name')  
    















