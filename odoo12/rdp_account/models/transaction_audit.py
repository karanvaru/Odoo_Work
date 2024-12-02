from ast import Store
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
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class AccountJournalAudit(models.Model):
    _name = "journal.audit"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'
    _description = 'Accounting Transactions Audit for RDP Accounting Purpose'

    name = fields.Char('Reference',track_visibility='always',default=lambda self: _('New'))
    date = fields.Date('Bill Date')
    journal_entry_id = fields.Many2one('account.move',string='Journal Entry',track_visibility='always')
    journal_id = fields.Many2one('account.journal',string='Journal')
    currency_id = fields.Many2one('res.currency', string='Currency')
    partner_id = fields.Many2one('res.partner',string="Partner")
    reference = fields.Char('Bill Reference No', related='journal_entry_id.ref')
 
    
    origin_id = fields.Char('Source Document', compute="action_get_origin")
    # invoice_ref = fields.Char('Invoice Reference', compute="action_get_invoice")
    amount = fields.Float('Amount')
    journal_status = fields.Selection([
        ('draft', 'Unposted'),
        ('posted', 'Posted')], string='Journal Status')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issue', 'Issue'),
        ('rectified', 'Rectified'),
        ('audited', 'Audited'),
        ('refuse', 'Refuse')], string='Status',readonly=1, default='draft',track_visibility='onchange')
    
    open_days = fields.Char(string='Open Days',compute='calculate_open_day')
    create_date = fields.Date('Created On')
    date_audited  = fields.Date(string='Audited On',readonly=True)
    date_refuse  = fields.Date(string='Refused On',readonly=True)
    

    # journal_line_ids 
    journal_line_ids = fields.One2many("journal.audit.line", "journal_audit_id", string="journal Items")
    tax_invoiced_attached = fields.Boolean('Tax Invoiced Attached')
    audit_remarks = fields.Text('Audit Remarks')
    account_move_id = fields.Integer("Account Move Id")

    # reason_line_ids
    reason_line_ids = fields.One2many("audit.reason.line", "journal_audit_id", string="Reason",track_visibility='always')
   
    # Check List 
    audit_checklist_ids = fields.Many2many('audit.checklist', string='Audit CheckList',readonly= False, compute='get_visible_only_check_list', store = True)
    audit_ck_progress = fields.Float('Audit Progress', compute='audit_checklist_progress')
    audit_description = fields.Char('Description', help="Explain about not accept the Audit Checklist")
    audit_checklist_len = fields.Integer('Audit Length',compute='get_len_audit_checklist', invisible=True, Store=True)
    # user_id = fields.Many2one('res.users',"User ID", default=lambda self: self.env.user)
    user_id = fields.Char("User ID", compute ='_get_current_login_user')

    # @api.multi
    # def _get_current_user(self):
    #     self.user_id = self.env.uid

    # user_id = fields.Many2one('res.users', 'Current User', compute='_get_current_user')

    @api.one
    def _get_current_login_user(self):
        user_obj = self.env['res.users'].search([])
        for user_login in user_obj:
            current_login = self.env.user
            if user_login == current_login:
                self.user_id = current_login.id
        return

    def get_visible_only_check_list(self):
        filter_list= []
        for rec in self:
            check_list = self.env['audit.checklist'].search([])
            for check in check_list:
                if rec.journal_id in check.journal_ids:
                    for group in check.groups_ids:
                        if rec.user_id in group.users:
                            filter_list.append(check.id)
            rec.audit_checklist_ids = filter_list
   
    # cl_tax_invoice = fields.Selection([('yes', 'Yes'),('no','No')],'Tax Invoice Attached?')
    # cl_vendor_reference = fields.Selection([('yes', 'Yes'),('no','No')],'According to Tax invoice Document Invoice Number updated in "Vendor Reference" field?')
    # cl_payment_terms = fields.Selection([('yes', 'Yes'),('no','No')],'According to Document Payment terms updated in "Payment terms & Due date" field?')
    # cl_gst_tax = fields.Selection([('yes', 'Yes'),('no','No')],'The GST Tax allocation is correct?')
    # cl_tds_tcs = fields.Selection([('yes', 'Yes'),('no','No')],'Is deduct TDS/TCS, If it is service?')
    # cl_coa = fields.Selection([('yes', 'Yes'),('no','No')],'Did you take COA correctly according to the description?')
    # cl_advance_payment = fields.Selection([('yes', 'Yes'),('no','No')],'Did the Bill Reconcil, If it is advance payment?')
    # cl_inventory = fields.Selection([('yes', 'Yes'),('no','No')],'Have a Purchase Order Number, If it is Inventory?')
    # cl_einvoice = fields.Selection([('yes', 'Yes'),('no','No')],'Is the e-Invoice Created?')
    # cl_ewaybill = fields.Selection([('yes', 'Yes'),('no','No')],'Is the e-Waybill Created?')
   
    # Reason
    # reason_tax = fields.Char('Reason')
    # reason_vendor_reference = fields.Char('Reason')
    # reason_payment_terms = fields.Char('Reason')
    # reason_gst_tax = fields.Char('Reason')
    # reason_tds_tcs = fields.Char('Reason')
    # reason_coa = fields.Char('Reason')
    # reason_advance_payment = fields.Char('Reason')
    # reason_inventory = fields.Char('Reason')
    # reason_einvoice = fields.Char('Reason')
    # reason_ewaybill = fields.Char('Reason')
    
    # =============================Methods=========================================================
    
    @api.onchange('journal_line_ids','reference')
    # def update_changed_values(self):
    #     invoices = self.env['account.invoice'].search([('number','=',self.journal_entry_id.name)])
    #     print('==========Dayan=============invoice=======Onchange=============',invoices)
    #     for rec in invoices:
    #         self.write({'reference': rec.reference})
            # self.reference = rec.reference

    @api.multi
    def action_get_origin(self):
        for res in self:
            if res.reference:
                invoice_sea = self.env['account.invoice'].search([('reference','=',res.reference)])
                for rec in invoice_sea:
                    res.origin_id = rec.origin
            else:
                invoice_sea = self.env['account.payment'].search([('move_name','=',res.journal_entry_id.name)])
                for obj in invoice_sea:
                    res.origin_id = obj.name

    @api.depends('audit_checklist_ids')
    def get_len_audit_checklist(self):
        for res in self:
            self.audit_checklist_len = len(res.audit_checklist_ids)

    
    # @api.multi
    # def action_get_invoice(self):
    #     for inv in self:
    #         if inv.origin_id:
    #             inv_ref = self.env['account.move'].search([('name','=',inv.journal_entry_id.name)])
    #             for rec in inv_ref:
    #                 inv.invoice_ref = rec.number

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('journal.audit.sequence')
        res = super(AccountJournalAudit, self).create(vals) 
        return res

    @api.depends('date_refuse','date_audited')
    def calculate_open_day(self):
        for rec in self:
            if rec.date_refuse:
                rec.open_days = str((rec.date_refuse - rec.create_date).days +1) + " Days"
            if rec.date_audited:
                rec.open_days = str((rec.date_audited - rec.create_date).days +1) + " Days"
            if not rec.date_refuse and not rec.date_audited:
                rec.open_days =  str((date.today() - rec.create_date).days +1) + " Days"
    
    @api.depends('audit_checklist_ids')
    def audit_checklist_progress(self):
        for each in self:
            total_len = self.env['audit.checklist'].search_count([('journal_ids.id','=',each.journal_id.id)])
            entry_len = len(each.audit_checklist_ids)
            if total_len != 0:
                each.audit_ck_progress = (entry_len * 100) / total_len

    # State Validate
    def set_status_to_audited(self):
        if self.audit_checklist_ids:
            if not self.audit_ck_progress == 100:
                if not self.audit_description:
                    raise ValidationError("Please Enter the Description for Unfilled Audit Checklist...")
                else:
                    self.date_audited = date.today()
                    self.state = 'audited'
            else:
                self.date_audited = date.today()
                self.state = 'audited'
        else:
                self.date_audited = date.today()
                self.state = 'audited'
            
    # State Refuse
    def set_status_to_refuse(self):
        self.date_refuse = date.today()
        self.state = 'refuse'
    
    # State Draft
    def set_status_to_draft(self):
        # val = []
        for rec in self:
            for check in rec.audit_checklist_ids: 
                # ck_list = self.env['audit.checklist'].search([('id','in',rec.audit_checklist_ids.ids)])
                print('===============check================================',check)
                # if check.reset == False:
                #     self.state = 'draft'
                if check.reset == True:
                    # val.append(ck_list) 
                    # if (ck_list in val):
                    print('===============check.reset================================',check.reset)
                    # check.write ({'check':False}) 
                    rec.audit_checklist_ids = False 
                    print('===============val================================',check)
                    self.state = 'draft'
                else:
                    raise ValidationError("Kindly verify the Checklist to change the stages...")
            # print('===============ck_list================================',ck_list)
        self.state = 'draft'
    
