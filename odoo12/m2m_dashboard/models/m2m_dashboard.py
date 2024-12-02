# -*- coding: utf-8 -*-
import time
from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class MondayToMondayDashboard(models.Model):
    _name = "m2m.dashboard"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = 'Monday 2 Monday Dashboard'
    

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
    drishyam_date = fields.Date(string='Drishyam Date')
    drishyam_1 = fields.Integer(string='Drishyam 1 (L1)')
    drishyam_2 = fields.Integer(string='Drishyam 2 (CR)')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('m2m.dashboard.sequence'),
		})
        return super(MondayToMondayDashboard, self).create(vals)
