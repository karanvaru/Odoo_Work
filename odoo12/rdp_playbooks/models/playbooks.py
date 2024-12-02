from odoo import models, fields, api
from odoo.exceptions import AccessError

class PlayBooks(models.Model):
    _name = 'play.books'
    _description = "RDP Playbooks Name Model"

    name = fields.Char(string='Name', required= True)

class RdpPlaybooks(models.Model):
    _name = 'rdp.playbooks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "RDP Playbooks"

    name = fields.Char(string='Name',track_visibility='onchange')
    active = fields.Boolean(string='Active', default=True)
    playbook_id = fields.Many2one('play.books','Playbook Name' ,track_visibility='onchange',required=True)
    created_by = fields.Char(string='Created By',readonly= 1, default=lambda self: self.env.user.name,track_visibility='onchange')
    description = fields.Text(string='Description',track_visibility='onchange')
    playbook_doc = fields.Char(string='Playbook Doc Link',track_visibility='onchange')
    playbook_slide = fields.Char(string='Playbook Slide Link',track_visibility='onchange')
    playbook_sheet = fields.Char(string='Playbook Sheet Link',track_visibility='onchange')
    internal_notes = fields.Html(string='Internal Notes', track_visibility='onchange')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')], string='Status',readonly=1, default='active', track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('rdp.playbooks.sequence')
        res = super(RdpPlaybooks, self).create(vals) 
        return res

    # State Active
    def set_record_to_active(self):
        # self.date_refuse = date.today()
        self.state = 'active'

    # State Inactive
    def set_record_to_inactive(self):
        # self.date_refuse = date.today()
        self.state = 'inactive'
