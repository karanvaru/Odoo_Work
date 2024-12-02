from odoo import models, fields, api


class ContractReportTemplate(models.Model):
    _name = 'contract.report.template'

    name = fields.Char(
        string='Name',
        required=True
    )

    description = fields.Html(
        string="Description",
        required=True
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
        string="Company",
    )

