from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    total_discount_amount = fields.Monetary(
        string='Total Discount Amount',
        compute='_compute_total_discount_amount',
        store=True,
    )
    ############## Added by sabitha 24-8-2023##############
    gst_returns_year_id = fields.Many2one('account.gst.returns.year',string="GST Filed Year",track_visibility="onchange")
    gst_returns_month_id = fields.Many2one('account.gst.returns.month',string="GST Filed Month",track_visibility="onchange")
    challan_number = fields.Char('Challan Number',track_visibility="always")
    bsr_code = fields.Char('BSR Code',track_visibility="always")
    tds_certificate_number  = fields.Char('TDS Certificate No',track_visibility="always")
    tds_certificate  = fields.Binary('TDS Certificate',track_visibility="always",filename="filename")
    challan_amount = fields.Char('Challan Amount',track_visibility="always")
    account_tds_paid_month_id = fields.Many2one('account.tds.paid.month','TDS Paid Month',track_visibility="onchange")
    account_tds_paid_year_id = fields.Many2one('account.tds.paid.year','TDS Paid Year',track_visibility="onchange")
    pan = fields.Char('PAN',
                      # compute="compute_pan_number"
                      )
    tax_type_id = fields.Many2one('account.tds.tax.type',string="Tax Type", track_visibility="onchange")

    
    
    @api.depends('invoice_line_ids.discount_amount')
    def _compute_total_discount_amount(self):
        for invoice in self:
            invoice.total_discount_amount = sum(invoice.invoice_line_ids.mapped('discount_amount'))
    # @api.model
    # def create(self, vals):
    #     res = super(AccountInvoice, self).create(vals)
    #     account_move_obj = self.env['account.move'].search([('id','=',self.move_id.id)])
    #     vals =account_move_obj.update({
    #             'challan_number':res.challan_number,
    #             'bsr_code':res.bsr_code,
    #             'tds_certificate_number':res.tds_certificate_number,
    #             'tds_certificate':res.tds_certificate,
    #             'challan_amount':res.challan_amount,
    #             'account_tds_paid_month_id':res.account_tds_paid_month_id.id,
    #             'account_tds_paid_year_id':res.account_tds_paid_year_id.id,
    #             'gst_returns_year_id':res.gst_returns_year_id.id,
    #             'gst_returns_month_id':res.gst_returns_month_id.id,


    #         })
    @api.model
    def action_invoice_create(self, grouped=False, final=False):
        res = super(AccountInvoice, self).action_invoice_create(grouped, final)
        account_move_obj = self.env['account.move'].search([('id','=',self.move_id.id)])
        vals =account_move_obj.update({
                'challan_number':res.challan_number,
                'bsr_code':res.bsr_code,
                'tds_certificate_number':res.tds_certificate_number,
                'tds_certificate':res.tds_certificate,
                'challan_amount':res.challan_amount,
                'account_tds_paid_month_id':res.account_tds_paid_month_id.id,
                'account_tds_paid_year_id':res.account_tds_paid_year_id.id,
                'gst_returns_year_id':res.gst_returns_year_id.id,
                'gst_returns_month_id':res.gst_returns_month_id.id,
                'tax_type_id':res.tax_type_id.id,


            })
        
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        for rec in self:
                account_move_obj = rec.env['account.move'].search([('id','=',rec.move_id.id)])
                vals =account_move_obj.update({
                'challan_number':rec.challan_number,
                'bsr_code':rec.bsr_code,
                'tds_certificate_number':rec.tds_certificate_number,
                'tds_certificate':rec.tds_certificate,
                'challan_amount':rec.challan_amount,
                'account_tds_paid_month_id':rec.account_tds_paid_month_id.id,
                'account_tds_paid_year_id':rec.account_tds_paid_year_id.id,
                'gst_returns_year_id':rec.gst_returns_year_id.id,
                'gst_returns_month_id':rec.gst_returns_month_id.id,
                'tax_type_id':rec.tax_type_id.id,



            })
                     
        return res        

    # @api.depends('partner_id')
    # def compute_pan_number(self):
    #     for rec in self:
    #         rec.pan = rec.partner_id.pan

