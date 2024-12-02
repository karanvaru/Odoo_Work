from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

# class FinanceAnalysisType(models.Model):
#     _name = "finance.analysis.type"
#     _description = "Analysis Type"
#     _order = 'sequence, id'

#     name = fields.Char('Operation Type', required=True, translate=True)
#     color = fields.Integer('Color')
#     sequence = fields.Integer('Sequence', help="Used to order the 'All Operations' kanban view")
#     sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence', required=True)
#     account_payment_id = fields.Many2one('account.payment',string='Payments')
#     purchase_order_id = fields.Many2one('purchase.order', "Purchase Order")
#     sale_order_id = fields.Many2one('sale.order', "Sale Order")
#     return_analysis_type_id = fields.Many2one('finance.analysis.type', 'Operation Type for Returns')

class FinanceAnalysis(models.Model):
    _name = 'finance.analysis' 
    _description = "Finance Analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Reference', readonly=True, default='New', required=True,track_visibility=True)
    model_name = fields.Char('Model Name',readonly=True,track_visibility=True)
    is_active = fields.Boolean(invisible=1, compute="compute_active", store=True)
    model = fields.Char('Model',readonly=True,track_visibility=True)
    source_reference = fields.Char(string="Source Reference",readonly=True)
    source_date = fields.Date(string="Source Date", track_visibility=True,readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner", track_visibility=True,readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency",default=lambda self: self.env.user.company_id.currency_id,readonly=True)
    finance_analysis = fields.Boolean(string='Finance Analysis', default=True, track_visibility=True)
    payment_amount = fields.Monetary(string="Payment Amount", currency_field='currency_id',track_visibility=True,readonly=True)
    amount = fields.Monetary(string="Amount",track_visibility=True)
    office_location_id = fields.Many2one('office.location', string="Office Location", track_visibility=True)
    multiple_office_location_ids = fields.Many2many('office.location', string='Multiple Office Location', track_visibility=True)
    transaction_category_id = fields.Many2one('transaction.category', string='Transaction Category',track_visibility=True)
    transaction_sub_category_id = fields.Many2one('transaction.sub.category', string='Transaction Sub Category',track_visibility=True)
    transaction_category_type_id = fields.Many2one('transaction.category.type', string='Transaction Category Type',track_visibility=True)
    remaining_amount = fields.Monetary(string='Balance',track_visibility=True)
    # analysis_type_id = fields.Many2one('finance.analysis.type','Finance Analysis Type')
    color = fields.Integer('Color')
    status = fields.Selection([('draft', 'Draft'),
                                ('security_cheque', 'Security Cheques'),
                                ('register', 'Register'),
                                ('deposit', 'Deposit for Bounce'),
                                ('bounce', 'Bounce'),
                                ('posted', 'Posted'),
                                ('sent', 'Sent'),
                                ('reconciled', 'Reconciled'),
                                ('return', 'Return'),
                                ('cancelled', 'Cancelled'),
                                ('submit', 'Submitted'),
                                ('approve', 'Approved'),
                                ('post', 'Posted'),
                                ('done', 'Paid'),
                                ('cancel', 'Refused'),
                                ('open', 'Open'),
                                ('in_payment', 'In Payment'),
                                ('paid', 'Paid')], readonly=True,track_visibility=True)
   
    # invoice_count = fields.Integer(compute='compute_invoice_count')


# Sale 
    sale_order_id = fields.Many2one('sale.order', "Sale Order",track_visibility=True)
    sales_person_id = fields.Many2one('res.users', "Sales Person",compute = 'compute_sale_details',track_visibility=True,store=True)
    product_category_head_id = fields.Many2one('res.users', "Product Category Head",compute = 'compute_sale_details',track_visibility=True,store=True)
    revenue_head_id = fields.Many2one('res.users', "Revenue Head",compute = 'compute_sale_details',track_visibility=True,store=True)
    vice_president_id = fields.Many2one('res.users', "Vice President",compute = 'compute_sale_details',track_visibility=True,store=True)
    team_id = fields.Many2one('crm.team', "Sales Team",compute = 'compute_sale_details',track_visibility=True,store=True)
    so_gem_rp_id = fields.Many2one('res.partner', "SO GeM RP",compute = 'compute_sale_details',track_visibility=True,store=True)
# purchase
    purchase_order_id = fields.Many2one('purchase.order', "Purchase Order",track_visibility=True)
# Payment
    account_payment_id = fields.Many2one('account.payment',string='Payments',track_visibility=True)
    # payment_count = fields.Integer(compute='compute_payment_count',track_visibility=True)
    payment_type = fields.Selection([('outbound', 'Send Money'),('inbound', 'Receive Money'),
                                     ('transfer', 'Internal Transfer')], string='Payment Type',track_visibility=True, compute="compute_account_payment",store=True)
    partner_type = fields.Selection([('customer', 'Customer'),('supplier', 'Vendor')], string='Partner Type', track_visibility=True, compute="compute_account_payment",store=True)
    journal_id = fields.Many2one('account.journal', string="Payment Journal", track_visibility=True, compute="compute_account_payment",store=True)
    company_id = fields.Many2one('res.company', string='Company', track_visibility=True, compute="compute_account_payment",store=True)
