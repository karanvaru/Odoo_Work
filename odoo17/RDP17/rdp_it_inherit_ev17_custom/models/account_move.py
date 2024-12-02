# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        track_visibility="onchange",
        copy=False
    )


    @api.model
    def create(self, vals):
        id = super(AccountMove, self).create(vals)
        if id.stock_move_id:
            picking_id = id.stock_move_id.picking_id
            production_id = id.stock_move_id.production_id
            created_production_id = id.stock_move_id.created_production_id
            raw_material_production_id = id.stock_move_id.raw_material_production_id
            
            if picking_id:
                id.update({
                    'record_type_id': picking_id.record_type_id.id,
                    'record_category_id': picking_id.record_category_id.id
                })
            elif production_id:
                id.update({
                    'record_type_id': production_id.record_type_id.id,
                    'record_category_id': production_id.record_category_id.id
                })
            elif created_production_id:
                id.update({
                    'record_type_id': created_production_id.record_type_id.id,
                    'record_category_id': created_production_id.record_category_id.id
                })
            elif raw_material_production_id:
                id.update({
                    'record_type_id': raw_material_production_id.record_type_id.id,
                    'record_category_id': raw_material_production_id.record_category_id.id
                })

        return id

    def _write(self, vals):
        res = super(AccountMove, self)._write(vals)

        if self._context.get('from_po', False):
            return res

        if self._context.get('from_so', False):
            return res

        if self._context.get('from_mo', False):
            return res

        if 'record_type_id' in vals or 'record_category_id' in vals:
            for rec in self:
                purchase = rec.line_ids.purchase_line_id.order_id
                purchase.with_context(invoice_purchase=True).write({
                    'record_type_id': rec.record_type_id.id,
                    'record_category_id': rec.record_category_id.id
                })

                source_orders = self.line_ids.sale_line_ids.order_id
                source_orders.with_context(invoice_sale=True).write({
                    'record_type_id': rec.record_type_id.id,
                    'record_category_id': rec.record_category_id.id
                })
                for pick in source_orders.picking_ids:
                    pick.with_context(invoice_sale_picking=True).write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                for purc in purchase.picking_ids:
                    purc.with_context(invoice_purchase_picking=True).write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                picking = rec.stock_move_id.picking_id
                if picking:
                    picking.write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })

                    sale_id = picking.sale_id
                    if sale_id:
                        sale_id.with_context(invoice_sale=True).write({
                            'record_type_id': rec.record_type_id.id,
                            'record_category_id': rec.record_category_id.id
                        })

                    purchase_id = picking.purchase_id
                    if purchase_id:
                        purchase_id.with_context(invoice_purchase=True).write({
                            'record_type_id': rec.record_type_id.id,
                            'record_category_id': rec.record_category_id.id
                        })
                else:
                    production_id = False
                    if rec.stock_move_id.production_id:
                        production_id = rec.stock_move_id.production_id
                    elif rec.stock_move_id.created_production_id:
                        production_id = rec.stock_move_id.created_production_id
                    elif rec.stock_move_id.raw_material_production_id:
                        production_id = rec.stock_move_id.raw_material_production_id
                    if production_id:
                        production_id.with_context(from_account=True).write({
                            'record_type_id': rec.record_type_id.id,
                            'record_category_id': rec.record_category_id.id
                        })

                        # mrp = self.env['mrp.production'].sudo().search([('name', '=', picking.origin)])
                        # mrp.with_context(from_account=True).write({'record_type_id': self.record_type_id})
        return res

