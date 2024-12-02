from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrderWizard(models.TransientModel):
    _name = 'create.purchase.order.wizard'
    _description = 'Purchase Order'

    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
    )

    def action_create(self):
        vals = {
            'partner_id': self.partner_id.id,
        }
        res = self.env['purchase.order'].create(vals)
        for purchase in self._context.get('active_ids'):
            print('purchase', purchase)
            value = {
                'product_id': purchase,
                'order_id': res.id,
            }
            self.env['purchase.order.line'].create(value)
        print('rrrrrrrrrrrrrr', res)
        current_id = self._context.get('active_id')
        # current_ids = self._context.get('active_ids')
        # print('cccccccccccc', current_ids)
        browse_id = self.env[self._context.get('active_model')].browse(current_id)
        browse_id.purchase_id = res.id

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'target': 'current',
            'res_id': res.id,
            'flags': {
                'form': {
                    'action_buttons': True,
                    'options': {
                        'mode': 'edit'
                    }
                }
            }
        }
