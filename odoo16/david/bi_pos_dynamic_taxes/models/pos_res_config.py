# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pos_modify_taxes_line = fields.Boolean(related='pos_config_id.modify_taxes_line', readonly=False)
	pos_taxes_ids = fields.Many2many(related='pos_config_id.taxes_ids', readonly=False,
											  string='Select Dynamic Taxes')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: