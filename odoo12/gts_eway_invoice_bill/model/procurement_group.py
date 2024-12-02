from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
