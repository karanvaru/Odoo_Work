from odoo import api, fields, models, _


class CostSheetTemplate(models.Model):
    _name = "cost.sheet.template"

    name = fields.Char("Name", required=True)
    line_ids = fields.One2many("cost.sheet.template.line", "cost_sheet_template_id", string="Lines")


class CostSheetTemplateLine(models.Model):
    _name = "cost.sheet.template.line"

    cost_sheet_template_id = fields.Many2one("cost.sheet.template", string="Template")
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float("Quantity")
