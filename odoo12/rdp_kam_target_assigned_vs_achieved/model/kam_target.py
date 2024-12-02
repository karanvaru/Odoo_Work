from odoo import models, fields, api
from datetime import date, timedelta

class KamTarget(models.Model):
    _name = 'kam.target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    reference_no = fields.Char(string='Sequence Number',
                               readonly=True, default='New', required=True ,track_visibility='True')
    kam = fields.Many2one('res.users',string='KAM',track_visibility='True',required=True)
    kam_target_assigned = fields.Integer(string='KAM Target Assigned',track_visibility='True',required=True)
    assigned_date = fields.Date(string='Assigned Date',track_visibility='True',default=date.today())
    total_revenue_achieved_in_month = fields.Float('Total Revenue Achieved in this Month',track_visibility='True',required=True)
    total_kam_achieved_percentage = fields.Float(string='Total KAM Achieved Percentage ',compute='_compute_percentage',track_visibility='True',required=True)
    internal_notes = fields.Html(string='Internal Notes',track_visibility='True')
    @api.depends('kam_target_assigned', 'total_revenue_achieved_in_month')
    def _compute_percentage(self):
        for record in self:
            try:
                record.total_kam_achieved_percentage = (record.total_revenue_achieved_in_month / record.kam_target_assigned)
            except:
                record.total_kam_achieved_percentage = 0

    @api.model
    def create(self, vals):
        print(vals)
        print(self)
        vals['reference_no'] = self.env['ir.sequence'].next_by_code(
            'kam.target')
        res = super(KamTarget, self).create(vals)
        return res