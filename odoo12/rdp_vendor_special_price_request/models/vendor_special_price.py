from odoo import api, fields, models, _
from datetime import date, datetime

class VendorSpecialPrice(models.Model):
    _name = "vendor.special.price"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Vendor Special Price Request"
    _order = 'create_date desc'

    name = fields.Char(string='Reference', copy=False, index=True,
                       default=lambda self: _('New'))
    lead_oppurtunity_id = fields.Many2one('crm.lead', 'Lead/Oppurtunity', track_visibility='always')
    bid_tender_closed_date = fields.Date(string='Bid/Tender Close Date', track_visibility='always')
    sales_person_id = fields.Many2one('res.users', 'Sales Person', track_visibility='always')
    sales_team_id = fields.Many2one('crm.team', 'Sales Team', track_visibility='always')
    vspr_program_id = fields.Many2one('vspr.program', 'VSPR Program', track_visibility='always')
    brand_id = fields.Many2one('product.brand.amz.ept', 'Brand', track_visibility='always')
    requested_through_distributor_id = fields.Many2one('res.partner', 'Requested Through Distributor', track_visibility='always')
    quantity = fields.Integer(string='Quantity', track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='always')

    requested_date = fields.Date(string='Requested Date', track_visibility='always')
    requested_sku_id = fields.Many2one('product.product', string='Requested SKU', track_visibility='always')
    requested_quantity = fields.Integer(string='Requested Quantity', track_visibility='always')
    requested_price_in_inr_incl_tax = fields.Monetary(currency_field="currency_id", string="Requested Price(In INR Incl Tax)", track_visibility='always')
    requested_price_in_usd = fields.Float(string='Requested Price(In USD)', track_visibility='always')
    market_operating_price = fields.Monetary(currency_field="currency_id", string='Market Operating Price(In INR Incl Tax)', track_visibility='always')
    competitor_brand = fields.Char(string='Competitor Brand', track_visibility='always')
    competitor_model_no = fields.Char(string='Competitor Model No', track_visibility='always')
    competitor_price = fields.Monetary(currency_field="currency_id", string='Competitor Price(in INR Incl Tax)', track_visibility='always')
    approved_date = fields.Date(string='Approved Date', track_visibility='always')
    approved_sku_id = fields.Many2one('product.product', string='Approved SKU', track_visibility='always')
    valid_till = fields.Date(string='Valid Till', track_visibility='always')
    approved_price_in_usd = fields.Float(string='Approved Price(In USD)', track_visibility='always')
    approved_price_in_inr_excl_tax = fields.Monetary(currency_field="currency_id", string='Approved Price(In INR Incl Tax)', track_visibility='always')

    extension_requested_date = fields.Date(string='Extension Requested Date', track_visibility='always')
    extension_valid_till = fields.Date(string='Extension Valid Till', track_visibility='always')
    discount_received = fields.Char(string='Discount Received(%)', compute="compute_discount_received")
    valid_days_remaining = fields.Char(string='Valid Days Remaining', compute="valid_days")
    closed_date = fields.Date('Closed Date')
    description = fields.Html("Description", track_visibility='always')

    state = fields.Selection([
        ('a_draft', 'DRAFT'),
        ('b_request_sent', 'REQUEST SENT'),
        ('c_approved', 'APPROVED'),
        ('d_rejected', 'REJECTED'),
        ('e_expired', 'EXPIRED')
    ], string='Status', default='a_draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('vendor.special.price.sequence'),
        })

        return super(VendorSpecialPrice, self).create(vals)

    @api.multi
    def action_to_request_sent(self):
        self.state = 'b_request_sent'

    @api.multi
    def action_to_approved(self):
        self.state = 'c_approved'

    @api.multi
    def action_to_rejected(self):
        self.state = 'd_rejected'

    @api.multi
    def action_to_expired(self):
        self.state = 'e_expired'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'a_draft'})

    @api.depends('approved_price_in_inr_excl_tax')
    def compute_discount_received(self):
        for record in self:
            if record['market_operating_price']:
                record['discount_received'] = "{:.2f}".format(((record['market_operating_price'] -record['approved_price_in_inr_excl_tax']) / record['market_operating_price']) * 100)
                record['discount_received'] = record['discount_received'] + '%'

    @api.depends('valid_till')
    def valid_days(self):
        for record in self:
            if record['valid_till']:
                record['valid_days_remaining'] = record['valid_till'] - date.today()
                record['valid_days_remaining'] = record['valid_days_remaining'].split(',')[0]


class VSPRProgram(models.Model):
    _name = "vspr.program"
    _description = "VSPR Program"

    name = fields.Char("VSPR Program")



