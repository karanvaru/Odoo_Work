# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
#    @api.multi odoo13
    @api.depends('prepared_hours_ids.purchased_hours')
    def compute_total_purchase_hours(self):
        total_purchased_hours = 0.0
        for rec in self:
            for record in rec.prepared_hours_ids:
                    total_purchased_hours += record.purchased_hours
            rec.total_purchase_hours = total_purchased_hours
    
#    @api.multi odoo13
#     @api.depends('timesheet_custom_ids')
#     def compute_total_consumed_hours(self):
# #         anlytic_lines = self.env['account.analytic.line'].search([('account_id','=',self.id)])
#         total_purchased_hours = 0.0
#         for rec in self:
#             for line in rec.timesheet_custom_ids:
#                     total_purchased_hours += line.unit_amount
#             rec.total_consumed_hours = total_purchased_hours

    @api.depends('line_ids')
    def compute_total_consumed_hours(self):
        for rec in self:
            anlytic_lines = self.env['account.analytic.line'].search([('account_id','=',rec.id),('project_id', '!=', False)])
            total_purchased_hours = 0.0
            for line in anlytic_lines:
                total_purchased_hours += line.unit_amount
            rec.total_consumed_hours = total_purchased_hours

#    @api.multi odoo13
    @api.depends('total_purchase_hours',
                 'total_consumed_hours')
    def compute_total_remaining_hours(self):
        total_remaining_hours = 0.0
        for rec in self:
            total_remaining_hours = rec.total_purchase_hours - rec.total_consumed_hours
            rec.remaining_hours = total_remaining_hours
    
    timesheet_custom_ids = fields.One2many(
        'account.analytic.line',
        'account_id',
        string='Timesheet Custom'
    )
    prepared_hours_ids = fields.One2many(
        'prepared.purchase.hours',
        'prepared_hours_id',
        string='Prepaid Hours',
        copy=False,
    )
    total_purchase_hours = fields.Float(
        string='Total Purchase Hours',
        compute='compute_total_purchase_hours',
        store=True,
        copy=False,
    )
    total_consumed_hours = fields.Float(
        string='Total Consumed Hours',
        compute='compute_total_consumed_hours',
        store=True,
        copy=False,
    )
    remaining_hours = fields.Float(
        string='Remaining Hours',
        compute='compute_total_remaining_hours',
        store=True,
        copy=False,
    )
    
class PreparedPurchaseHhours(models.Model):
    _name = 'prepared.purchase.hours'
    _description = "Prepared Purchase Hours"
    
    prepared_hours_id = fields.Many2one(
        'account.analytic.account',
        string='Contract'
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        'Sales Order',
        required=True
    )
    date = fields.Date(
        'Date of Sales Order',
        required=True
    )
    purchased_hours = fields.Float(
        'Purchased Hours',
        required=True
    )
   
