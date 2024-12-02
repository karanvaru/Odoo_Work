# # -*- coding: utf-8 -*-
# import logging
# from bdb import effective
# from odoo import fields, models, api, _
# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)

# class PaymentProjection(models.Model): 
#     _name = "payment.projection"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = 'Payment Projection'
#     _order='id desc' 

#     currency_id = fields.Many2one('res.currency', string='Currency',readonly=True,store=True)
#     name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
#     projection_date = fields.Date('Projection Date', default=fields.Date.context_today,store=True, track_visibility='onchange')
#     assigned_to = fields.Many2one('res.users', 'Assigned To', readonly=True,store=True,track_visibility='onchange')
#     inventory_total = fields.Monetary('Inventory Total', currency_field='currency_id',readonly=True, compute='compute_inventory_total', track_visibility='onchange')
#     vendor_bills_total = fields.Monetary('Vendor Bills Total', currency_field='currency_id',readonly=True,compute='compute_vendor_bill_total',track_visibility='onchange')
#     advance_payment_total = fields.Monetary('Advance Payment Total', currency_field='currency_id',readonly=True, compute='compute_advance_payment_total',track_visibility='onchange')
#     expense_amount = fields.Monetary('Reimbursement Total', currency_field='currency_id',readonly=True, compute='compute_expense_total',track_visibility='onchange')
#     rafc = fields.Monetary('Reserved Amount for Cheques(V)', currency_field='currency_id',readonly=True, compute='compute_cheque_payment',track_visibility='onchange')
#     available_bank_balance = fields.Monetary('Available Bank Balance', currency_field='currency_id',readonly=True, compute='compute_bank_balance',track_visibility='onchange')
#     projection_amount = fields.Monetary('Projection Amount', currency_field='currency_id',readonly=True, compute='compute_projection_amount',track_visibility='onchange')
#     balance_amount = fields.Monetary('Balance Amount', currency_field='currency_id',readonly=True, compute='compute_projection_balance_amount',track_visibility='onchange')

#     vendor_bills_projection_ids = fields.One2many('vendor.bills.projection.line','vendor_projection_id',store=True,readonly=True,compute='compute_vendor_bills', track_visibility='onchange')
#     advance_payments_projection_ids = fields.One2many('advance.payment.projection.line', 'advance_projection_id',store=True,readonly=True, compute='compute_advance_payments', track_visibility='onchange')
#     expenses_projection_ids = fields.One2many('expense.projection.line', 'expense_projection_id',store=True,readonly=True,compute='compute_expense_sheet', track_visibility='onchange')
#     bank_accounts_projection_ids = fields.One2many('bank.accounts.projection.line', 'bank_projection_id',store=True,readonly=True,compute='compute_bank_payments', track_visibility='onchange')
#     cheques_projection_ids = fields.One2many('cheques.projection.line', 'cheques_projection_id',store=True,readonly=True,compute='compute_cheques_payments', track_visibility='onchange')
   
    
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('submit', 'Submitted'),
#         ('approve', 'Approved'),
#         ('closed', 'CLOSED'),
#         ('cancel', 'Cancelled'),
#     ], string='Status', default='draft',track_visibility='onchange')

#     @api.model
#     def create(self,vals):
#         vals.update({
# 			'name': self.env['ir.sequence'].next_by_code('payment.projection.sequence'),
# 		})
#         return super(PaymentProjection, self).create(vals)
    
# # ========= Inventory Total==========================Dayan Compute=========================  
#     @api.multi
#     def compute_inventory_total(self):
#         for rec in self:
#             if rec.projection_date:
#                 inv_lines = rec.env['account.account'].search([('name','ilike','Inventories')])
#                 if inv_lines:
#                     for inl in inv_lines:
#                         rec.inventory_total = rec.inventory_total + inl['balance_amount']

