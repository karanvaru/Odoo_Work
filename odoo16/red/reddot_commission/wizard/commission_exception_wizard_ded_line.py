from odoo import models, fields, api


class CommissionExceptionWizardDedLine(models.TransientModel):
    _name = 'commission.exception.wizard.ded.line'
    _description = "Commission Exception ded Line"

    line_id = fields.Many2one(
        'commission.structure.deduction.line',
        string='Commission Structure Deduction Line',
    )

    is_exception = fields.Boolean(
        string="Exception?",
    )

    exception_reason = fields.Text(
        string="Reason"
    )
    manager_result = fields.Selection(
        selection=[
            ('todo', 'Todo'),
            ('pass', 'Pass'),
            ('fail', 'Fail'),
        ],
    )

    manager_result_to_be = fields.Selection(
        selection=[
            ('todo', 'Todo'),
            ('pass', 'Pass'),
            ('fail', 'Fail'),
        ],
        default="todo",
    )

    kpi_commission_structure_exception_reason_wizard_id = fields.Many2one(
        'commission.structure.exception.reason.wizard',
        string='Kpi Commission',
    )