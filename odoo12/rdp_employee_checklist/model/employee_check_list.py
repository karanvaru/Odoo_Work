from odoo import models,fields

class EmployeeCheckList(models.Model):

    _inherit = 'hr.employee'


    color = fields.Char(string='color')

    shirt_size = fields.Selection(
        [('s', 'S'), ('m', 'M'), ('l', 'L'),('xl', 'Xl')],)
    waist_size = fields.Selection(
        [('28', '28'), ('30', '30'), ('32', '32'),('etc', 'etc')],)
    t_shirt_size = fields.Selection(
        [('s', 'S'), ('m', 'M'), ('l', 'L'),('xl', 'XL'),('xxl', 'XXL')],)