# Expense
    hr_expense_id = fields.Many2one('hr.expense',track_visibility=True)
    description = fields.Char('Description',track_visibility=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Documents",help='Attach your Expense Bills',track_visibility=True)
    # hr_expense_amount = fields.Monetary(string="Expense Amount",track_visibility=True)
# Expense Sheet
    hr_expense_sheet_id = fields.Many2one('hr.expense.sheet',track_visibility=True)
    expense_date = fields.Date('Expense Date',track_visibility=True)
    # expenses_count = fields.Integer(compute='compute_expenses_count',track_visibility=True)

    # @api.depends('sale_order_id','sale_order_id.user_id','sale_order_id.product_category_head_id','sale_order_id.revenue_head_id','sale_order_id.revenue_head_id','sale_order_id.vice_president_id','sale_order_id.team_id')
    @api.depends('sale_order_id','sale_order_id.user_id','sale_order_id.team_id')
    def compute_sale_details(self):
        for rec in self:
            rec.sales_person_id = rec.sale_order_id.user_id
            # rec.product_category_head_id = rec.sale_order_id.product_category_head_id
            # rec.revenue_head_id = rec.sale_order_id.revenue_head_id
            # rec.vice_president_id = rec.sale_order_id.vice_president_id
            # rec.team_id = rec.sale_order_id.team_id
            # rec.so_gem_rp_id = rec.sale_order_id.so_gem_rp_id

    @api.depends('office_location_id','office_location_id.code')
    def compute_active(self):
        for rec in self:
            if rec.office_location_id:
                print('Sai Print=======================================================Priya')
                if rec.office_location_id.code == 'CO':
                    rec.is_active = True

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('finance.analysis.sequence')
        res = super(FinanceAnalysis, self).create(vals)
        return res
    
# Payment Count
    # def compute_payment_count(self):
    #     for rec in self:
    #         rec.payment_count = rec.env['account.payment'].search_count([('id','=',rec.account_payment_id.id)])
    
    @api.depends('account_payment_id','account_payment_id.payment_type','account_payment_id.partner_type','account_payment_id.journal_id','account_payment_id.company_id')
    def compute_account_payment(self):
        for rec in self:
            rec.payment_type = rec.account_payment_id.payment_type
            rec.partner_type = rec.account_payment_id.partner_type
            rec.journal_id = rec.account_payment_id.journal_id.id
            rec.company_id = rec.account_payment_id.company_id.id

# Payment Transaction Smart Button
    # @api.multi
    # def account_payment_count(self):
    #     return {
    #         'name': 'Payments',
    #         'res_model': 'account.payment',
    #         'view_mode': 'tree,form',
    #         'view_type': 'form',
    #         'target': 'current',
    #         'type': 'ir.actions.act_window',
    #         'domain': [('name','=',self.source_reference)],
    #     }
    
# Expense Sheet Count
    # def compute_expenses_count(self):
    #     for rec in self:
    #         rec.expenses_count = rec.env['hr.expense.sheet'].search_count([('id','=',rec.hr_expense_sheet_id.id)])

# Expense Report Transaction Smart Button
    # @api.multi
    # def hr_expenses_sheet_count(self):
    #     return {
    #         'name': 'Expenses',
    #         'res_model': 'hr.expense.sheet',
    #         'view_mode': 'tree,form',
    #         'view_type': 'form',
    #         'target': 'current',
    #         'type': 'ir.actions.act_window',
    #         'domain': [('name','=',self.source_reference)],
    #     }
    
# Invoice Transaction Smart Button
    # @api.multi
    # def action_view_invoice(self):
    #     invoices = self.mapped('invoice_ids')
    #     action = self.env.ref('account.action_invoice_tree1').read()[0]
    #     if len(invoices) > 1:
    #         action['domain'] = [('id', 'in', invoices.ids)]
    #     elif len(invoices) == 1:
    #         action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
    #         action['res_id'] = invoices.ids[0]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action

    @api.onchange('transaction_category_id')
    def compute_transaction_category(self):
        for rec in self:
            if rec.transaction_category_id:
                result = []
                sub_categ = rec.env['transaction.category.type'].search([])
                for record in sub_categ:
                    if rec.transaction_category_id.id in [c.id for c in record.transaction_category_ids]:
                        result.append(record.id)
                return {'domain': {'transaction_category_type_id':[('id','in',result)]}}
            
    def get_action_finance_analysis(self):
        return self._get_action('rdp_finance_analysis.action_finance_analysis')
