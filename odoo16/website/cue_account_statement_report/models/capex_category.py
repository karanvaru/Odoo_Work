from odoo import models, api, fields, _


class CapexCategory(models.Model):
    _name = "capex.category"

    name = fields.Char(
        string='Name',
        required=True,
    )
    report_head_type = fields.Selection(
        selection=[
            ('variable_cost', 'Variable Cost'),
            ('overhead_cost', 'Overhead Cost'),
            ('capex', 'Capex'),
            ('direct_cost', 'Direct Cost'),
            ('wages_cost', 'Wages Cost'),
        ],
        copy=False
    )
    sequence = fields.Integer(
        string="Sequence",
        default=1
    )
    department_id = fields.Many2one(
        'hr.department',
        string="Department"
    )