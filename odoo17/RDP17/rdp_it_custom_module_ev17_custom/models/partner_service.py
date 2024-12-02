from odoo import fields,models,api,_


class PartnerServices(models.Model):
    _name = 'partner.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Partner Services"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)
    partner_type_ids = fields.Many2many('partner.type', string='Partner Type',track_visibility='always')
