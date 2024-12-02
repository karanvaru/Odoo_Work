from unicodedata import name
from odoo import api, fields, models, _
from datetime import date, datetime
import time


class FmAdminCredentials(models.Model):
    _name = "admin.credentials"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "FM Admin Credentials"

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), track_visibility='always')
    subject = fields.Char(string="Subject", track_visibility='always')
    source_url = fields.Char(string="Source URL", track_visibility='always')
    registered_email = fields.Char(string="Registered Email", track_visibility='always')
    registered_mobile = fields.Char(string="Registered Mobile", track_visibility='always')
    department = fields.Many2one('hr.department', string='Department', track_visibility='onchange')
    owner = fields.Many2one('hr.employee', string='Owner', track_visibility='onchange', compute='compute_owner', readonly=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('credentials', 'Credentials'),
        ('live', 'Live'),
        ('cancel', 'Cancel'),
        ('close', 'Close'),
    ], string='Status', default='draft', track_visibility='always')
    notes = fields.Html(string="Notes")
    credentials_ids = fields.One2many('user.credentials', 'user_id', string="Credentials Ids", track_visibility='Onchange')
    closed_date = fields.Datetime.today()
    @api.model
    def create(self, vals):

        vals.update({
            'name': self.env['ir.sequence'].next_by_code('admin.credentials.sequence'),
        })
        return super(FmAdminCredentials, self).create(vals)

    @api.multi
    def action_to_credentials(self):
        self.state = 'credentials'

    @api.multi
    def action_to_live(self):
        self.state = 'live'

    @api.multi
    def action_to_closed(self):
        self.state = 'close'

    @api.multi
    def action_to_cancelled(self):
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    def compute_owner(self):
        for rec in self:
            manager = rec.env['hr.employee'].search([('manager', '=', True)])
            manager_list = []
            for man in manager:
                manager_list.append(man.id)
            rec.owner = manager_list


class UserCredentials(models.Model):
    _name = "user.credentials"
    _description = "User Credentials"

    user_id = fields.Many2one('admin.credentials', string='Owner')
    user_name = fields.Char('Username', track_visibility='onchange')
    password = fields.Char('Password', track_visibility='onchange')




