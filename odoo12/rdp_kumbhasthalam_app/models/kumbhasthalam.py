from odoo import api, fields, models, _
from datetime import date, datetime



class Kumbhasthalam(models.Model):
    _name = "kumbhasthalam.app"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Kumbhasthalam App"


    name = fields.Char(string='Reference No', required=True, copy=False,track_visibility='always', readonly=True, index=True, default=lambda self : _('New'))
    text = fields.Text(string="Text")
    notes = fields.Text(string="Internal Notes")
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('kumbhasthalam.sequence')
        res = super(Kumbhasthalam, self).create(vals)
        return res