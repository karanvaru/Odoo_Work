from odoo import fields,api,models,_


class PurchaseChannel(models.Model):
    _name = 'purchase.channel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Purchase Channel"
    _order = 'sequence,id'

    name = fields.Char(string="Name",track_visibility=True)
    sequence = fields.Integer("Sequence", default=1)


    