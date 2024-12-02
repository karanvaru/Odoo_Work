# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    record_type_id = fields.Many2one(
        'record.type',
        string="Record Type",
        track_visibility="onchange",
        copy=False,
        required=True
    )

    record_category_id = fields.Many2one(
        'record.category',
        string="Record Category",
        track_visibility="onchange",
        copy=False,
        required=True
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
        if self._context.get('from_uo', False):
            return res

        if 'record_type_id' in vals or 'record_category_id' in vals:
            for rec in self:
                if rec.stock_move_id:
                    rec.stock_move_id.with_context(stock_move=True).write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                expense_sheet = self.env['hr.expense.sheet'].sudo().search([('account_move_id', '=', rec.id)])
                if expense_sheet:
                    expense_sheet.with_context(expense_move=True).write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                    for ex in expense_sheet.expense_line_ids:
                        ex.with_context(from_es=True).update({
                            'record_type_id': self.record_type_id,
                            'record_category_id': self.record_category_id,
                        })
                for recs in rec.line_ids:
                    recs.invoice_id.with_context(invoice_move=True).write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })
                sale = self.env['sale.order'].sudo().search([('name','=',rec.custom_source_document)])
                if sale:
                    sale.write({
                        'record_type_id': rec.record_type_id.id,
                        'record_category_id': rec.record_category_id.id
                    })

                purchase = self.env['purchase.order'].sudo().search([('name', '=', rec.custom_source_document)])
                if purchase:
                    purchase.write({
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

        return res

