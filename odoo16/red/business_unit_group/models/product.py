from odoo import _, api, fields, models



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bu_id = fields.Many2one('business.unit', string='BU')




class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    bu_id = fields.Many2one('business.unit', string='BU')





class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bu_id = fields.Many2one('business.unit', related='product_id.bu_id', store=True)





class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    bu_ids = fields.Many2many('business.unit', string='BUs')
