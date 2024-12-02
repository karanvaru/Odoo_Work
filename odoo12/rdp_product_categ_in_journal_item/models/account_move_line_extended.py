from odoo import models,fields,api,_

class AccountMoveLineExtended(models.Model):
    _inherit = 'account.move.line'

    product_categ = fields.Many2one('product.category', string="Product Category", compute="compute_product_categ", store=True)

    @api.depends('product_id')
    def compute_product_categ(self):
        for rec in self:
            if rec.product_id.categ_id:
                rec.product_categ = rec.product_id.categ_id.id
            