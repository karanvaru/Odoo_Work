import time
from datetime import datetime,date
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _order = 'id desc'
    _description = 'Invoice '

    check_box = fields.Boolean(string="checking", compute='compute_check_status', store=True)
    audit_status = fields.Selection([
        ('draft', 'Draft'),
        ('issue', 'Issue'),
        ('rectified', 'Rectified'),
        ('audited', 'Audited'),
        ('refuse', 'Refuse')], string='Audit Status',readonly=1,  compute='action_get_status')
    check_status = fields.Boolean(string="Is Cheque Issued?")
    
    # @api.onchange('invoice_line_ids','reference')
    # def update_changed_values(self):
    #     invoices = self.env['journal.audit'].search([('journal_entry_id.name','=',self.number)])
    #     print('==========Dayan=============invoice====================',invoices)
    #     for rec in invoices:
    #         rec.write({'reference': self.reference})
            # self.reference = rec.reference
            
    @api.depends('payment_term_id')
    def compute_check_status(self):
        for rec in self:
            if rec.payment_term_id:
                payment_type = rec.payment_term_id.name
                if 'PDC' in payment_type:
                    rec.check_box = True
                if 'pdc' in payment_type:
                    rec.check_box = True
                if 'Pdc' in payment_type:
                    rec.check_box = True



    @api.multi
    def action_get_status(self):
        audit = self.env['journal.audit'].search([('journal_entry_id.id','=',self.move_id.id)])
        for rec in audit:
            self.audit_status = rec.state

    @api.multi    
    def get_reference_document_to_audit(self):
        for org in self:
    # Source Document for PO and SO Invoices.
            invoice =  self.env['journal.audit'].search([('journal_entry_id.name','=',org.number)])
            print('==========Dayan=============invoice====================',invoice)
            if invoice:
                inv_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="account.invoice">%s</a>') % (org.id,org.number)
                invoice.message_post(body = inv_message)        

     # Source Document for Purchase Order
            purchase = self.env['purchase.order'].search([('name','=',org.origin)])
            print('============Dayan===========purchase====================',purchase)
            if purchase:
                for po in purchase:
                    po_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="purchase.order">%s</a>') % (po.id, po.name)
                    invoice.message_post(body = po_message)
            
    # Source Document for Sale Order
            sale = self.env['sale.order'].search([('name','=',org.origin)])
            print('===========Dayan============sale=====================',sale)
            if sale:
                for so in sale:
                    so_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="sale.order">%s</a>') % (so.id, so.name)
                    invoice.message_post(body = so_message)

    # Update Values to Journal Entries and Journal Audit
            move = self.env['account.move'].search([('name','=',self.number)])
            invoices = self.env['journal.audit'].search([('journal_entry_id.name','=',self.number)])
            if move:
                for jr in move:
                    jr.update({'ref': org.reference
                            #    'line_ids':[(6,0,{'account_id':line.account_id.id,
                            #                     'partner_id':line.partner_id.id,
                            #                     'name':line.name,
                            #                     'tax_ids':[(6,0,[tax.id for tax in line.invoice_line_tax_ids])],
                            #                     }) for line in org.invoice_line_ids]
                    })
            if invoices:
                for rec in invoices:
                    rec.update({'reference': org.reference
                                # "journal_line_ids": [(6,0,org.invoice_line_ids)]
                                # "journal_line_ids": org.invoice_line_ids
                    })
    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate(),to_open_invoices.get_reference_document_to_audit()
