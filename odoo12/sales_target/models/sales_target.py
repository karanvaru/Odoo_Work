# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SalesTarget(models.Model):
    _name = "sales.target"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sales Target'
    _order = 'id desc'

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
    sales_person = fields.Many2one('res.users',string='Sales Person')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('sales.target.sequence'),
		})
        return super(SalesTarget, self).create(vals)
