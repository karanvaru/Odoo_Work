from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _prepare_invoice(self):
        print('hello*********')
        vals = super(SaleOrder, self)._prepare_invoice()
        if self.warehouse_id:
            vals['warehouse_id'] = self.warehouse_id.id
        print(vals)
        return vals




