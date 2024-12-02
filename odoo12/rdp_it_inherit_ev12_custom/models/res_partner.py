from odoo import api,fields,models,_



class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_service_ids = fields.Many2many(
        'partner.service', 
        string='Partner Services',
        track_visibility='onchange',
        copy=False
    )

    partner_industry_ids = fields.Many2one(
        'partner.industry',
        string='Partner Industry',
        track_visibility='onchange',
        copy=False
    )
    