# # ========= Vendor Bills Total==========================Dayan Compute=========================  
#     @api.multi
#     def compute_vendor_bill_total(self):
#         for rec in self:
#             if rec.projection_date:
#                 vendor_bills = rec.env['account.invoice'].search([('effective_date', '=', rec.projection_date),
#                  ('type', '=', 'in_invoice'),('state', 'not in', ['paid'])])
#                 if vendor_bills:
#                     for bill_amt in vendor_bills:
#                         rec.vendor_bills_total = rec.vendor_bills_total + bill_amt['residual']

# # ========= Advance Payment Total==========================Dayan Compute=========================  
#     @api.multi
#     def compute_advance_payment_total(self):
#         for rec in self:
#             if rec.projection_date:
#                 adv_payments = rec.env['advance.payment'].search(
#                     [('effective_date', '=', rec.projection_date), ('x_studio_status', 'in', ['submit'])])
#                 if adv_payments:
#                     for adv_amt in adv_payments:
#                         rec.advance_payment_total = rec.advance_payment_total + adv_amt['x_studio_advance_payment']

# # ========= Expense Total ==========================Dayan Compute=========================  
#     @api.multi
#     def compute_expense_total(self):
#         for rec in self:
#             expense_lists = rec.env['hr.expense.sheet'].search([('state','in',['post'])])
#             if expense_lists:
#                 for exp in expense_lists:
#                     rec.expense_amount = rec.expense_amount + exp['total_amount']

# # ===========Available Bank Balance=====================Dayan Compute==============================
#     @api.multi
#     def compute_bank_balance(self):
#         for rec in self:
#             if rec.projection_date:
#                 jitems = rec.env['account.move.line'].search([('x_studio_account_type', 'ilike', 'Bank and Cash'), ('account_id', 'not ilike', 'close'),('date', '<=', rec.projection_date)])
#                 if jitems:
#                     for avb in jitems:
#                         rec.available_bank_balance = rec.available_bank_balance + avb['balance']

# # ========= Reserved Amount for Cheques(V) Total====================Dayan Compute====================
#     @api.multi
#     def compute_cheque_payment(self):
#         for rec in self:
#             cheque_payments = rec.env['account.payment'].search(
#                 [('payment_type', '=', 'outbound'), ('payment_method_id', 'ilike', 'check'),('state', 'not in', ['posted', 'reconciled', 'return', 'cancelled','security_cheque'])])
#             if cheque_payments:
#                 for cp in cheque_payments:
#                     rec.rafc = rec.rafc + cp['amount']

# # ===========Projection Amount=====================Dayan Compute====================================
#     @api.multi
#     def compute_projection_amount(self):
#         for record in self:
#             if record.projection_date or record.vendor_bills_total or record.advance_payment_total or record.expense_amount:
#                 record.projection_amount = record.vendor_bills_total + record.advance_payment_total + record.expense_amount

# # =========== Balance Amount=====================Dayan Compute========================================
    
#     @api.multi
#     def compute_projection_balance_amount(self):
#         for record in self:
#             if record.available_bank_balance or record.rafc or record.projection_amount:
#                 record.balance_amount = record.available_bank_balance - record.rafc - record.projection_amount

# # ========= Vendor Bills Line==========================Dayan Compute===================================  
#     @api.depends('projection_date')
#     @api.multi
#     def compute_vendor_bills(self):
#         for inv in self:
#             if inv.projection_date:
#                 vend_bills = inv.env['account.invoice'].search([('effective_date','=',inv.projection_date),('type','=','in_invoice'),('state','not in',['paid'])])
#                 if vend_bills:
#                     val=[(5,0,0)]
#                     for rec in vend_bills:
#                         val.append({
#                             'create_date': rec.create_date,
#                             'date_invoice': rec.date_invoice,
#                             'effective_date': rec.effective_date,
#                             'number': rec.number,
#                             'partner_id': rec.partner_id,
#                             'date_due': rec.date_due,
#                             'amount_untaxed': rec.amount_untaxed,
#                             'amount_tax_signed': rec.amount_tax_signed,
#                             'amount_total_signed': rec.amount_total_signed,
#                             'residual_signed': rec.residual_signed,
#                             'state': rec.state,
#                         })
#                     inv.update({'vendor_bills_projection_ids':val})

