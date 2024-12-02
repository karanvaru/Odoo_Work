from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class TargetCommissionPercentage(models.Model):
    _name = 'commission.target.percentage'
    _description = 'Commission Target Percentage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    from_percentage = fields.Float(
        string="From(%)"
    )
    to_percentage = fields.Float(
        string="To(%)"
    )
    commission_percentage = fields.Float(
        string="Commission(%)"
    )
    commission_target_percentage_sheet_id = fields.Many2one(
        'commission.target.percentage.sheet',
        string="Commission Target Percentage Sheet",
        copy=False,
    )
    target_commission_config_plan_id = fields.Many2one(
        'commission.config.plan',
        string="Commission Config Plan",
        copy=False,
    )


class CommissionRule(models.Model):
    _name = 'commission.rule'
    _description = 'Commission Rules'
    # _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
# 
#     department_ids = fields.Many2many(
#         'hr.department',
#         string='Department',
#         copy=False
#     )
#     employee_ids = fields.Many2many(
#         'hr.employee',
#         string='Department',
#         copy=False
#     )
    period_type = fields.Selection(
        selection=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
 
        ],
        string='Period Type',
        tracking=1,
    )
    term_condition_id = fields.Many2one(
        'commission.term.condition',
        string='Term And Condition',
    )
# 
    date_start = fields.Date(
        string="Date From"
    )
    date_end = fields.Date(
        string="Date To"
    )
