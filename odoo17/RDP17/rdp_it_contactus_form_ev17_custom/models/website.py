from odoo import models, fields, api

class Website(models.Model):
    _inherit = 'website'

    recaptcha_sitekey = fields.Char()
    recaptcha_secretkey = fields.Char()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recaptcha_sitekey = fields.Char(
        string="Recaptcha Site Key",
        related='website_id.recaptcha_sitekey',
        readonly=False,
        )
    recaptcha_secretkey = fields.Char(
        string="Recaptcha Secret Key",
        related='website_id.recaptcha_secretkey',
        readonly=False,
        )