class AccountMoveLine(models.Model):
    _inherit = 'account.invoice.line'

    discount_amount = fields.Monetary(
        string='Discount Amount',
        compute='_compute_discount_amount',
        store=True,
    )
    user_id = fields.Many2one('res.users',string="Sales Person",compute="compute_sales_team")
    team_id = fields.Many2one('crm.team',string="Sales Team",compute="compute_sales_team")
    parent_product_category_id = fields.Many2one('product.category','Parent Product Category',compute="compute_parent_product_category")
  

    @api.depends('invoice_id')
    def compute_sales_team(self):
        for rec in self:
            rec.user_id = rec.invoice_id.user_id.id
            rec.team_id = rec.invoice_id.team_id.id

    @api.depends('categ_id')
    def compute_parent_product_category(self):
        for rec in self:
            rec.parent_product_category_id = rec.categ_id.parent_id.id



    @api.depends('discount', 'price_unit', 'quantity')
    def _compute_discount_amount(self):
        for line in self:
            line.discount_amount = (line.price_unit * line.quantity) * (line.discount / 100)

############## Added by sabitha 24-8-2023##############
class AccountGSTReturnsYear(models.Model):
    _name = "account.gst.returns.year"   
    _description ="Account GST Returns Year"  

    name = fields.Char('Name')

class AccountGSTReturnsMonth(models.Model):
    _name = "account.gst.returns.month"   
    _description ="Account GST Returns Month"  

    name = fields.Char('Name') 

class AccountParentTypeID(models.Model):
    _name = "account.parent.type"   
    _description ="Account Parent Type"  

    name = fields.Char('Name')     

class AccountTDSMonth(models.Model):
    _name = "account.tds.paid.month"   
    _description ="Account TDS Paid Month"  

    name = fields.Char('Name')    

class AccountTDSYear(models.Model):
    _name = "account.tds.paid.year"   
    _description ="Account TDS Paid Year"  

    name = fields.Char('Name')   

class AccountTDSTaxType(models.Model):
    _name = "account.tds.tax.type"   
    _description ="Account TDS Tax Type"  

    name = fields.Char('Name')          

       
class AccountAccountInherited(models.Model):
    _inherit = "account.account"

    parent_type_id = fields.Many2one('account.parent.type',strring="Parent Type",track_visiblity="onchange")
    parent_type = fields.Selection([
        ('shareholder_funds', "Shareholder's Funds"),
        ('share_application_money_pending_allotment', 'Share Application Money Pending Allotment'),
        ('long_term_borrowings', 'Long-term Borrowings'),
        ('deferred_tax_liabilities', 'Deferred Tax Liabilities (Net)'),
        ('other_long_term_liabilities', 'Other Long-term Liabilities'),
        ('long_term_provisions', 'Long-term Provisions'),
        ('short_term_borrowings', 'Short-term Borrowings'),
        ('trade_payables', 'Trade Payables'),
        ('other_current_liabilities', 'Other Current Liabilities'),
        ('short_term_provisions', 'Short-term Provisions'),
        ('tangible_assets', 'Tangible Assets'),
        ('intangible_assets', 'Intangible Assets'),
        ('capital_work_in_progress', 'Capital Work-in Progress'),
        ('intangible_assets_under_development', 'Intangible Assets Under Development'),
        ('non_current_investments', 'Non Current Investments'),
        ('deferred_tax_assets', 'Deferred Tax Assets (Net)'),
        ('long_term_loans_and_advances', 'Long-term Loans and Advances'),
        ('other_non_current_Assets', 'Other Non-current Assets'),
        ('current_investments', 'Current Investments'),
        ('inventories', 'Inventories'),
        ('trade_receivables', 'Trade Receivables'),
        ('cash_and_cash_equivalents', 'Cash and Cash Equivalents'),
        ('short_term_loans_and_advances', 'Short-term Loans and Advances'),
        ('other_current_assets', 'Other Current Assets'),
    ], string='Parent Type', track_visibility="always",required=True)    
    id_parent_type = fields.Integer('Parent Type ID',related="parent_type_id.id",store=True,track_visiblity="onchange")

    

