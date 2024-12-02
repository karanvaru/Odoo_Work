from odoo import api,fields,models,_



class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_service_ids = fields.Many2many(
        'partner.service', 
        string='Partner Services',
        track_visibility='always',
        copy=False
    )

    partner_type_ids = fields.Many2one(
        'partner.type',
        string='Partner Type',
        track_visibility='always',
        copy=False
    )