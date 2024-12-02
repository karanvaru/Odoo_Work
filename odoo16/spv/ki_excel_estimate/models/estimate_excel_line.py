from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EstimateExcelLine(models.Model):
    _name = 'estimate.excel.line'

    data = fields.Float(
        string='Data'
    )
    cell = fields.Char(
        string='Cell'
    )
    estimate_excel_id = fields.Many2one(
        'estimate.excel'
    )

    @api.model
    def create(self, vals_list):
        self._check_unique_cell(vals_list['estimate_excel_id'], vals_list['cell'])
        return super(EstimateExcelLine, self).create(vals_list)

    def write(self, vals):
        if 'cell' in vals:
            self._check_unique_cell(self.estimate_excel_id.id, vals['cell'])
        return super(EstimateExcelLine, self).write(vals)

    def _check_unique_cell(self, estimate_excel_id, cell):
        estimate = self.search([('estimate_excel_id', '=', estimate_excel_id), ('cell', '=', cell)])
        if estimate:
            raise UserError(_('Cell Number Must Be Unique For Each Value!'))
