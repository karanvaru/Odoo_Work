from odoo import models, fields, api
from odoo.exceptions import AccessError

class WorkFlows(models.Model):
    _name = 'work.flows'
    _description = "RDP Workflows Name Model"

    name = fields.Char(string='Name', required= True)

class RdpWorkflows(models.Model):
    _name = 'rdp.workflows'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "RDP Workflows"

    name = fields.Char(string='Name',track_visibility='onchange')
    active = fields.Boolean(string='Active', default=True)
    workflow_id = fields.Many2one('work.flows','Workflows Name' ,track_visibility='onchange',required=True)
    created_by = fields.Char(string='Created By',readonly= 1, default=lambda self: self.env.user.name,track_visibility='onchange')
    description = fields.Text(string='Description',track_visibility='onchange')
    workflow_video = fields.Char(string='Workflow Video Link',track_visibility='onchange')
    workflow_doc = fields.Char(string='Workflow Doc Link',track_visibility='onchange')
    workflow_slide = fields.Char(string='Workflow Slide Link',track_visibility='onchange')
    workflow_sheet = fields.Char(string='Workflow Sheet Link',track_visibility='onchange')
    internal_notes = fields.Html(string='Internal Notes', track_visibility='onchange')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')], string='Status',readonly=1, default='active', track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('rdp.workflows.sequence')
        res = super(RdpWorkflows, self).create(vals) 
        return res

   