from odoo import models, fields, api


class CommissionExceptionWizardRevenueLine(models.TransientModel):
    _name = 'commission.exception.wizard.revenue.line'
    _description = "Commission Exception Revenue Line"

    line_id = fields.Many2one(
        'commission.structure.line',
        string='Commission Structure',
    )

    is_exception = fields.Boolean(
        string="Exception?",
    )

    exception_reason = fields.Text(
        string="Reason"
    )

    revenue_wizard_target_archived = fields.Float(
        string="Commission Archived"
    )
    commission_to_be = fields.Float(
        string="Commission To Be"
    )

    revenue_commission_structure_exception_reason_wizard_id = fields.Many2one(
        'commission.structure.exception.reason.wizard',
        string='Revenue Commission',
    )
