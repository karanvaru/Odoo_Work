from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    gst_no = fields.Char("GSTIN", tracking=2)
    user_name = fields.Char("User Name", tracking=2)
    user_password = fields.Char("Password", tracking=2)
    auth_token = fields.Char('Auth-Token', tracking=2)
    expire_date = fields.Datetime('Token Expiry Date', tracking=2)
    expire_date1 = fields.Char('Token Expiry Date1', tracking=2)


