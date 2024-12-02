from odoo import api, fields, models, _


class QuoteExcelTemplate(models.Model):
    _name = "quote.excel.template"

    file = fields.Binary(
        string='File',
        required=True,

    )
    file_char = fields.Char(
        string='File'
    )
    line_ids = fields.One2many(
        "quote.excel.template.line",
        "quote_excel_template_id",
    )


class QuoteExcelTemplateLine(models.Model):
    _name = "quote.excel.template.line"

    field_id = fields.Many2one(
        'ir.model.fields',
        domain="[('model_id.model', 'in', ['sale.order','res.partner','sale.order.line'])]",
        string="Fields",
    )

    cell = fields.Char(
        string='Cell'
    )
    sheet_number = fields.Integer(
        string='Sheet Number',
        default=1
    )

    quote_excel_template_id = fields.Many2one(
        'quote.excel.template',
        string="Template",
    )
