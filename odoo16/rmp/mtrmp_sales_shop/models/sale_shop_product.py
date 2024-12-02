from odoo import models, fields, api, _
from odoo.tools import float_repr, html2plaintext
from odoo.exceptions import ValidationError


class SaleShopProduct(models.Model):
    _name = 'sale.shop.product'
    _description = "Shop Product"
    # _sql_constraints = [
    #
    #     ('default_code_unique', 'unique (default_code)', 'SKU code is already exists...!')
    #
    # ]

    name = fields.Char(string="Name",
                       # required=True,
                       # related='product_id.name'
                       )
    product_id = fields.Many2one('product.product', string="Base Product", required=True)
    product_tmpl_id = fields.Many2one('product.template', string="Base Product TMPL",
                                      related='product_id.product_tmpl_id')
    shop_id = fields.Many2one('sale.shop', string="Shop", required=True)
    default_code = fields.Char(string="Shop SKU")
    list_price = fields.Float(string="Sales Price")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", related='product_tmpl_id.uom_id')
    active = fields.Boolean(string="Active", default=True)
    shop_categ_id = fields.Many2one('product.category', string="Base product Category",
                                    related='product_tmpl_id.categ_id')
    is_published = fields.Boolean(string="Published/UnPublish")
    publish_date = fields.Date(string="Published On")
    last_sale_order_line_id = fields.Many2one('sale.order.line', string="Last Order Lines", readonly=1)
    last_sale_order_id = fields.Many2one('sale.order', string="Last Order", readonly=1)
    last_sale_order_date = fields.Datetime(string="Last Order Date", related='last_sale_order_id.date_order')
    last_sale_order_line_qty = fields.Float(string="Last Order qty", related='last_sale_order_line_id.product_uom_qty')
    description = fields.Text(string="Description")
    size = fields.Char(string="Size")
    l10n_in_hsn_code = fields.Char(string="HSN Code")

    country_id = fields.Many2one('res.country', string="Country",related="product_id.country_id"
        # default=lambda self: self.env['res.country'].search([('code', '=', 'IN')], limit=1)
    )
    company_id = fields.Many2one('res.company', string="Company")
    taxes_id = fields.Many2many('account.tax', string="GST")
    product_public_category_id = fields.Many2one('product.public.category', string="Channel Product Category")
    product_category = fields.Text(string="Channel Category Description", readonly=True)
    master_code = fields.Char('Master SKU')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                # rec.name = rec.product_id.name
                rec.list_price = rec.product_id.list_price
                rec.description = html2plaintext(rec.product_id.description)
                rec.uom_id = rec.product_id.uom_id.id
                rec.country_id = rec.product_id.country_id.id


    def publish_product(self):

        for rec in self:
            rec.is_published = True
            rec.publish_date = fields.Date.today()

    def unpublish_product(self):
        for rec in self:
            rec.is_published = False

