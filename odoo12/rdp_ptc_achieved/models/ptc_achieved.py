from odoo import models, fields, api, _
from datetime import date, datetime, timedelta


class PTCAchieved(models.Model):
    _name = 'ptc.achieved'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "PTC Achieved"

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Partner Name', track_visibility='onchange')
    kam_id = fields.Many2one('res.users', string='KAM', track_visibility='onchange')
    ptc_signed_date = fields.Date(string='PTC Signed Date', track_visibility='always')
    ptc_signed_value = fields.Float(string='PTC Signed Value', track_visibility='always')
    open_days = fields.Char('Open Days', compute="compute_open_days")
    total_revenue_achieved_in_fy = fields.Float('Total Revenue Achieved In This FY', track_visibility='always')
    total_ptc_achieved_percentage = fields.Float(string='Total PTC Achieved Percentage',
                                                 compute='_compute_percentage', track_visibility='always')
    tag_ids = fields.Many2many('ptc.tags', string='Tags', track_visibility='onchange')
    closed_date = fields.Datetime(string="Closed Date")
    description = fields.Html(string='Description', track_visibility='always')


    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('ptc.achieved.sequence'),
        })
        return super(PTCAchieved, self).create(vals)

    @api.depends('ptc_signed_value', 'total_revenue_achieved_in_fy')
    def _compute_percentage(self):
        for record in self:
            try:
                record.total_ptc_achieved_percentage = (record.total_revenue_achieved_in_fy / record.ptc_signed_value) 
            except:
                record.total_ptc_achieved_percentage = 0

    @api.multi
    def compute_open_days(self):
        for record in self:
            if record['closed_date']:
                record['open_days'] = str((record['closed_date'] - record['create_date']).days) + " Days"
            else:
                record['open_days'] = str((datetime.today() - record['create_date']).days) + " Days"


class PTCResPartner(models.Model):
    _inherit = 'res.partner'


    ptc_res_partner_id = fields.Many2one('ptc.achieved', 'PTC ID')


class PTCTags(models.Model):
    _name = "ptc.tags"
    _description = "PTC Tags"

    name = fields.Char('Name')