# # ========= Advance Payments Line==========================Dayan Compute=====================
#     @api.depends('projection_date')
#     @api.multi
#     def compute_advance_payments(self):
#         for adv in self:
#             if adv.projection_date:
#                 adv_payments = adv.env['advance.payment'].search([('effective_date','=',adv.projection_date),('x_studio_status','in',['submit'])])
#                 if adv_payments:
#                     val=[(5,0,0)]
#                     for rec in adv_payments:
#                         if rec.purchase_order:
#                             obj_origin = str(rec.purchase_order.name)
#                         else:
#                             obj_origin = str(rec.x_studio_field_dtu5f.name)
#                         # _logger.info("---obj_origin--------%r-----------------------------------",obj_origin)
                       
#                         if rec.x_studio_vendor:
#                             obj_partner_id = rec.x_studio_vendor.id
#                         else:
#                             obj_partner_id = rec.x_studio_contact.id
#                         # _logger.info("---obj_partner_id--------%r-----------------------------------",obj_partner_id)
#                         val.append({
#                             'create_date': rec.create_date, 
#                             'date': rec.date,
#                             'effective_date': rec.effective_date,

#                             'origin':  obj_origin or '',
#                             'partner_id': obj_partner_id,
                            
#                             # 'origin':  [org for org in adv_payments if org.purchase_order == True if org.x_studio_field_dtu5f == True],
#                             # 'partner_id': [org for org in adv_payments if org.x_studio_vendor == True if org.x_studio_contact == True],

#                             # 'purchase_id': rec.purchase_order,
#                             # 'budget_id': rec.x_studio_field_dtu5f,
#                             # 'partner_id': rec.x_studio_vendor,
#                             # 'contact_id': rec.x_studio_contact,

#                             'advance_payment': rec.x_studio_advance_payment,
#                             'state': rec.x_studio_status,
#                         })
#                     adv.update({'advance_payments_projection_ids':val})
#                     # _logger.info("---val--------%r-----------------------------------",val)
# # ========= Expenses Line==========================Dayan Compute=============================  
#     @api.depends('projection_date')
#     @api.multi
#     def compute_expense_sheet(self):
#         for exp in self:
#             if exp.projection_date:
#                 expense_list = exp.env['hr.expense.sheet'].search([('effective_date','=',exp.projection_date),('state','in',['post'])])
#                 if expense_list:
#                     val=[(5,0,0)]
#                     for rec in expense_list:
#                         val.append({
#                             'create_date': rec.create_date,
#                             'accounting_date': rec.accounting_date,
#                             'effective_date': rec.effective_date,
#                             'employee_id': rec.employee_id,
#                             'name': rec.name,
#                             'total_amount': rec.total_amount,
#                             'state': rec.state,
#                         })
#                     exp.update({'expenses_projection_ids':val})

# # =========Bank Accounts Line ==========================Dayan Compute=========================  
#     @api.depends('projection_date')
#     @api.multi
#     def compute_bank_payments(self):
#         for bnk in self:
#             if bnk.projection_date:
#                 # bank_account_lines = bnk.env['account.account'].search(['&','&',('user_type_id','ilike','bank'),('name','not ilike','close'),('balance_amount','!=',0)])
#                 bank_account_lines = bnk.env['account.account'].search([('user_type_id','ilike','bank'),('name','not ilike','close')])
#                 if bank_account_lines:
#                     val=[(5,0,0)]
#                     for rec in bank_account_lines:
#                         val.append({
#                             'code': rec.code,
#                             'name': rec.name,
#                             'user_type_id': rec.user_type_id,
#                             'currency_id': rec.currency_id,
#                             'company_id': rec.company_id,
#                             'account_balance': rec.balance_amount,
#                         })
#                     bnk.update({'bank_accounts_projection_ids':val})

