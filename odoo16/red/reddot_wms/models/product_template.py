from odoo import api, fields, models





class ProductFamily(models.Model):
    _name = 'product.family'
    _description = 'Product Family'

    name = fields.Char(string="Family", required=True, index='trigram', Tracking=True)



class ProductGroup(models.Model):
    _name = 'product.group'
    _description = 'Product Group'

    name = fields.Char(string="Product Group", required=True, index='trigram', Tracking=True)

class CategoriesProducts(models.Model):
    _name = "product.cat"
    _description = " Reddot Product Categories"
    _inherit = ['mail.thread']

    name = fields.Char(string='Category', required=True, index='trigram', translate=True)


class ModelProducts(models.Model):
    _name = "product.model"
    _description = " Reddot Product Models"
    _inherit = ['mail.thread']

    name = fields.Char(string='Model', required=True, index='trigram', translate=True)


class CategoriesProducts(models.Model):
    _name = "product.line"
    _description = " Reddot Product Lines"
    _inherit = ['mail.thread']

    name = fields.Char(string='Product Line', required=True, index='trigram', translate=True)


class ReddotProductTemplate(models.Model):
    _inherit = "product.template"

    category = fields.Many2one('product.cat', string='Category')
    models = fields.Many2one('product.model', string='Models')
    product_line = fields.Many2one('product.line', string='Product Line')
    product_family_id = fields.Many2one('product.family', string='Product Family')
    product_group_id = fields.Many2one('product.group', string='Product Group')

