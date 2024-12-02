from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class PaymentCategory(models.Model):
    _name = 'payment.category'

    name = fields.Char('Name')

class AssetLocation(models.Model):
    _name = 'asset.location'

    name = fields.Char('Name')

class AssetPayment(models.Model):
    _name = 'asset.payment'

    name = fields.Char('Name')

class AssetCategory(models.Model):
    _name = 'asset.category'

    name = fields.Char('Name')

class PaymentTags(models.Model):
    _name = 'payment.tags'

    name = fields.Char(string='Name')

class RDPPayments(models.Model):
    _inherit = 'account.payment'

    payment_category_id = fields.Many2one('payment.category','Payment Category', required=True)
    asset_location_id = fields.Many2one('asset.location','Location')
    asset_payment_id = fields.Many2one('asset.payment','Asset Payment For')
    asset_category_id = fields.Many2one('asset.category','Asset Category')
    tags = fields.Many2many('payment.tags', string="Payment Tags")
    note = fields.Text()
    check = fields.Boolean('check', invisible=1)

    # def check_category(self):
    #     for rec in self:
    #         if rec.payment_category_id:
    #             if rec.payment_category_id.name == 'Assets Payment' or rec.payment_category_id.name == 'Assets Payment Refund':
    #                 rec.check = True

    @api.onchange('payment_category_id')
    def check_category(self):
        for rec in self:
            rec.check = False
            if rec.payment_category_id:
                if rec.payment_category_id.name == 'Assets Payment' or rec.payment_category_id.name == 'Assets Payment Refund':
                    rec.check = True
                else:
                    rec.check = False
