from odoo import fields, models


class SaleDocumentTypes(models.Model):
    _name = "sale.document.types"

    name = fields.Char(
        string="Name",
        required=True
    )
    code = fields.Char(
        string="Code",
        required=True
    )
