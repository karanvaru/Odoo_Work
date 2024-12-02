from odoo import models, fields, api


class RDPSignatures(models.Model):
    _inherit = 'sign.request'

    signer = fields.Char(string='Signer',compute='_compute_singer')
    signer_company_2 = fields.Char(string='Signer Company', compute='_compute_singer')
    signer_company = fields.Char(compute='_compute_singer')
    signer_company1 = fields.Char(compute='_compute_singer')

    @api.depends('request_item_ids')
    def _compute_singer(self):
        for rec in self:
            for record in rec.request_item_ids:
                if record:
                    rec.signer = record.partner_id.name
                    rec.signer_company_2 = record.partner_id.parent_id.name
                    rec.signer_company = record.partner_id.company_name
                    rec.signer_company1 = record.partner_id.company_id.name
