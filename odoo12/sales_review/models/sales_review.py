# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SalesReview(models.Model):
    _name = "sales.review"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sales Review'

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
    review_date = fields.Date('Review Date', store=True, track_visibility='onchange')
    review_by = fields.Many2one('res.users', string='Review By',store=True, track_visibility='onchange')
    review_to = fields.Many2one('res.users', string='Review By', store=True, track_visibility='onchange')
    currency = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    mtd = fields.Monetary('MTD',currency_field="currency")
    ytd = fields.Monetary('YTD',currency_field="currency")
    today_revenue_c = fields.Monetary('Today Revenue', store=True, track_visibility='onchange',currency_field="currency")
    today_revenue_d = fields.Monetary('Today Revenue', store=True, track_visibility='onchange',currency_field="currency")
    new_partner_add = fields.Char('New Partner Additions', store=True, track_visibility='onchange')
    meeting_schedule_with= fields.Many2many('res.partner', string='Meeting Scheduled With', track_visibility='onchange')
    manager_review_inputs = fields.Html('Manager Reviewer Inputs for Performance Improvement', strore=True, track_visibility='onchange')


    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('sale.review.sequence'),
		})
        return super(SalesReview, self).create(vals)