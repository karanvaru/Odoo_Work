from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    usd_currency_id = fields.Many2one('res.currency', string='USD Currency')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    usd_currency_id = fields.Many2one(related='pos_config_id.usd_currency_id', string='USD Currency', readonly=False)


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        res["search_params"]["fields"].append("customer_passport_number")
#         res["search_params"]["fields"].append("staying_at")
        return res
