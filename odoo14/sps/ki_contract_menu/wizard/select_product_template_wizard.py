from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplateSelectWizard(models.TransientModel):
    _name = 'purchase.select.product.wizard'
    _description = 'Purchase Order'

    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
    )
    qty = fields.Integer(
        string='Quantity',
        required=True,
    )
    price_unit = fields.Float(
        string='Price',
    )

    def action_submit(self):
        pass
        current_id = self._context.get('active_id')
        browse_id = self.env[self._context.get('active_model')].browse(current_id)
        lis = []
        count = 0
        for pro in self.product_id.product_variant_ids:
            if not pro.purchase_id:
                if self.qty > len(self.product_id.product_variant_ids):
                    raise ValidationError(_("Enter the valid Quantity!!!"
                                            "!!!There are %s numbers of variants",
                                            str(len(self.product_id.product_variant_ids))))
                count += 1
                if count <= self.qty:
                    product = pro
                    print('product_id:', product)
                    lis.append((0, 0, {
                        'product_id': product.id,
                        # 'name': product.name,
                        # 'product_qty': self.qty,
                        'price_unit': self.price_unit,
                    }))
            else:
                raise ValidationError(_("No any Product Quantity remain"))
        browse_id.order_line = lis
        for i in browse_id.order_line:
            i.product_id.purchase_id = current_id
