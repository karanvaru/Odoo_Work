from odoo import fields,models,api,_
from datetime import datetime, timedelta,date


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    confirmation_date = fields.Datetime(string="Confirmation Date", related="order_id.confirmation_date", store=True)
    main_product_id = fields.Many2one('product.template', string="Main Product", related="product_id.product_tmpl_id", store=True)
    product_category_id = fields.Many2one('product.category', string="Product Category", related="product_id.categ_id", store=True)
    sales_team_id = fields.Many2one('crm.team', related="order_id.team_id", string="Sale Team", store=True)