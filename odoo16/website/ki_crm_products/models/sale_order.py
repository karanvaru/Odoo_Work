# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields_list):
        super_res = super(SaleOrder, self).default_get(fields_list)
        if 'opportunity_id' in super_res:
            lead_id = super_res['opportunity_id']
            crm_id = self.env['crm.lead'].browse(lead_id)
            data_list = []
            for res in crm_id.crm_product_ids:
                id = Command.create({
                        'product_id': res.product_id.id,
                        'product_uom_qty': res.quantity,
                        'product_uom': res.uom_id.id,
                        'price_unit': res.price_unit,
                        'price_subtotal':res.sub_total,
                        'name':res.product_id.display_name
                    })
                data_list.append(id)
            super_res.update({
                'order_line': data_list,
            })
        return super_res
