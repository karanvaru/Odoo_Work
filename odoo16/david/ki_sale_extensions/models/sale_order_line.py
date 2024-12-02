from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.tools import format_datetime, formatLang


class Saleorderline(models.Model):
    _inherit = "sale.order.line"

    item_code = fields.Char(
        string="Item Code",
    )

    @api.onchange('product_template_id')
    def onchange_item_code(self):
        if self.product_template_id:
            if self.product_template_id.default_code:
                self.item_code = self.product_template_id.default_code
        else:
            self.item_code = ''

    @api.depends('product_id')
    def _compute_name(self):
        res = super()._compute_name()
        for rec in self:
            if rec.product_template_id.name:
                rec.name = rec.product_template_id.name
            else:
                rec.name = ''
        return res

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({
            'item_code': self.item_code
        })
        return res


# class Saleorder(models.Model):
#     _inherit = "sale.order"

