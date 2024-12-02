# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class RMAInvoiceRefund(models.TransientModel):
    _name = "rma.invoice.refund"
    _description = "RMA Invoice refund"

    @api.model
    def default_get(self, fields):
        """
            Override method for set default values
        """
        res = super(RMAInvoiceRefund, self).default_get(fields)
        if self.env.context.get('active_id'):
            rma_issue_id = self.env['rma.issue'].browse(self.env.context.get('active_id'))
            res['rma_issue_id'] = self.env.context.get('active_id')
            res['sale_id'] = rma_issue_id.associated_so and rma_issue_id.associated_so.id or False
            res['partner_id'] = rma_issue_id.partner_id and rma_issue_id.partner_id.id or False
        return res

    invoice_id = fields.Many2one('account.invoice', string='Invoice to be refunded', required=True)
    rma_issue_id = fields.Many2one('rma.issue', string="RMA")
    sale_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', string='Customer')

    def process_refund(self):
        """
            Create refund invoice
        """
        ctx = dict(self._context or {})
        invoice_id = False
        ctx.update({'active_model': 'account.invoice', 'active_id': self.invoice_id.id, 'active_ids': [self.invoice_id.id]})
        refund_inv = self.env['account.invoice.refund'].with_context(ctx).create({
            'filter_refund': 'refund','description': 'refund',
            })
        refund_result = refund_inv.sudo().invoice_refund()

        if refund_result and refund_result.get('domain'):
            domain = [dom[2] for dom in refund_result.get('domain') if dom[0] == 'id']
            invoice_id = domain[0][0]
        if refund_result and refund_result.get('res_id'):
            invoice_id = refund_result['res_id']
        if invoice_id:
            invoice_id = self.env['account.invoice'].browse(invoice_id)
            invoice_id.rma_issue_id = self.rma_issue_id and self.rma_issue_id.id or False
            reasons = self.rma_issue_id.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'credit' and l.to_return > 0).mapped('return_type_id').mapped('name')
            invoice_id.comment = 'Create credit note because of the : ' + ', '.join(reasons) + 'reasons of ' + invoice_id.rma_issue_id.name + ' issue.'

            for invoice_line in invoice_id.invoice_line_ids:
                if invoice_line.product_id.id not in self.rma_issue_id.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'credit').mapped('product_id').ids:
                    invoice_line.unlink()
                    continue
                flag = 0
                quantity = 0
                for issue_line in self.rma_issue_id.issue_line_ids:
                    if invoice_line.product_id == issue_line.product_id and issue_line.return_type_id.return_purpose == 'credit':
                        if flag == 0:
                            quantity = issue_line.to_return
                            flag = 1
                        else:
                            quantity += issue_line.to_return
                        issue_line.invoice_id = invoice_id.id
                invoice_line.quantity = quantity

            self.rma_issue_id.invoice_ids = [(4, invoice_id.id)]
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoice_id.id
            return action
