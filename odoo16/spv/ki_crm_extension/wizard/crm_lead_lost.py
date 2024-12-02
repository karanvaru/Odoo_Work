# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    def _get_sale_domain(self):
        active_id = self._context.get('active_id', False)
        return [('opportunity_id', '=', active_id), ('state', 'in', ['draft', 'sent'])]

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        domain=_get_sale_domain,
    )

    def action_lost_reason_apply(self):
        res = super(CrmLeadLost, self).action_lost_reason_apply()
        active_id = self._context.get('active_id', False)
        order_ids = self.env['sale.order'].search([
            ('opportunity_id', '=', active_id),
            ('state', 'in', ['draft', 'sent'])
        ])
        if order_ids and not self.sale_order_id:
            raise ValidationError(
                _('Please select order to be cancelled!')
            )
        if self.sale_order_id:
            self.sale_order_id.action_cancel()
        return res
