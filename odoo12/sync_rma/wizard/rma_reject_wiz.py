# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class RmaRejectWiz(models.TransientModel):
    _name = "rma.reject.wiz"
    _description = 'RmaRejectWiz'

    name = fields.Text(string="Reject Note", required=True)

    def reject_rma(self):
        """
            Reject RMA and set to reject state
        """
        active_id = self.env.context.get('active_id')
        if active_id:
            active_id = self.env['rma.issue'].browse(active_id)
            active_id.rma_reject_note = self.name
            active_id.reject_rma()
