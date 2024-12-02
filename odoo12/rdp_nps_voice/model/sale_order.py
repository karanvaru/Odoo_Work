import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create(grouped, final)
        res = self.env['nps.voice'].search([('sale_order_id','=',self.id)])
        print("====================Salwe0000===ma===============",res)
        if res != True:
            res = res.create({
                'sale_order_id': self.id,
                'so_state': self.state,
                'inv_status': self.invoice_status,
            })
        return res
    
    @api.multi
    def write(self,vals):
        res = super().write(vals)
        res = self.env['nps.voice'].search([('sale_order_id','=',self.id)])
        if res:
            print("====================Salwe0000=====wr=============",res)
            res = res.update({
                'so_state': self.state,
                'inv_status': self.invoice_status,
            })
        return res
