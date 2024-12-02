from odoo import fields, models, api


class ProductTagCategory(models.Model):
    _name = 'product.tag.category'
    _description = 'Product Tags Category'

    name = fields.Char(
        string='Name',
        required=True
    )
    sequence = fields.Integer(
        string='Sequence',
    )
    product_tag_categ_ids = fields.One2many('product.tag', 'product_tag_categ_id','Product Category Tags')


    @api.model
    def action_prepare_question(self):
        tag_ids = self.search([])
        vals = {
            'tag_ids': tag_ids
        }
        html = self.env['ir.ui.view']._render_template("cue_website.prepare_question",values=vals)
        return html

    @api.model
    def action_question_result(self, formData):
        formDataObject = []
        tags = self.env['product.tag']
        for Data in formData:
            name = self.browse(int(Data.get('name')))
            value = self.env['product.tag'].browse(int(Data.get('value')))
            tags += value
            formDataObject.append({'tag_id': name, 'category_id': value})
#         products = self.env['product.product'].sudo().search([('product_tag_ids', 'in', tags.ids)])
        products_mapping = self.env['product.tag.mapping'].sudo().search([])

        mapping_record = self.env['product.tag.mapping'].sudo()
        for map_rec in products_mapping:
            if map_rec.tag_ids.ids == tags.ids:
                mapping_record = map_rec
                break

        products = mapping_record.mapped('product_id')
        vals = {
            'formDataObject': formDataObject,
            'products': products
        }
        html = self.env['ir.ui.view']._render_template("cue_website.prepare_result",values=vals)
        return html


class ProductTagMapping(models.Model):
    _name = 'product.tag.mapping'
    _description = 'Product Tag Mapping'

    product_id = fields.Many2one(
        'product.product',
        required=True,
        string='Product'
    )
    tag_ids = fields.Many2many(
        'product.tag',
        required=True,
        string='Product tags'
    )
