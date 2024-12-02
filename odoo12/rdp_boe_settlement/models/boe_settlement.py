from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import ValidationError


class BOESettlement(models.Model):
    _name = "boe.settlement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "BOE Settlement"
    _order = 'id desc'

    name = fields.Char(string='Reference', required=True, copy=False, track_visibility='always', readonly=True,
                       index=True,
                       default=lambda self: _('New'))
    number = fields.Char(string="Bill No", track_visibility='always')
    partner_id = fields.Many2one('res.partner', string="Vendor", track_visibility='always')
    bill_date = fields.Date(string="Bill Date", track_visibility='always')
    company_id = fields.Many2one('res.company', string='company', default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency',string="Currency",default=lambda self:self.env.user.company_id.currency_id)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", currency_field='currency_id', track_visibility='always')
    amount_tax = fields.Monetary(string="Tax", currency_field='currency_id', track_visibility='always')
    amount_total = fields.Monetary(string="Total", currency_field='currency_id', track_visibility='always')
    bill_of_entry_no = fields.Char(string="Bill Of Entry No", track_visibility='always')
    edpms_no = fields.Char(string="EDPMS No", track_visibility='always')
    invoice_amount_usd = fields.Integer(string="Invoice Value [USD]", track_visibility='always')
    boe_amount_usd = fields.Integer(string="BOE Value [USD]",track_visibility='always')
    invoice_value_usd = fields.Integer(string="Invoice Value [USD]", track_visibility='always')
    boe_value_usd = fields.Integer(string="BOE Value [USD]", track_visibility='always')
    balance_value_usd = fields.Integer(string="Balance Value [USD]", compute="compute_balance_value_usd", track_visibility='always' )
    boe_document = fields.Binary(string="BOE Document", track_visibility='always')
    file_name = fields.Char('File Name')
    file_name_one = fields.Char('File Name')
    file_name_two = fields.Char('File Name')
    file_name_three = fields.Char('File Name')
    edpms_document = fields.Binary(string="EDPMS Document", track_visibility='always')
    transporter_document = fields.Binary(string="Transporter Document", track_visibility='always')
    proforma_invoice_document = fields.Binary(string="Proforma Invoice Document", track_visibility='always')
    completed_percentage = fields.Integer(string="Completed Percentage", compute="progress_bar", track_visibility='always')
    description = fields.Text(string="Notes")
    state = fields.Selection([
        ('new', 'New'),
        ('pending_from_checker', 'Pending From Checker'),
        ('approved_by_checker', 'Approved By Checker'),
        ('pending_from_bank', 'Pending From Bank'),
        ('approved_by_bank', 'Approved By Bank'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='new', track_visibility='always')
    open_days = fields.Char(string='Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime(string='Closed date')

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('bill.of.exchange.sequence')
        })
        res = super(BOESettlement, self).create(vals)
        return res

    @api.depends('state')
    def progress_bar(self):
        for rec in self:
            if rec.state == "new":
                completed_percentage = 0
            elif rec.state == "pending_from_checker":
                completed_percentage = 25
            elif rec.state == "approved_by_checker":
                completed_percentage = 50
            elif rec.state == "pending_from_bank":
                completed_percentage = 75
            elif rec.state == "approved_by_bank":
                completed_percentage = 95
            elif rec.state == "close":
                completed_percentage = 100
            else:
                completed_percentage = 0
            rec.completed_percentage = completed_percentage

    @api.depends('invoice_value_usd', 'boe_value_usd')
    def compute_balance_value_usd(self):
        for rec in self:
            if rec.invoice_value_usd > rec.boe_value_usd:
                rec.balance_value_usd = rec.invoice_value_usd - rec.boe_value_usd
            else:
                rec.balance_value_usd = 0


    @api.multi
    def action_set_new(self):
        self.write({'state': 'new'})

    @api.multi
    def action_to_submit(self):
        self.state = 'pending_from_checker'

    @api.multi
    def action_to_approval(self):
        self.state = 'approved_by_checker'

    @api.multi
    def action_submit_to_bank(self):
        self.state = 'pending_from_bank'

    @api.multi
    def action_bank_approval(self):
        self.state = 'approved_by_bank'

    # @api.multi
    # def action_approved_by_bank(self):
    #     self.state = 'approved_by_bank'

    @api.multi
    def action_to_closed(self):
        self.state = "closed"
        self.closed_date = datetime.today()

    @api.multi
    def action_to_cancelled(self):
        self.state = "cancelled"

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = str((rec.closed_date - rec.create_date).days) + " Days"
            else:
                rec.open_days = str((datetime.today() - rec.create_date).days) + " Days"










