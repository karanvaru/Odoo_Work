from odoo import models, fields, api, _


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    report_head_type = fields.Selection(
        selection=[
            ('variable_cost', 'Variable Cost'),
            ('overhead_cost', 'Overhead Cost'),
            ('capex', 'Capex'),
        ],
        copy=False
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    report_head_type = fields.Selection(
        selection=[
            ('variable_cost', 'Variable Cost'),
            ('overhead_cost', 'Overhead Cost'),
            ('capex', 'Capex'),
            ('working_capital_in', 'Working Capital IN'),
            ('direct_cost', 'Direct Cost'),
        ],
        copy=False
    )
    report_revenue_type = fields.Selection(
        selection=[
            ('1_cue_bridge', 'Cue Bridge'),
            ('2_cue_bridge_max', 'Cue Bridge Max'),
            ('3_cue_bridge_plus', 'Cue Bridge Plus'),
            ('4_other', 'Other')
        ],
        copy=False
    )


class Partner(models.Model):
    _inherit = 'res.partner'

    report_head_type = fields.Selection(
        selection=[
            ('variable_cost', 'Variable Cost'),
            ('overhead_cost', 'Overhead Cost'),
            ('capex', 'Capex'),
            ('revenue', 'Revenue'),
            ('exclude_fs', 'Exclude From Fund Statement'),
            ('exclude_fs_revenue_in', 'Except Revenue Exclude From Fund Statement'),
        ],
        copy=False
    )
#     capex_category_id = fields.Many2one(
#         'capex.category',
#         string='Capex Category'
#     )


class ProductCategory(models.Model):
    _inherit = 'product.category'

    report_head_type = fields.Selection(
        selection=[
            ('variable_cost', 'Variable Cost'),
            ('overhead_cost', 'Overhead Cost'),
            ('capex', 'Capex')
        ],
        copy=False
    )