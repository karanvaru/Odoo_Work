import io
from PIL import Image
import pytesseract
from odoo import fields, models, _
from odoo import api, SUPERUSER_ID
# import cv2
import re
import phonenumbers
import datetime
import logging
from odoo import http
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CreditApproval(models.Model):
    _name = "credit.approval"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Credit Approval"

    # name = fields.Char(
    #     'Name', default=lambda self: self.env['ir.sequence'].next_by_code('credit.approval.sequence'),
    #     required=True)
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    # name = fields.Char(copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('credit.approval.sequence'))
    
    partner_id = fields.Many2one('res.partner', string="Partner")
    
    # email = fields.Char("Email")
    # phone = fields.Char("Phone", unaccent=False)
    # street = fields.Char("Street")
    # zip = fields.Char("Zip", change_default=True)
    # city = fields.Char("City")
    # state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
    #                            domain="[('country_id', '=?', country_id)]")
    # country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    state = fields.Selection([
        ('draft', 'Not Confirmed'),
        ('approve', 'Confirmed'),
        ('reject', 'Reject'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    credit_amount = fields.Float('Credit Amount')
    description = fields.Text('Description')
    available_credit = fields.Float('Available Credit' , compute="compute_availabe_credit")

    def action_approve(self):
        for rec in self:
            if rec.available_credit:
                total_credit_amount = rec.available_credit + rec.credit_amount
                val = rec.partner_id.update({
                    'use_partner_credit_limit': 'True',
                    'credit_limit': total_credit_amount})
            else:
                val = rec.partner_id.update({
                    'use_partner_credit_limit': 'True',
                    'credit_limit': rec.credit_amount})

        self.write({
                'state': 'approve'})
            
    @api.depends('partner_id')
    def compute_availabe_credit(self):
        for rec in self:
                rec.available_credit = rec.partner_id.credit_limit

       

    def action_reject(self):
        self.write({
            'state': 'reject',
        })
    # @api.model 
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('credit.approval.sequence')
    #     return super(CreditApproval, self).create(vals)  
    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('credit.approval.sequence')
           
        })
        res = super(CreditApproval, self).create(vals)
        return res


# class ResPartner(models.Model):
#     _inherit = 'res.partner'

#     credit_approval_id = fields.Many2one('credit.approval',"Credit Approval")
