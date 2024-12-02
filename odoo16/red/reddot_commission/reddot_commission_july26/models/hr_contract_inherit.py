import base64
from odoo import api, fields, models, _


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    commission_config_plan_id = fields.Many2one(
        'commission.config.plan',
        'Commission Plan',
        copy=False
    )
    hr_contract_commission_config_line_ids = fields.One2many(
        "hr.contract.commission.config.line",
        'hr_contract_id',
        string="Commission Configuration Lines"
    )
    commission_target_percentage_employee_ids = fields.One2many(
        "commission.target.percentage.employee",
        'target_percentage_hr_contract_id',
        string="Commission Percentage Target"
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
        tracking=1,
    )
    commission_type = fields.Selection(
        selection=[
            ('gp', 'GP(Gross Profit)'),
            ('customer_invoice', 'Customer Invoice'),
        ],
        string='Commission Type',
        tracking=True,
    )
    plan_target_amount = fields.Float(
        string="Target Amount",
        copy=False
    )
    plan_commission_amount = fields.Float(
        string="Commission Amount",
        copy=False
    )
    contract_state = fields.Selection(
        selection=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
        ],
        string='Contract State',
        tracking=True,
        copy=False
    )
    commission_term_condition_id = fields.Many2one(
        'commission.term.condition',
        'Term And Condition',
        copy=False
    )
  
    def action_send_mail(self):
        for rec in self:
            generated_report = self.env['ir.actions.report']._render_qweb_pdf(
                'reddot_commission.action_employee_contract_report', self.id)
            data_record = base64.b64encode(generated_report[0])
            ir_values = {
                'name': 'Commission_TC',
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
                'res_model': 'hr.contract',
            }
            report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
            email_template = self.env.ref('reddot_commission.employee_approval_structure')
            email_template.attachment_ids = [(4, report_attachment.id)]
            url = self.get_base_url() + "/contract_varification/%s" % (self.employee_id.id)
            ctx = {
                'url': url
            }
            email_template.with_context(ctx).send_mail(rec.id)
            email_template.attachment_ids = [(5, 0, 0)]

    def write(self, vals):
        super_res = super(ContractInherit, self).write(vals)
        if 'commission_config_plan_id' in vals:
            for record in self:
                record.onchange_commission_config_plan_id()
        return super_res

    @api.onchange('commission_config_plan_id')
    def onchange_commission_config_plan_id(self):
        self.update({
            'hr_contract_commission_config_line_ids': [(5, 0, 0)],
            'commission_target_percentage_employee_ids': [(5, 0, 0)],
        })
        plan_id = self.commission_config_plan_id

        hr_contract_commission_config_line_ids = []
        for rec in plan_id.plan_line_ids:
            line_dct = {}
            line_dct.update({
                'company_id': rec.company_id.id,
                'business_unit_id': rec.business_unit_id.id,
                'bu_group_id': rec.bu_group_id.id,
                'country_group_id': rec.country_group_id.id,
                'division_level': rec.division_level,
                'division_level_id': rec.division_level_id.id,
                'division_type': rec.division_type,
                'commission_division_type': rec.commission_division_type,
            })
            hr_contract_commission_config_line_ids.append((0, 0, line_dct))

        percentage_line_list = []
        for rec in plan_id.plan_commission_target_percentage_ids:
            line_dct = {}
            line_dct.update({
                'from_percentage': rec.from_percentage,
                'to_percentage': rec.to_percentage,
                'commission_percentage': rec.commission_percentage,
            })
            percentage_line_list.append((0, 0, line_dct))

        self.update({
            'calculation_types' :  plan_id.calculation_types,
            'commission_type' : plan_id.commission_type,
            'hr_contract_commission_config_line_ids': hr_contract_commission_config_line_ids,
            'commission_target_percentage_employee_ids': percentage_line_list
        })

    def set_calculation_type_value(self):
        calculation_type = {
            'bu_level': 'Bu Level',
            'company_level': 'Company Level',
            'region_level': 'Region Level',
            'bu_group_level': 'Bu Group Level',
            'self': 'Self',
        }
        return calculation_type

    def set_commission_type_value(self):
        commission_type = {
            'gp': 'GP(Gross Profit)',
            'customer_invoice': 'Customer Invoice',
        }
        return commission_type


class HrContractCommissionConfigLine(models.Model):
    _name = 'hr.contract.commission.config.line'
    _description = 'Contract Commission Config Line'
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
        related="division_level_id.division_level",
        string='Division Level',
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
    hr_contract_id = fields.Many2one(
        'hr.contract',
        string="Contract"
    )
    line_ids = fields.One2many(
        'hr.contract.commission.config.line.allocation',
        'parent_id',
        string="Lines"
    )
    target_description = fields.Text(
        string="Description"
    )
    target_amount = fields.Float(string="Target Amount")
    commission_amount = fields.Float(string="Commission Amount")


    def action_open_wizard(self):
        act = self.env.ref(
            "reddot_commission.action_commission_config_allocation_wizard"
        ).read([])[0]
        return act

class HrContractCommissionConfigLineAllocation(models.Model):
    _name = 'hr.contract.commission.config.line.allocation'
    _description = 'Contract Commission Config Line Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one(
        'res.company',
        string="Company",
    )
    business_unit_id = fields.Many2one(
        'business.unit',
        string='Business Unit',
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country Group',
    )
    target_amount = fields.Float(
        string="Target Amount"
    )
    commission_percentage = fields.Float(
        string="Commission (%)"
    )
    parent_id = fields.Many2one(
        'hr.contract.commission.config.line',
        string='Parent',
    )

    def name_get(self):
        result = []
        for line in self:
            name = ''
            if line.company_id:
                name = name + "Company :" + line.company_id.name
            elif line.business_unit_id:
                name = name + "BU :" + line.business_unit_id.name
            elif line.country_id:
                name = name + "Country :" + line.country_id.name
            
            name = name + "\nCommission : " + str(line.commission_percentage) + "%"
            name = name + "\nTarget : " + str(line.target_amount)
            result.append((line.id, name))
        return result

class TargetCommissionPercentageEmployee(models.Model):
    _name = 'commission.target.percentage.employee'
    _description = 'Commission Target Percentage Employee'

    from_percentage = fields.Float(
        string="From(%)"
    )
    to_percentage = fields.Float(
        string="To(%)"
    )
    commission_percentage = fields.Float(
        string="Commission(%)"
    )

    target_percentage_hr_contract_id = fields.Many2one(
        'hr.contract',
        string="Contract"
    )

