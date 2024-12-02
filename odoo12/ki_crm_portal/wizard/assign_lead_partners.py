# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Assign_partner(models.TransientModel):
    _name = "crm.assign.partner"
    _description = "Assign CRM Partners"

    @api.model
    def default_get(self, fields):
        defaults = super(Assign_partner, self).default_get(fields)
        defaults['lead_id'] = self.env.context.get('active_id')
        return defaults

    lead_id = fields.Many2one(
        'crm.lead',
        required=True,
        readonly=True
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string="Partners",
        required=True
    )

    def action_assign(self):
        context = self._context
        active_ids = context.get('active_ids')
        active_model = context.get('active_model')
        if active_ids and active_model == 'crm.lead':
            lead_ids = self.env[active_model].browse(active_ids).filtered(lambda l: l.is_master_opportunity)
            lead_ids.assign_new_partner(self.partner_ids)
        else:
            self.lead_id.assign_new_partner(self.partner_ids)
