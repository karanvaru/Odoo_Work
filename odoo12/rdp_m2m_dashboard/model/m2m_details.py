from odoo import models, fields, api,_
from datetime import date, timedelta


class M2MDashboard(models.Model):
    _name = 'm2m.details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference No', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    m2m_date = fields.Date(string='M2M Date',default=date.today())
    bcd = fields.Date(string='BCD', compute='_compute_total')
    m1 = fields.Char(string='M.1', track_visibility='always')
    m2 = fields.Char(string='M.2', track_visibility='always')
    m3 = fields.Char(string='M.3', track_visibility='always')
    mwh = fields.Char(string='M.WH', track_visibility='always')
    m5 = fields.Char(string='M5', track_visibility='always')
    start_date = fields.Selection(
        [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),('Sunday', 'Sunday')],)
    duration = fields.Char(string='Next',compute='_compute_total_rent')


    @api.depends('m2m_date', 'bcd')
    def _compute_total(self):
        for record in self:
            record.bcd = record.m2m_date + timedelta(days=7)

    # @api.depends('start_date', 'duration')
    # def _compute_total_rent(self):
    #     for record in self:
    #         record.duration = record.start_date + timedelta(days=7)
    #
    #
    #

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('m2m.details.sequence'),
        })

        return super(M2MDashboard, self).create(vals)

    @api.depends('start_date', 'duration')
    def _compute_total_rent(self):
        for record in self:
            record.duration = record.start_date
