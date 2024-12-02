from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrContractCommissionConfigLineAllocationWizard(models.TransientModel):
    _name = 'commission.config.allocation.wizard'
    _description = 'Contract Commission Config Line Allocation Wizard'

    line_ids = fields.One2many(
        "commission.config.allocation.wizard.line",
        'parent_id',
        string="Allocation"
    )
    division_type = fields.Selection(
        selection=[
            ('equally', 'Equally'),
            ('manually', 'Manually'),
            ('all', 'All'),
        ],
        string='Division Of Target',
        required=True,
    )
    commission_division_type = fields.Selection(
        selection=[
            ('equally', 'Equally'),
            ('manually', 'Manually'),
        ],
        string='Division Of Commission Percentage',
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
    )
    division_level_id = fields.Many2one(
        'commission.division.level',
        string='Division Level ID',
        required=False,
    )
    division_level = fields.Selection(
        related="division_level_id.division_level"
    )

    def action_confirm(self):
        if self.commission_division_type == 'manually':
            commission_percentage_sum = sum(rec.commission_percentage for rec in self.line_ids)
            if commission_percentage_sum != 100:
                raise UserError(_("Commission Percentage Should Be 100..."))

        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model', False)
        active_record = self.env[active_model].browse(active_id)
        
        active_record.update({
            'line_ids': [(6, 0, [])],
        })
        lines = []
        
        for line in self.line_ids:
            commission_percentage = line.commission_percentage
            if self.commission_division_type == 'equally':
                commission_percentage = 100.0 / len(self.line_ids.ids)
                
            total_target_amount = 0
            target_amount = line.target_amount
            if self.division_type == 'equally':
                target_amount = active_record.target_amount  / len(self.line_ids.ids) 
            total_target_amount += target_amount


            vals = {
                'business_unit_id': line.business_unit_id.id,
                'company_id': line.company_id.id,
                'country_id': line.country_id.id,
                'target_amount': target_amount,
                'commission_percentage': commission_percentage
            }
            lines.append((0, 0, vals))

        active_record.update({
            'line_ids': lines
        })
        return  True
        
    @api.model
    def default_get(self, fields):
        super_res = super(
            HrContractCommissionConfigLineAllocationWizard, self
        ).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model', False)
        active_record = self.env[active_model].browse(active_id)

        line_ids = []
        for line in active_record.line_ids:
            line_ids.append((0, 0, {
                'company_id': line.company_id.id,
                'business_unit_id': line.business_unit_id.id,
                'country_id': line.country_id.id,
                'target_amount': line.target_amount,
                'commission_percentage': line.commission_percentage,
            }))

        super_res.update({
            'division_type': active_record.division_type,
            'commission_division_type': active_record.commission_division_type,
            'calculation_types': active_record.hr_contract_id.calculation_types,
            'division_level_id': active_record.division_level_id.id,
            'line_ids': line_ids
        })
        return super_res


class HrContractCommissionConfigLineAllocation(models.TransientModel):
    _name = 'commission.config.allocation.wizard.line'
    _description = 'Contract Commission Config Line Allocation Wizard'

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
        'commission.config.allocation.wizard',
        string='Parent',
    )
