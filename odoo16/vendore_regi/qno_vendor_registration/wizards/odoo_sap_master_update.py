# -*- coding: utf-8 -*-

from odoo import fields, models


class OdooSapMasterUpdate(models.TransientModel):
    _name = 'odoo.sap.master.update'
    _description = 'Odoo SAP Master Update'

    type = fields.Selection([
        ('getBPGroup', 'BPGroup'),
        ('getBPSalesPerson', 'BPSalesPerson'),
        ('getBPPaymentTerms', 'PaymentTerms')
    ],
        string="Type",
        required=True
    )

    def action_update_sap(self):
        pass
