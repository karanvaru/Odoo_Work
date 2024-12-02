# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _rma_count(self):
        """
            Count RMA
        """
        for invoice in self:
            invoice.rma_issue_count = len(invoice.rma_issue_id) if invoice.rma_issue_id else 0

    rma_issue_count = fields.Integer(compute="_rma_count", string="RMA Issue Count", copy=False)
    rma_issue_id = fields.Many2one('rma.issue', string="RMA", copy=False, readonly=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
            Override method for apply domain
        """
        if self._context.get('sale_id', False):
            sale_id = self.env['sale.order'].browse(self._context.get('sale_id', False))
            invoice_ids = sale_id.invoice_ids.filtered(lambda r: r.type == 'out_invoice' and r.state == 'paid')
            invoice_ids = invoice_ids and invoice_ids.ids or []
            if len(invoice_ids) > 0:
                args.append(('id', 'in', invoice_ids))
            else:
                args.append(('id', 'in', []))
        if not self._context.get('sale_id') and self._context.get('partner_id'):
            args.append(('partner_id', '=', self._context['partner_id']))
            args.append(('type', '=', 'out_invoice'))
        if self._context.get('rma_issue_id', False):
            rma_issue_id = self.env['rma.issue'].browse(self._context.get('rma_issue_id'))
            issue_lines_product = rma_issue_id.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'credit' and not l.invoice_id).mapped('product_id')
            if issue_lines_product:
                args.append(('invoice_line_ids.product_id', 'in', issue_lines_product.ids))
        return super(AccountInvoice, self).name_search(name, args=args, operator=operator, limit=limit)

    def get_rma_issue(self):
        """
            Show RMA
        """
        self.ensure_one()
        action = self.env.ref('sync_rma.rma_issue').read()[0]
        if len(self.rma_issue_id) > 1:
            action['domain'] = [('id', '=', self.rma_issue_id.id)]
        elif len(self.rma_issue_id) == 1:
            action['views'] = [(self.env.ref('sync_rma.ram_issue_view_form').id, 'form')]
            action['res_id'] = self.rma_issue_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
