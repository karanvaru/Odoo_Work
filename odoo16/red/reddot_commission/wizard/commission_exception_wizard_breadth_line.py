from odoo import models, fields, api


class CommissionExceptionWizardBreadthLine(models.TransientModel):
    _name = 'commission.exception.wizard.breadth.line'
    _description = "Commission Exception Breadth Line"

    line_id = fields.Many2one(
        'commission.structure.line',
        string='Commission Structure',
    )

    is_exception = fields.Boolean(
        string="Exception?",
    )
    breadth_wizard_target_archived = fields.Float(
        string="Commission Archived"
    )
    commission_to_be = fields.Float(
        string="Commission To Be"
    )
    exception_reason = fields.Text(
        string="Reason"
    )
    breadth_commission_structure_exception_reason_wizard_id = fields.Many2one(
        'commission.structure.exception.reason.wizard',
        string='Breadth Commission',
    )