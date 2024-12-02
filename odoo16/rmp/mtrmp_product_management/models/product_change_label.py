from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_code = fields.Char(string="Master SKU")

    # FIXME : Already available same in the base
    # company_id = fields.Many2one('res.company', 'Company', index=1, # default=lambda self: self.env.company)

    # Purchase Order line

    last_purchase_line_id = fields.Many2one('purchase.order.line', string="Last Purchase", readonly=1)
    last_purchase_order_id = fields.Many2one('purchase.order', string="Last Purchase Order", related='last_purchase_line_id.order_id')
    last_purchase_qty = fields.Float(string="Last Purchase Quantity", related="last_purchase_line_id.product_qty")
    last_purchase_amount = fields.Float(string="Last Purchase Price", related="last_purchase_line_id.price_unit")
    last_purchase_date = fields.Datetime(string="Last Purchase Date", related="last_purchase_line_id.order_id.date_approve")
    last_partner_id = fields.Many2one( 'res.partner', string="Last Supplier", related='last_purchase_line_id.order_id.partner_id')
    last_purchse_prodcuct_id = fields.Text(string="Lase Purchase prodcut",related='last_purchase_line_id.name')

    # Product Group
    product_group_id = fields.Many2one('product.group', string="Group")

    # Critical Stock
    min_qty = fields.Float(string="Min Quantity")

    # Shipping Mode
    default_shipping_mode = fields.Selection([('air', 'Air'), ('Surface', 'Surface')], string='Shipping Mode')

    # Package Type Fields
    default_package_type_id = fields.Many2one('stock.package.type', string="Package Type")
    default_package_type_packaging_length = fields.Integer(string="Length", readonly=True, related='default_package_type_id.packaging_length')
    default_package_type_packaging_height = fields.Integer(string="Height", readonly=True, related='default_package_type_id.height')

    #
    country_id = fields.Many2one('res.country', string="Country", default=lambda self: self.env['res.country'].search([('code', '=', 'IN')], limit=1))

    # @api.constrains('name')
    # def default_code_constraint(self):
    #     for record in self:
    #         if record.name:
    #             exist_code = self.search([
    #                 ('name', '=', record.name),
    #                 ('id', '!=', record.id),
    #             ])
    #             if exist_code:
    #                 raise ValidationError(_("Master Product Name must be uniq!"))


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char(string="Master SKU")

    # Purchase Order line
    last_purchase_line_id = fields.Many2one('purchase.order.line', string="Last Purchase", readonly=1)
    last_purchase_order_id = fields.Many2one('purchase.order', string="Last Purchase Order", related='last_purchase_line_id.order_id')
    last_purchase_qty = fields.Float(string="Quantity", related="last_purchase_line_id.product_qty")
    last_purchase_amount = fields.Float(string="Price", related="last_purchase_line_id.price_unit")
    last_purchase_date = fields.Datetime(string="Purchase Date", related="last_purchase_line_id.order_id.date_approve")
    last_partner_id = fields.Many2one('res.partner', string="Last Supplier", related='last_purchase_line_id.order_id.partner_id')
    last_purchse_prodcuct_id = fields.Text(string="Lase Purchase prodcut", related='last_purchase_line_id.name')

    # Critical Stock
    min_qty = fields.Float(string="Min Quantity", related='product_tmpl_id.min_qty')
    is_quantity = fields.Boolean(default=False, compute="_compute_is_quantity", store=True)

    country_id = fields.Many2one('res.country', string="Country", related="product_tmpl_id.country_id")

    @api.depends("min_qty", "virtual_available")
    def _compute_is_quantity(self):
        for rec in self:
            if rec.virtual_available <= rec.min_qty:
                rec.is_quantity = True
            else:
                rec.is_quantity = False
