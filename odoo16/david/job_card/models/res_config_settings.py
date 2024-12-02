# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_task_sequence_ignore = fields.Boolean(string="Task Sequence Ignore")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['custom_task_sequence_ignore'] = self.env['ir.config_parameter'].sudo().get_param('job_card.custom_task_sequence_ignore')
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('job_card.custom_task_sequence_ignore', self.custom_task_sequence_ignore or False)
        super(ResConfigSettings, self).set_values()