# # =========Cheques Payment Line==========================Dayan Compute=========================  
#     @api.depends('projection_date')
#     @api.multi
#     def compute_cheques_payments(self):
#         for chq in self:
#             if chq.projection_date:
#                 cheque_payment = chq.env['account.payment'].search([('payment_type','=','outbound'),('payment_method_id','ilike','check'),('state','not in',['posted','reconciled','return','cancelled','security_cheque'])])
#                 if cheque_payment:
#                     val=[(5,0,0)]
#                     for rec in cheque_payment:
#                         val.append({
#                             'payment_date': rec.payment_date,
#                             'journal_id': rec.journal_id,
#                             'payment_method_id': rec.payment_method_id,
#                             'cheque_ref': rec.check_ref,
#                             'partner_id': rec.partner_id,
#                             'amount': rec.amount,
#                             'state': rec.state,
#                         })
#                     chq.update({'cheques_projection_ids':val})

# # =====================Stages=========================Dayan======================================

#     @api.multi
#     def action_submit(self):
#         self.write({'state': 'submit'})
#         return

#     @api.multi
#     def action_approve(self):
#         self.write({'state': 'approve'})
#         return

#     @api.multi
#     def action_close(self):
#         self.write({'state': 'closed'})
#         return

#     @api.multi
#     def action_cancel(self):
#         self.write({'state': 'cancel'})
#         return

#     @api.multi
#     def action_set_to_draft(self):
#         self.write({'state':'draft'})
#         return

# # ============Vendor Bills Projection Line=============================Dayan=======================
# class VendorBillsProjectionLine(models.Model):
#     _name = 'vendor.bills.projection.line'
#     _description = 'Vendor Bills Projection Line'
#     _order='id desc'

#     vendor_projection_id = fields.Many2one('payment.projection', string='Vendor Bills Projection Reference',invisible=True)
#     currency_id = fields.Many2one('res.currency','Account Currency')
#     create_date = fields.Datetime('Created On')
#     date_invoice = fields.Date('Bill Date')
#     effective_date = fields.Date('Effective Date')
#     number = fields.Char('Number')
#     partner_id = fields.Many2one('res.partner','Vendor')
#     date_due = fields.Date('Due Date')
#     amount_untaxed = fields.Monetary('Untaxed Amount',currency_field='currency_id')
#     amount_tax_signed = fields.Monetary('Tax')
#     amount_total_signed = fields.Monetary('Total')
#     residual_signed = fields.Monetary('To Pay')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('open', 'Open'),
#         ('in_payment', 'In Payment'),
#         ('paid', 'Paid'),
#         ('cancel', 'Cancelled'),
#     ], string='Status')

# # =============Advance Payment Projection Line=========================Dayan=======================

# class AdvancePaymentProjectionLine(models.Model):
#     _name = 'advance.payment.projection.line'
#     _description = 'Advance Payment projection Line'
#     _order='id desc'

#     advance_projection_id = fields.Many2one('payment.projection', string='Advance Payment Projection Reference',invisible=True)
#     currency_id = fields.Many2one('res.currency','Account Currency')
#     create_date = fields.Datetime('Created On')
#     date = fields.Date('Date')
#     effective_date = fields.Date('Effective Date')
#     # purchase_id = fields.Many2one('purchase.order','Source Document')
#     # budget_id = fields.Many2one('bills.approvals','Source Document')
#     origin = fields.Char('Source Document')
#     partner_id = fields.Many2one('res.partner','Contact')
#     # contact_id = fields.Many2one('res.partner','Contact')
#     advance_payment = fields.Monetary('Advance Payment',currency_field='currency_id')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('submit', 'Submit'),
#         ('create_payment', 'Payment'),
#         ('Close', 'Close'),
#         ('cancel', 'Cancelled'),
#     ], string='Status')

# # ============Expense Projection Line==================================Dayan=======================

# class ExpenseProjectionLine(models.Model):
#     _name = 'expense.projection.line'
#     _description = 'Expense Projection Line'
#     _order='id desc'

