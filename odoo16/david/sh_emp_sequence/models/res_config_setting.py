# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_auto_create = fields.Boolean(
        "Auto Create Employee No.")


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_auto_create = fields.Boolean(
        string="Auto Create Employee No.",
        related='company_id.sh_auto_create',
        readonly=False
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        sh_auto_create = self.env['ir.config_parameter'].sudo().get_param('sh_auto_create')

        res.update(
            sh_auto_create=sh_auto_create,
        )
        return res

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('sh_auto_create', self.sh_auto_create)
        return res
