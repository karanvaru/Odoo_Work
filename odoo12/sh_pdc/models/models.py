from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero
    
class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"
    
    pdc_id = fields.Many2one('pdc.wizard')
    
class AccountMove(models.Model):
    _inherit = "account.move"
    
    pdc_id = fields.Many2one('pdc.wizard')
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    def open_pdc_payment(self):
        [action] = self.env.ref('sh_pdc.sh_pdc_payment_menu_action').read()
        action['domain'] = [('id', 'in', self.pdc_payment_ids.ids)]
        return action
    
    
    def _compute_pdc_payment(self):
        for rec in self:
            rec.pdc_payment_count = len(self.pdc_payment_ids)

    pdc_id = fields.Many2one('pdc.wizard')
    pdc_payment_ids = fields.Many2many('pdc.wizard',compute='_compute_pdc_payment_invoice')
    pdc_payment_count = fields.Integer("Pdc payment count",compute='_compute_pdc_payment')
    total_pdc_payment = fields.Monetary("Total",compute='_compute_total_pdc')
    total_pdc_pending = fields.Monetary("Total Pending",compute='_compute_total_pdc')
    total_pdc_cancel = fields.Monetary("Total Cancel",compute='_compute_total_pdc')
    total_pdc_received = fields.Monetary("Total Received",compute='_compute_total_pdc')
    
    
    @api.depends('pdc_payment_ids.state')
    def _compute_total_pdc(self):
        for rec in self:
            rec.total_pdc_payment = 0.0
            rec.total_pdc_pending = 0.0
            rec.total_pdc_cancel = 0.0
            rec.total_pdc_received = 0.0
            if rec.pdc_payment_ids:
                for pdc_payment in rec.pdc_payment_ids:
                    if pdc_payment.state in ('done'):
                        rec.total_pdc_received += pdc_payment.payment_amount
                    elif pdc_payment.state in ('cancel'):
                        rec.total_pdc_cancel += pdc_payment.payment_amount
                    else:
                        rec.total_pdc_pending += pdc_payment.payment_amount
            rec.total_pdc_payment = rec.total_pdc_pending + rec.total_pdc_received + rec.total_pdc_cancel
    
    def _compute_pdc_payment_invoice(self):
        self.pdc_payment_ids = False
        for move in self:
            pdcs = self.env["pdc.wizard"].search([
                ('invoice_id','=',move.id)
                ])
            if pdcs:
                move.pdc_payment_ids = [(6,0,pdcs.ids)]
    
#     @api.one
#     @api.depends(
#         'state', 'currency_id', 'invoice_line_ids.price_subtotal',
#         'move_id.line_ids.amount_residual',
#         'move_id.line_ids.currency_id')
#     def _compute_residual(self):
#         residual = 0.0
#         residual_company_signed = 0.0
#         sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
#         
#         # check pdc payment
#         related_pdc_payment = self.env['pdc.wizard'].sudo().search([('invoice_id','=',self.id)])
#         if not related_pdc_payment:
#             for line in self.sudo().move_id.line_ids:
#                 if line.account_id == self.account_id:
#                     residual_company_signed += line.amount_residual
#                     if line.currency_id == self.currency_id:
#                         residual += line.amount_residual_currency if line.currency_id else line.amount_residual
#                     else:
#                         from_currency = line.currency_id or line.company_id.currency_id
#                         residual += from_currency._convert(line.amount_residual, self.currency_id, line.company_id, line.date or fields.Date.today())
#         self.residual_company_signed = abs(residual_company_signed) * sign
#         self.residual_signed = abs(residual) * sign
#         self.residual = abs(residual)
#         digits_rounding_precision = self.currency_id.rounding
#         if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
#             self.reconciled = True
#         else:
#             self.reconciled = False