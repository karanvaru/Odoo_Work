from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UpdateTaxWizard(models.TransientModel):
    _name = "update.tax.wizard"

    picking_id = fields.Many2one('stock.picking', string='Transfer#')
    move_lines = fields.One2many('update.tax.wizard.line', 'tax_wizard_id',
                                 string='Move Lines')

    @api.model
    def default_get(self, fields):
        result = super(UpdateTaxWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        picking_obj = self.env['stock.picking']
        picking = picking_obj.browse(active_id)
        if picking:
            result['picking_id'] = picking.id
            lines_list = []
            for move in picking.move_ids_without_package:
                lines_list.append((0, 0, {
                    'product_id': move.product_id.id,
                    'product_uom': move.product_uom.id,
                    'product_price': move.product_price,
                    # 'tax_id': [(6, 0, move.tax_id.ids)],
                    'cess_non_advol': move.cess_non_advol,
                    'move_id': move.id,
                }))
            result['move_lines'] = lines_list
        return result

    def update_tax(self):
        ''' Function to update tax and Price '''
        for line in self.move_lines:
            line.move_id.write({
                'product_price': line.product_price,
                'tax_id': [(6, 0, line.tax_id.ids)],
                'cess_non_advol': line.cess_non_advol,
            })
        return True


class UpdateTaxWizardLine(models.TransientModel):
    _name = "update.tax.wizard.line"

    tax_wizard_id = fields.Many2one('update.tax.wizard', string='Wizard Id')
    move_id = fields.Many2one('stock.move', string='Move')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom = fields.Many2one('product.uom', string='Unit of Measure')
    product_price = fields.Float('Product Price', help="Product Price for Eway Bill")
    tax_id = fields.Many2many('account.tax', string='Taxes')
    cess_non_advol = fields.Selection([('0', '0'), ('400', '400'), ('2076', '2076'),
                                       ('2747', '2747'), ('3668', '3668'), ('4006', '4006'),
                                       ('4170', '4170')], string='CESS Non Advol Amount')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_price = self.product_id.standard_price
