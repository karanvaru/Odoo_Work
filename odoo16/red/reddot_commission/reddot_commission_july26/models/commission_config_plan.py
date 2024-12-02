from odoo import models, fields, api


class CommissionDivisionLevel(models.Model):
    _name = 'commission.division.level'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Commission Division Level'
    _rec_name = "division_level"

    division_level = fields.Selection(
        selection=[
            ('company_wise', 'Company Wise'),
            ('bu_wise', 'BU Wise'),
            ('country_wise', 'Country Wise'),
            ('all', 'All'),
        ],
        string='Division Level',
        required=True,
        tracking=1,
    )
    calculation_types = fields.Selection(
        selection=[
            ('bu_level', 'Bu Level'),
            ('company_level', 'Company Level'),
            ('region_level', 'Region Level'),
            ('bu_group_level', 'Bu Group Level'),
            ('self', 'Self'),
        ],
        string='Calculation Type',
        required=False,
        tracking=1,
    )


class CommissionConfigPlan(models.Model):
    _name = 'commission.config.plan'
    _description = 'Commission Config Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Name',
        required=True,
    )
    calculation_types = fields.Selection(
        selection=[
            ('bu_level', 'Bu Level'),
            ('company_level', 'Company Level'),
            ('region_level', 'Region Level'),
            ('bu_group_level', 'Bu Group Level'),
            ('self', 'Self'),
        ],
        string='Calculation Type',
        required=True,
        tracking=1,
        default="bu_level"
    )
    commission_type = fields.Selection(
        selection=[
            ('gp', 'GP(Gross Profit)'),
            ('customer_invoice', 'Customer Invoice'),
        ],
        string='Commission Type',
        required=True,
        tracking=1,
        default="customer_invoice"
    )
    plan_line_ids = fields.One2many(
        "commission.config.plan.line",
        'commission_config_plan_id',
        string="Plan Lines"
    )

#     
    plan_commission_target_percentage_ids = fields.One2many(
        "commission.target.percentage",
        'target_commission_config_plan_id',
        string="Commission based on target"
    )
    plan_commission_target_percentage_sheet_id = fields.Many2one(
        'commission.target.percentage.sheet',
        string="Thresold",
        copy=False,
    )


    @api.onchange('plan_commission_target_percentage_sheet_id')
    def onchange_plan_commission_target_percentage_sheet_id(self):
        line_list = []
        self.plan_commission_target_percentage_ids = [(5, 0, 0)]
        for rec in self.plan_commission_target_percentage_sheet_id.line_ids:
            line_dct = {}
            line_dct.update({
                'from_percentage': rec.from_percentage,
                'to_percentage': rec.to_percentage,
                'commission_percentage': rec.commission_percentage,
            })
            line_list.append((0, 0, line_dct))
        self.plan_commission_target_percentage_ids = line_list
        
        
        
class CommissionConfigPlanLine(models.Model):
    _name = 'commission.config.plan.line'
    _description = 'Commission Config Plan Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one(
        'res.company',
        string="Company",
    )
    business_unit_id = fields.Many2one(
        'business.unit',
        string='Business Unit',
    )
    bu_group_id = fields.Many2one(
        'business.unit.group',
        string="BU Group",
    )
    country_group_id = fields.Many2one(
        'res.country.group',
        string='Country Group',
    )
    division_level_id = fields.Many2one(
        'commission.division.level',
        string='Division Level ID',
        required=False,
        tracking=1,
    )
    division_level = fields.Selection(
        selection=[
            #             ('company_wise', 'Company Wise'),
            ('bu_wise', 'BU Wise'),
            ('all', 'All'),
        ],
        string='Division Level',
        required=False,
        tracking=1,
    )
    division_type = fields.Selection(
        selection=[
            ('equally', 'Equally'),
            ('manually', 'Manually'),
            ('all', 'All'),
        ],
        string='Division Of Target',
        required=True,
        tracking=1,
    )
    commission_division_type = fields.Selection(
        selection=[
            ('equally', 'Equally'),
            ('manually', 'Manually'),
        ],
        string='Division Of Commission Percentage',
        tracking=1,
    )
    description = fields.Text(
        string="Description",
        readonly=True,
    )

    commission_config_plan_id = fields.Many2one(
        'commission.config.plan',
        string="Commission Plan"
    )
