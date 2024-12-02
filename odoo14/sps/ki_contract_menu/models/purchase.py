from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'


