from odoo import fields, models, api

class ProductBrandInherit(models.Model):
    _inherit = 'product.brand'

    show_website = fields.Boolean(string="Show Website")

    out_of_box_visible = fields.Boolean(
        string="Out Of The Box Visible"
    )

    slider_type = fields.Selection([
        ('top', 'Top'),
        ('middle', 'Middle'),
        ('bottom', 'Bottom'),
        ], string='Slider Type'
    )
    redirect_url = fields.Char(
        string="URL",
        default="/"
    )
    product_category_ids = fields.Many2many(
        'product.category',
        string="Categories"
    )


    @api.model
    def prepare_out_of_box_list(self):
        upper_brand_ids = self.search([('out_of_box_visible', '=', True), ('slider_type', '=', 'top')])
        middle_brand_ids = self.search([('out_of_box_visible', '=', True), ('slider_type', '=', 'middle')])
        bottom_brand_ids = self.search([('out_of_box_visible', '=', True), ('slider_type', '=', 'bottom')])
        brands = {}
        
        for i in upper_brand_ids+middle_brand_ids+bottom_brand_ids:
            brands[i.id] = i.redirect_url
        
        return {
            'list': [upper_brand_ids.ids, middle_brand_ids.ids, bottom_brand_ids.ids],
            'brands': brands
        }
        