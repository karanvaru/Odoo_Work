# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class RDPGlossory(models.Model):
    _name = "rdp.glossory"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'RDP Glossory'

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')

    s_name = fields.Char('Short Name', track_visibility='onchange')
    department = fields.Many2many('hr.department', string='Department',track_visibility='onchange')
    description = fields.Html('Description' ,track_visibility='onchange')
    type = fields.Selection([
        ('acronym', 'Acronym'),
        ('abbreviation', 'Abbreviation'),
        ('terminology', 'Terminology')
    ], string='Type', store=True,
        help="Type of Shortname.")
    notes = fields.Text('notes', store=True,track_visibility='onchange')

    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('rdp.glossory.sequence'),
		})
        return super(RDPGlossory, self).create(vals)