class AccountJournalAuditLine(models.Model):
    _name = "journal.audit.line"
    _description ="Reference of the Journal Accounting line"

    journal_audit_id = fields.Many2one('journal.audit',string="Journal Audit")
    account_id = fields.Many2one('account.account',string='Account')
    partner_id = fields.Many2one('res.partner',string='Partner')
    name = fields.Char(string='Label')
    debit = fields.Monetary(default=0.0, currency_field='company_currency_id')
    credit = fields.Monetary(default=0.0, currency_field='company_currency_id')
    tax_ids = fields.Many2many('account.tax',string='Taxes Applied')
    date_maturity = fields.Date('Due Date')
    company_currency_id = fields.Many2one('res.currency', string="Company Currency")
    invoice_id = fields.Many2one('account.invoice',string='Invoice')
    statement_id = fields.Many2one('account.bank.statement',string='Statement')

class AuditReasonLine(models.Model):
    _name = "audit.reason.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'This line is to save the Description about the Issue and Rectified reason which is entered in the wizard'

    journal_audit_id = fields.Many2one('journal.audit',string="Journal Audit") 
    created_by = fields.Many2one("res.users",'Created By')
    created_on = fields.Datetime('Created On')
    action = fields.Selection([('issue', 'Issue'),('rectified', 'Rectified')], string='Action')
    description = fields.Text('Description')
    issued_by = fields.Many2one("res.users",'Issued By')

