# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

#     def _action_done(self):
#         res = super(StockPicking, self)._action_done()
#         if not self:
#             return res
#         for record in self:
#             picking = self.search([('origin', '=', record.origin)])
#             picking_type = self.env['stock.picking.type'].sudo().search([
#                 ('name', '=', 'Returns'),
#                 ('company_id', '=', self.env.company.id)
#             ], limit=1)
#             if all(rec.state == 'done' and rec.picking_type_id != picking_type for rec in picking):
#                 wizard_obj = self.env["stock.invoice.onshipping"].with_context(
#                     active_ids=record.id,
#                     active_model=record._name,
#                 ).sudo().create({})
#                 invoice_ids = wizard_obj.create_invoice()
#                 invoices = self.env['account.move'].browse(invoice_ids)
#                 invoices.write({
#                     'branch_id': record.branch_id.id
#                 })
#                 invoices.action_post()
#                 # self.create_invoice()
#             elif all(rec.state == 'done' and rec.picking_type_id == picking_type for rec in picking):
#                 record.create_credit_note()
#         return res




    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        if not self:
            return res
        for record in self:
            if record.sale_id.sales_shop_id.is_create_invoice:
                if record.state == 'done':
                    if record.picking_type_id.code == 'outgoing':
                        wizard_obj = self.env["stock.invoice.onshipping"].with_context(
                            active_ids=record.id,
                            active_model=record._name,
                        ).sudo().create({})
                        invoice_ids = wizard_obj.create_invoice()
                        invoices = self.env['account.move'].browse(invoice_ids)
                        invoices.write({
                            'branch_id': record.branch_id.id
                        })
                        invoices.action_post()
                    elif record.picking_type_id.code == 'incoming':
                        record.create_credit_note()
    #             picking = self.search([('origin', '=', record.origin)])
    #             picking_type = self.env['stock.picking.type'].sudo().search([
    #                 ('name', '=', 'Returns'),
    #                 ('company_id', '=', self.env.company.id)
    #             ], limit=1)
    #             if all(rec.state == 'done' and rec.picking_type_id != picking_type for rec in picking):
    #                 wizard_obj = self.env["stock.invoice.onshipping"].with_context(
    #                     active_ids=record.id,
    #                     active_model=record._name,
    #                 ).sudo().create({})
    #                 invoice_ids = wizard_obj.create_invoice()
    #                 invoices = self.env['account.move'].browse(invoice_ids)
    #                 invoices.write({
    #                     'branch_id': record.branch_id.id
    #                 })
    #                 invoices.action_post()
    #                 # self.create_invoice()
    #             elif all(rec.state == 'done' and rec.picking_type_id == picking_type for rec in picking):
    #                 record.create_credit_note()
        return res

    def create_credit_note(self):
        moves = self.sale_id.invoice_ids
        if not moves:
            raise ValidationError(_('Please create customer invoice first then allow to create credit note!'))

        move = self.sale_id.invoice_ids[0]

        move_reversal = self.env['account.move.reversal'].with_context(
            active_model="account.move",
            active_ids=move.ids
        ).create({
            'date': fields.date.today(),
            'refund_method': 'refund',
            'journal_id': move.journal_id.id,
        })
        move_reversal.reverse_moves()
        if move_reversal.new_move_ids:
            move_reversal.new_move_ids.action_post()

    def create_invoice(self):
        picking_obj = self
        pick = picking_obj and picking_obj[0]
        type = pick.picking_type_id.code
        journal = self.env['account.journal'].sudo().search([
            ('name', '=', 'Customer Invoices'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if type == 'incoming':
            inv_type = 'in_invoice'
        else:
            inv_type = 'out_invoice'
        res = picking_obj.action_invoice_create(
            journal_id=journal.id,
            # group=self.group,
            move_type=inv_type,
        )
        return res
