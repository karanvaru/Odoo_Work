from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
from datetime import datetime,date,timedelta
from odoo.tools import float_compare

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order MO", track_visibility = "always")
