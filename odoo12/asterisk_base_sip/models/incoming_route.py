from odoo import fields, models, api, _
from odoo.addons.asterisk_base.utils import remove_empty_lines


class IncomingRoute(models.Model):
    _name = 'asterisk_base_sip.incoming_route'
    _description = "Incoming route"

    name = fields.Char(required=True)
