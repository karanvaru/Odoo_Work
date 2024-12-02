# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.multi
    def _rma_repair_count(self):
        """
            Count RMA
        """
        for rec in self:
            rec.issue_count = len(rec.rma_issue_ids) if rec.rma_issue_ids else 0

    @api.multi
    def _get_invoice_ids(self):
        """
            Count RMA invoices
        """
        for record in self:
            rma_ids = self.env['rma.issue'].search([('ticket_id', '=', record.id)])
            invoices = []
            invoice_ids = []
            for rma in rma_ids:
                invoices += rma.associated_so.invoice_ids.filtered(lambda r: r.type == 'out_refund')

            for invoice in invoices:
                invoice_ids.append(invoice.id)
            record.invoice_ids = invoice_ids or []
            record.invoice_count = len(record.invoice_ids)

    issue_count = fields.Integer(compute="_rma_repair_count", string='RMA')
    rma_issue_ids = fields.One2many('rma.issue', 'ticket_id', string="RMA Issue")
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    repair_id = fields.Many2one('repair.order', string="Repair Order")
    invoice_ids = fields.Many2many('account.invoice', compute="_get_invoice_ids", string='Invoices')
    invoice_count = fields.Integer(compute="_get_invoice_ids", string='# Invoice')

    @api.multi
    def action_get_rma_issue(self):
        """
            Show RMA
        """
        self.ensure_one()
        context = dict(self.env.context)
        context.update({
                'default_ticket_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_priority': self.priority,
                'default_subject': self.name,
                'default_issue_date': fields.Datetime.now()
            })
        tree_view = self.env.ref('sync_rma.view_rma_tree_view')
        form_view = self.env.ref('sync_rma.ram_issue_view_form')
        result = {
            'name': 'Issue',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'rma.issue',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', self.rma_issue_ids.ids)],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }
        return result

    @api.multi
    def action_view_credit_memo(self):
        """
            Show credit memo
        """
        self.ensure_one()
        if self.invoice_ids:
            invoices = self.invoice_ids
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
                action['res_id'] = invoices.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action
