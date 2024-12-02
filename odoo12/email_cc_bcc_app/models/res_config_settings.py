# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from distutils.command.install import install


class ResConfigSettings(models.TransientModel):	
    _inherit = 'res.config.settings'

    partner_cc_ids = fields.Many2many('res.partner', 'res_config_cc_partner_rel', 'config_id', 'partner_id', string="Default CC")
    partner_bcc_ids = fields.Many2many('res.partner', 'res_config_bcc_partner_rel', 'config_id', 'partner_id', string="Default BCC")

    cc_visible = fields.Boolean(string="Enable Email CC", default=True)
    bcc_visible = fields.Boolean('Enable Email BCC')

    @api.model
    def default_get(self, fields):
        settings = super(ResConfigSettings, self).default_get(fields)
        settings.update(self.get_email_ccbcc_config(fields))
        return settings
# 
    @api.model
    def get_email_ccbcc_config(self, fields):
        res_config = \
                    self.env.ref('email_cc_bcc_app.res_config_email_ccbcc_data1')
        return {
            'partner_cc_ids': [(6, 0, res_config.partner_cc_ids.ids)],
            'partner_bcc_ids': [(6, 0, res_config.partner_bcc_ids.ids)],
            'cc_visible': res_config.cc_visible,
            'bcc_visible': res_config.bcc_visible,
        }
# 
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        res_config = \
                    self.env.ref('email_cc_bcc_app.res_config_email_ccbcc_data1')
        vals = {
            'partner_cc_ids': [(6, 0, self.partner_cc_ids.ids)],
            'partner_bcc_ids': [(6, 0, self.partner_bcc_ids.ids)],
            'cc_visible': self.cc_visible,
            'bcc_visible': self.bcc_visible,
        }
        res_config.write(vals)


class ResConfigEmailCCBCC(models.Model):
    _name = 'res.config.email.ccbcc'
    _description = 'Email CC And Bcc Configuration'

    partner_cc_ids = fields.Many2many('res.partner', 'res_config_email_cc_partner_rel', 'config_id', 'partner_id', string="Default CC")
    partner_bcc_ids = fields.Many2many('res.partner', 'res_config_email_bcc_partner_rel', 'config_id', 'partner_id', string="Default BCC")
    cc_visible = fields.Boolean(string="Enable Email CC", default=True)
    bcc_visible = fields.Boolean('Enable Email BCC')


