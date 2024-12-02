from odoo import fields,api,models,_


class PartnerType(models.Model):
    _name = 'partner.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Partner Type"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)


    