from odoo import fields, models

class StockRoute(models.Model):
    _inherit = 'stock.route'

    business_type = fields.Selection([
        ('BTB', 'Back 2 Back'),
        ('RR', 'Run Rate'),
        ('BSPK', 'Bespoke'),
        ('SAP', 'SAP TYPE')
    ], string="Business Type", help="Specify the business type for this route.")
