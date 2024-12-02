from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    gstin_live = fields.Char("GSTIN(Live)", tracking=2)
    user_name_live = fields.Char("User Name(Live)", tracking=2)
    ewb_password_live = fields.Char("Ewb Password(Live)", tracking=2)
    registered_name = fields.Char("Registered Name", tracking=2)
