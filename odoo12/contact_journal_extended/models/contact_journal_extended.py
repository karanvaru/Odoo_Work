from odoo import api, fields, models
import re
from odoo.exceptions import ValidationError


class ContactExtended(models.Model):

    _inherit = 'res.partner'

    pan = fields.Char(string="PAN")

    @api.constrains('pan')
    def validating_pan(self):
        for rec in self:
            result = re.compile("[A-Za-z]{5}\d{4}[A-Za-z]{1}")
            if rec.pan:
                if not result.match(rec.pan):
                    raise ValidationError('Invalid PAN')


class JournalExtended(models.Model):

    _inherit = 'account.move.line'

    partner_pan = fields.Char(string="PAN", compute="compute_pan")


    def compute_pan(self):
        for rec in self:
            rec.partner_pan = rec.partner_id.pan


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    state_id = fields.Many2one('res.country.state', string="State", compute='compute_state')

    def compute_state(self):
        for rec in self:
            rec.state_id = rec.partner_id.state_id.id

# class StockMoveLine(models.model):
#     _inherit = 'stock.move.line'
#
#     company_id = fields.Many2one('res.company', string="Company", compute="compute_company")
#
#     def compute_company(self):
#         for rec in self:
#             rec.company_id = rec.move_id.company_id.id

