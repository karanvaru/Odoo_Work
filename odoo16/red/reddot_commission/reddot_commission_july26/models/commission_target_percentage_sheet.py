from odoo import models, fields, api


class CommissionTargetPercentageSheet(models.Model):
    _name = 'commission.target.percentage.sheet'
    _description="Thresold Template"

    name = fields.Char(
        'Name',
        required=True
    )
    line_ids = fields.One2many(
        "commission.target.percentage",
        'commission_target_percentage_sheet_id',
        string="Bu Company Target Allocation"
    )
