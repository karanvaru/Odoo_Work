# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import Warning,UserError
from odoo import models, fields, api, _


class stock_invoice_onshipping(models.TransientModel):
    _name = "stock.invoice.onshipping"

    def _get_journal(self):
        res_ids = self._context.get('active_ids', [])
        pick_obj = self.env['stock.picking']
        pickings = pick_obj.browse(res_ids)

        journal_obj = self.env['account.journal']
        journal_type = self._get_journal_type()

        journals = journal_obj.search([('type', '=', journal_type), ('company_id', 'in', pickings.mapped('company_id').ids)])
        return journals and journals[0] or False

    def _get_journal_type(self):
        res_ids = self._context.get('active_ids', [])
        pick_obj = self.env['stock.picking']
        pickings = pick_obj.browse(res_ids)
        pick = pickings and pickings[0]
        if not pick or not pick.move_ids:
            return 'sale'
        type = pick.picking_type_id.code
        if type == 'incoming':
            journal_type = 'purchase'
        else:
            journal_type = 'sale'
        return journal_type

    journal_id = fields.Many2one('account.journal', 'Destination Journal', required=True, default=_get_journal)
    journal_type = fields.Selection([('purchase_refund', 'Refund Purchase'), ('purchase', 'Create Supplier Invoice'),
                                     ('sale_refund', 'Refund Sale'), ('sale', 'Create Customer Invoice')],
                                    'Journal Type', readonly=True, default=_get_journal_type)
    group = fields.Boolean("Group by partner")
    invoice_date = fields.Date('Invoice Date')

    def open_invoice(self):
        invoice_ids = self.create_invoice()
        if not invoice_ids:
            raise UserError(_('No invoice created or invoice is  alrady created !'))
        action = {}
        if self.journal_type == 'sale':
            inv_type = 'out_invoice'
        else:
            inv_type = 'in_invoice'
        data_obj = self.env['ir.model.data']
        if inv_type == "out_invoice":
            action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        elif inv_type == "in_invoice":
            action = self.env.ref('account.action_move_in_invoice_type').sudo().read()[0]
        if action:
            action['domain'] = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"

            return action
        return True

    def create_invoice(self):
        picking_obj = self.env['stock.picking'].browse(self._context.get('active_ids'))
        pick = picking_obj and picking_obj[0]
        type = pick.picking_type_id.code
        if type == 'incoming':
            inv_type = 'in_invoice'
        else:
            inv_type = 'out_invoice'
        res = picking_obj.with_context(date_inv=self.invoice_date, inv_type=inv_type).action_invoice_create(
            journal_id=self.journal_id.id,
            group=self.group,
            move_type=inv_type,
        )

        return res
