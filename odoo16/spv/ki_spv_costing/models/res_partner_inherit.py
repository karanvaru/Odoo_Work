from odoo import api, fields, models, _


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    custom_partner_type = fields.Selection([
        ('distributor', 'Distributor'),
        ('chanel_partner', 'Chanel Partner')],
        string="Partner Type"
    )
    # is_distributor = fields.Boolean("Distributor")
    is_panel_distributor = fields.Boolean("Panel Distributor")
    panel_rent = fields.Float("Panel Rent")
