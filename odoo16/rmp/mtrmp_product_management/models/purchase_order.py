from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for po in self.order_line:
            if po:
                po.product_id.last_purchase_line_id = po.id
                po.product_id.product_tmpl_id.last_purchase_line_id = po.id
        return res

