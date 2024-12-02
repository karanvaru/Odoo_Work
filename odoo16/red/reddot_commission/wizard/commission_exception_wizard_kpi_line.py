from odoo import models, fields, api


class CommissionExceptionWizardKpiLine(models.TransientModel):
    _name = 'commission.exception.wizard.kpi.line'
    _description = "Commission Exception kpi Line"

    line_id = fields.Many2one(
        'commission.structure.kpi.line',
        string='Commission Structure KPI Line',
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