# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class BillsApprovals(models.Model):
    _name = "bills.approvals"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Budget Approval Bills submissions'

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
    contact = fields.Many2one('res.partner', string='contact', store=True, track_visibility='onchange')
    subject = fields.Text('Subject', store=True, track_visibility='onchange')
    description = fields.Html('Description', store=True, track_visibility='onchange')
    submit_to = fields.Many2one('res.users', 'Responsible', store=True, domain="[('is_int_user','=',True)]",track_visibility='onchange')

    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('bills.approvals.sequence'),
		})
        return super(BillsApprovals, self).create(vals)

