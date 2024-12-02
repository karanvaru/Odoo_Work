from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')], string='Shipping Policy',
        # default='one',
        help="It specifies goods to be deliver partially or all at once")

    @api.model
    def default_get(self, fields):
        rec = super(ResConfigSettings, self).default_get(fields)
        rec.update({
            'move_type': 'one',
        })
        return rec

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        type = ICPSudo.get_param('mt_order_delivery_manual.move_type')
        res.update(
            move_type=type)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('mt_order_delivery_manual.move_type', self.move_type)
