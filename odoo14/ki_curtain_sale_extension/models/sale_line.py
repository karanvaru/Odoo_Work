from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    curtain_line_id = fields.Many2many('curtain.line', widget="many2many_tags", string='Curtain Line')
    sale_sub_product_id = fields.Many2one('product.product', string='Sale sub product')

    def action_sale_line_show_details(self):
        return {
            'name': _('Sale Line'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.line.wizard',
            'target': 'new',
        }


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_explode(self):
        return_super = super().action_explode()
        if not self:
            return return_super
        move = self[0]
        rec = self.env['sale.order'].search([('name', '=', move.raw_material_production_id.origin)])
        for line in rec.order_line:
            if move.raw_material_production_id.product_id == line.product_id:
                vals = move.copy_data(default={
                    'picking_id': move.picking_id.id if move.picking_id else False,
                    'product_id': line.sale_sub_product_id.id,
                    'product_uom': line.sale_sub_product_id.uom_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'quantity_done': line.product_uom_qty,
                    'state': 'draft',  # will be confirmed below
                    'name': move.name,
                })

                move.raw_material_production_id.write({'move_raw_ids': [(0, 0, vals[0])]})

        return return_super


# current_variants_to_create.append({
#                             'product_tmpl_id': tmpl_id.id,
#                             'product_template_attribute_value_ids': [(6, 0, combination.ids)],
#                             'active': tmpl_id.active,
#                         })