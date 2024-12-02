# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_product_ids = fields.One2many(
        'crm.product.line',
        'crm_lead_id',
        string="Product Line",
    )