class AccountMoves(models.Model):
    _inherit = 'account.move'
    # _inherit = ['account.move','mail.thread', 'mail.activity.mixin', 'portal.mixin']
    # _description ="Inherited the post() Method to create the Audit Accounting Transaction"

    invoice_ref = fields.Char('Invoice Reference',compute='get_invoice_reference')
    audit_status = fields.Selection([
        ('draft', 'Draft'),
        ('issue', 'Issue'),
        ('rectified', 'Rectified'),
        ('audited', 'Audited'),
        ('refuse', 'Refuse')], string='Audit Status',readonly=1,  compute='action_get_status')
    
    @api.multi
    def action_get_status(self):
        audit = self.env['journal.audit'].search([('journal_entry_id.name','=',self.name)])
        for rec in audit:
            self.audit_status = rec.state
    

    def get_invoice_reference(self):
        for inv in self:
            inv_ref = self.env['account.invoice'].search([('number','=',inv.name)])
            for rec in inv_ref:
                inv.invoice_ref = rec.number
                
    
    @api.multi
    def post(self, invoice=False):
        self._post_validate()
        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in self:
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id

                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date
        self.write({'state': 'posted'})
        audit = self.env['journal.audit'].search([('journal_entry_id.name','=',self.name)])
        print('=========audit===================Entry============',audit)
        # check_audit_exist = self.env.search([('audit.journal_entry_id','=',self.name)])
        # print('=========check_audit_exist===============================',check_audit_exist)
        # record_exist = audit.journal_entry_id.name = self.name
        # print('=========record_exist====check======================',record_exist)
        # if audit:
        #     print('=========check_audit_exist====if=====update======12================',audit)
        #     res = audit.update({
        #             'reference':self.ref,
        #             'date':self.date,
        #             'partner_id':self.partner_id.id,
        #             'journal_id': self.journal_id.id,
        #             'journal_status':self.state,
        #             'amount':self.amount,
        #             'journal_line_ids':[(6,0,{'account_id':line.account_id.id,
        #                                       'partner_id':line.partner_id.id,
        #                                       'name':line.name,
        #                                       'debit':line.debit,
        #                                       'credit':line.credit,
        #                                       'tax_ids':[(6, 0, [tax.id for tax in line.tax_ids])],
        #                                       'date_maturity':line.date_maturity
        #                                       }) for line in self.line_ids]
        #             })

        # Label source Document(Bank Statement):
        for obj in self:
            for lab in obj.line_ids:
                print('===========lab===',lab.statement_id)
                if lab.statement_id:
                    # bank = self.env['account.bank.statement']
                    label = self.env['account.bank.statement'].search([('id','=',lab.statement_id.id)])
                    print('==========Dayan=============Label====================',label)
                    lab_message = _('Bank Statement: <a href="#" data-oe-id="%s" data-oe-model="account.bank.statement">%s</a>') % (label.id,label.name)
                    print('==========D=============lab_message====================',lab_message)
                    audit.message_post(body = lab_message)
                      

        if not audit:
            print('=========check_audit_exist====if=====Create=====67=================',audit)
            res = audit.create({
                        'journal_entry_id':self.id,
                        # 'journal_entry_id': self.line_ids.move_id.id,
                        'reference':self.ref,
                        'date':self.date,
                        'partner_id':self.partner_id.id,
                        'journal_id': self.journal_id.id,
                        'journal_status':self.state,
                        'amount':self.amount,
                        # 'origin':self.account_id,
                        'journal_line_ids':[(0,0,{'account_id':line.account_id.id,
                                                'partner_id':line.partner_id.id,
                                                'name':line.name,
                                                'debit':line.debit,
                                                'credit':line.credit,
                                                'tax_ids':[(6, 0, [tax.id for tax in line.tax_ids])],
                                                'date_maturity':line.date_maturity,
                                                'statement_id':line.statement_id.id,
                                                'invoice_id':line.invoice_id.id
                                                }) for line in self.line_ids]
                        })
        else:
            val=[(5,0,0)]
            for line in self.line_ids:
                val.append({
                    'account_id': line.account_id.id,
                     'partner_id': line.partner_id.id,
                     'name': line.name,
                     'debit': line.debit,
                     'credit': line.credit,
                     'tax_ids': [(6, 0, [tax.id for tax in line.tax_ids])],
                     'date_maturity': line.date_maturity,
                     'statement_id':line.statement_id.id,
                     'invoice_id':line.invoice_id.id
                })

            res = audit.update({
                        'journal_entry_id':self.id,
                        # 'journal_entry_id': self.line_ids.move_id.id,
                        'reference':self.ref,
                        'date':self.date,
                        'partner_id':self.partner_id.id,
                        'journal_id': self.journal_id.id,
                        'journal_status':self.state,
                        'amount':self.amount,
                        # 'origin':self.account_id,
                        # 'journal_line_ids':[(6,0,{'account_id':line.account_id.id,
                        #                         'partner_id':line.partner_id.id,
                        #                         'name':line.name,
                        #                         'debit':line.debit,
                        #                         'credit':line.credit,
                        #                         # 'tax_ids':[(0, 0, [tax.id for tax in line.tax_ids])],
                        #                         'date_maturity':line.date_maturity
                        #                         }) for line in self.line_ids],
                        'journal_line_ids': val
                        })
        
        return res

        # ===================Test==========================Dayan=================================15.Oct.2022====================
         # Source Document for Payment
            # if res.origin_id == True and 'SO' not in  res.origin_id or 'PO' not in  res.origin_id:
            # payment = self.env['account.payment'].search([('move_name','=',org.journal_entry_id.name)])
            # if payment:
            #     for pay in payment:
            #         pay_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="account.payment">%s</a>') % (pay.id, pay.name)
            #         org.message_post(body = pay_message)  
    
