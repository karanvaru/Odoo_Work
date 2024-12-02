from odoo import models, fields, api

class SaleShopLog(models.Model):
    _name = 'shop.fail.log'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Failed Import/Export Log"
    _order = "id desc"

    name = fields.Char(string='Name')
    shop_id = fields.Many2one('sale.shop')
    log_lines = fields.One2many('shop.fail.log.lines', 'shop_log_id')
    operation = fields.Selection([('import_products', 'Import Products'),
                                  ('import_retrun', 'Import Return'),
                                  ('import_sales_order', 'Import Sales Order'),
                                  ('import_AWB', 'Import AWB'),
                                  ('import_payment_settlement', 'Payment Settlement'),], string='Operation',
                                 required=True)
    @api.model
    def create(self,vals):
        name = self.env["ir.sequence"].next_by_code("shop.fail.log")
        vals.update({'name' : name})
        return super(SaleShopLog,self).create(vals)
class SaleShopLogLines(models.Model):
    _name = 'shop.fail.log.lines'
    _description = "Failed Import/Export Log Lines"
    _order = "id desc"

    operation = fields.Selection([('import_products', 'Import Products'),
                                  ('import_return', 'Import Return'),
                                  ('import_sales_order', 'Import Sales Order'),
                                  ('import_AWB', 'Import AWB'),
                                  ('import_payment_settlement', 'Payment Settlement'),], string='Operation', required=True)
    message = fields.Char()
    is_mismatch = fields.Boolean()
    shop_log_id = fields.Many2one('shop.fail.log')