#     expense_projection_id = fields.Many2one('payment.projection', string='Expense Projection Reference',invisible=True)
#     currency_id = fields.Many2one('res.currency','Account Currency')
#     create_date = fields.Datetime('Created On')
#     accounting_date = fields.Date('Date')
#     effective_date = fields.Date('Effective Date')
#     employee_id = fields.Many2one('hr.employee','Employee')
#     name = fields.Char('Expense Report')
#     total_amount = fields.Monetary('Total Amount',currency_field='currency_id')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('submit', 'Submitted'),
#         ('approve', 'Approved'),
#         ('post', 'Posted'),
#         ('done', 'Paid'),
#         ('cancel', 'Refused'),
#     ], string='Status')

# # ============Bank Accounts Projection Line==================================Dayan=================

# class BankAccountsProjectionLine(models.Model):
#     _name = 'bank.accounts.projection.line'
#     _description = 'Bank Accounts Projection Line'
#     _order='id desc'

#     bank_projection_id = fields.Many2one('payment.projection', string='Bank Accounts Projection Reference',invisible=True)
#     code = fields.Char('Code')
#     name = fields.Char('Name')
#     user_type_id = fields.Many2one('account.account.type','Type')
#     currency_id = fields.Many2one('res.currency','Account Currency')
#     company_id = fields.Many2one('res.company','Company')
#     account_balance = fields.Monetary('Balance Amount')

# # ============Cheques Projection Line==================================Dayan=======================

# class ChequesProjectionLine(models.Model):
#     _name = 'cheques.projection.line'
#     _description = 'Cheques Projection Line'
#     _order='id desc'

#     cheques_projection_id = fields.Many2one('payment.projection', string='Cheques Projection Reference',invisible=True)
#     currency_id = fields.Many2one('res.currency','Account Currency')
#     payment_date = fields.Date('Payment Date')
#     journal_id = fields.Many2one('account.journal','Payment Journal')
#     payment_method_id = fields.Many2one('account.payment.method','Payment Method Type')
#     cheque_ref = fields.Char('Cheque Reference')
#     partner_id = fields.Many2one('res.partner','Customer')
#     amount = fields.Monetary('Payment Amount',currency_field='currency_id')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('security_cheque', 'Security Cheques'),
#         ('register', 'Register'),
#         ('deposit', 'Deposit for Bounce'),
#         ('bounce', 'Bounce'),
#         ('posted', 'Posted'),
#         ('sent', 'Sent'),
#         ('reconciled', 'Reconciled'),
#         ('return', 'Return'),
#         ('cancelled', 'Cancelled'),
#     ], string='Status')

# # ============Effective Date========================Dayan=================================

# class AccountInvoice(models.Model):
#     _inherit = 'account.invoice'
    
#     effective_date = fields.Date('Effective Date',store=True, readonly=False, compute='compute_effective_date')
    
#     @api.depends('date_due')
#     @api.multi
#     def compute_effective_date(self):
#         for rec in self:
#             if rec.date_due:
#                 rec.effective_date = rec.date_due

# class AdvancePayment(models.Model):
#     _inherit = 'advance.payment'

#     effective_date = fields.Date('Effective Date',store=True, readonly=False, compute='compute_effective_date')
    
#     @api.depends('date')
#     @api.multi
#     def compute_effective_date(self):
#         for rec in self:
#             if rec.date:
#                 rec.effective_date = rec.date

# class AccountAccount(models.Model):
#     _inherit = 'account.account'

#     balance_amount = fields.Monetary('Balance Amount', compute='compute_balance_amount',track_visibility='onchange')
    
#     @api.multi
#     def compute_balance_amount(self):
#         for record in self:
#             jname = record['name']
#             total_j = self.env['account.move.line'].search([('account_id.name', '=', jname)])
#             if total_j:
#                 for tb in total_j:
#                     record['balance_amount'] = record['balance_amount'] + tb['balance']
#                     if record.balance_amount == 0.00:
#                         record.zero_balance = True
                    
# class ExpensesInherited(models.Model):
#     _inherit='hr.expense.sheet'
    
#     effective_date = fields.Date('Effective Date',store=True, readonly=False, compute='compute_effective_date')

#     @api.depends('accounting_date')
#     @api.multi
#     def compute_effective_date(self):
#         for rec in self:
#             if rec.accounting_date:
#                 rec.effective_date = rec.accounting_date
