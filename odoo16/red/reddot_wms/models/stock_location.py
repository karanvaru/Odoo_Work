from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMoveInherit(models.Model):
    _inherit = 'stock.location'
    _description = 'Reddot Stock Location'

    location_sellable_status = fields.Boolean('Sellable')
    project_id = fields.Many2one('project.project', string='RDD Project')
    business_type = fields.Selection([
        ('', 'select business type'),
        ('BTB', 'Back 2 Back'),
        ('RR', 'Run Rate'),
        ('BSPK', 'Bespoke')
    ], string="Business Type")