class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    @api.multi 
    def action_sheet_move_create(self):
        if any(sheet.state != 'approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.user.company_id.currency_id).rounding))
        res = expense_line_ids.action_move_create()

        if not self.accounting_date:
            self.accounting_date = self.account_move_id.date

        if self.payment_mode == 'own_account' and expense_line_ids:
            self.write({'state': 'post'})
        else:
            self.write({'state': 'done'})
        self.activity_update()

# class AccountPayment(models.Model):
#     _inherit = "account.payment"

    # @api.multi
    # def post(self):
    #     """ Create the journal items for the payment and update the payment's state to 'posted'.
    #         A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
    #         and another in the destination reconcilable account (see _compute_destination_account_id).
    #         If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
    #         If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
    #     """
    #     for rec in self:
    #         if rec.state not in ['draft', 'bounce', 'deposit', 'register']:
    #             raise UserError(_("Only a draft or Bounce payment can be posted."))

    #         if any(inv.state != 'open' for inv in rec.invoice_ids):
    #             raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

    #         # keep the name in case of a payment reset to draft
    #         if not rec.name:
    #             # Use the right sequence to set the name
    #             if rec.payment_type == 'transfer':
    #                 sequence_code = 'account.payment.transfer'
    #             else:
    #                 if rec.partner_type == 'customer':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.customer.invoice'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.customer.refund'
    #                 if rec.partner_type == 'supplier':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.supplier.refund'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.supplier.invoice'
    #             rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
    #             if not rec.name and rec.payment_type != 'transfer':
    #                 raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

    #         # Create the journal entry
    #         amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
    #         move = rec._create_payment_entry(amount)
    #         persist_move_name = move.name
    #         # In case of a transfer, the first journal entry created debited the source liquidity account and credited
    #         # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
    #         if rec.payment_type == 'transfer':
    #             transfer_credit_aml = move.line_ids.filtered(
    #                 lambda r: r.account_id == rec.company_id.transfer_account_id)
    #             transfer_debit_aml = rec._create_transfer_entry(amount)
    #             (transfer_credit_aml + transfer_debit_aml).reconcile()
    #             persist_move_name += self._get_move_name_transfer_separator() + transfer_debit_aml.move_id.name
    #         rec.write({'state': 'posted', 'move_name': move.name})
        
    #      # Source Document for Payment =================Dayan================17.Oct.2022=================
    #         payment = self.env['journal.audit'].search([('journal_entry_id.name','=',rec.move_name)])
    #         print('======================payment==========================',payment)
    #         if payment:
    #             pay_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="account.payment">%s</a>') % (rec.id, rec.name)
    #             payment.message_post(body = pay_message)  
    #     return True

         # =================================================Reference================Dayan=========08.10.2022===============
    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('journal.audit.sequence')
    #     res = super(AccountJournalAudit, self).create(vals) 
    #     for org in res:
    #         # purchase = self.env['purchase.order'].search([('name','=',org.origin_id)],limit=1)
    #         po_invoice =  self.env['account.invoice'].search([('number','=',org.journal_entry_id.name)],limit=1)
    #         # Source Document for Purchase Order 
    #         if po_invoice:
    #             for po_inv in po_invoice:
    #                 # po_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="purchase.order">%s</a>') % (po.id, po.name)
    #                 # org.message_post(body = po_message)
    #                 po_inv_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="account.invoice">%s</a>') % (po_inv.id, po_inv.name)
    #                 org.message_post(body = po_inv_message)
    #         # sale = self.env['sale.order'].search([('name','=',org.origin_id)],limit=1)
    #         so_invoice =  self.env['account.invoice'].search([('number','=',org.journal_entry_id.name)],limit=1)
    #         # Source Document for Sale Order
    #         if so_invoice:
    #             for so_inv in so_invoice:
    #                 # so_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="sale.order">%s</a>') % (so_inv.id, so_inv.name)
    #                 # org.message_post(body = so_message)
    #                 so_inv_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="account.invoice">%s</a>') % (so_inv.id, so_inv.name)
    #                 org.message_post(body = so_inv_message) 
    #         # payment = self.env['account.payment'].search([('move_name','=',org.origin_id)],limit=1)
    #         pay_invoice =  self.env['account.invoice'].search([('number','=',org.journal_entry_id.name)],limit=1)
    #         # Source Document for Payment
    #         if pay_invoice:
    #             for pay_inv in pay_invoice:
    #                 # pay_inv_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="account.payment">%s</a>') % (pay_inv.id, pay_inv.name)
    #                 # org.message_post(body = pay_inv_message)  
    #                 pay_message = _('This Accounting Transaction Audit has been created from: <a href="#" data-oe-id="%s" data-oe-model="account.payment">%s</a>') % (pay_inv.id, pay_inv.name)
    #                 org.message_post(body = pay_message)           
    #     return res
        

    # Post Function 25.10.2022============================================================
    # @api.multi
    # def post(self, invoice=False):
    #     self._post_validate()
    #     # Create the analytic lines in batch is faster as it leads to less cache invalidation.
    #     self.mapped('line_ids').create_analytic_lines()
    #     for move in self:
    #         if move.name == '/':
    #             new_name = False
    #             journal = move.journal_id

    #             if invoice and invoice.move_name and invoice.move_name != '/':
    #                 new_name = invoice.move_name
    #             else:
    #                 if journal.sequence_id:
    #                     # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
    #                     sequence = journal.sequence_id
    #                     if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
    #                         if not journal.refund_sequence_id:
    #                             raise UserError(_('Please define a sequence for the credit notes'))
    #                         sequence = journal.refund_sequence_id

    #                     new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
    #                 else:
    #                     raise UserError(_('Please define a sequence on the journal.'))

    #             if new_name:
    #                 move.name = new_name

    #         if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
    #             # For opening moves, we set the reconciliation date threshold
    #             # to the move's date if it wasn't already set (we don't want
    #             # to have to reconcile all the older payments -made before
    #             # installing Accounting- with bank statements)
    #             move.company_id.account_bank_reconciliation_start = move.date
    #     self.write({'state': 'posted'})
    #     res = self.env['journal.audit'].create({
    #                 'journal_entry_id':self.id,
    #                 # 'journal_entry_id': self.line_ids.move_id.id,
    #                 'reference':self.ref,
    #                 'date':self.date,
    #                 'partner_id':self.partner_id.id,
    #                 'journal_id': self.journal_id.id,
    #                 'journal_status':self.state,
    #                 'amount':self.amount,
    #                 # 'origin':self.account_id,
    #                 'journal_line_ids':[(0,0,{'account_id':line.account_id.id,
    #                                           'partner_id':line.partner_id.id,
    #                                           'name':line.name,
    #                                           'debit':line.debit,
    #                                           'credit':line.credit,
    #                                           'tax_ids':[(6, 0, [tax.id for tax in line.tax_ids])],
    #                                           'date_maturity':line.date_maturity
    #                                           }) for line in self.line_ids]
    #                 })
