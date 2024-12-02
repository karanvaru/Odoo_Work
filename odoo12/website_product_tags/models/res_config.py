# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class ResConfigSettings(models.TransientModel):
    _name = 'website.product.tags.setting'
    _inherit = 'res.config.settings'
    product_tags_limit = fields.Integer(string="Save Limit of Popular  Tags ", required=1,
                                        help='it\'s represent the Number of Tag you wish to show as Popular Tag', default=6)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            {
                'product_tags_limit':IrDefault.get('website.product.tags.setting', 'product_tags_limit') or 6,
            }
        )
        return res
        
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if self.product_tags_limit<=0:
            raise Warning(_('Tag limit should be positive.'))
        self.env['ir.default'].sudo().set(
            'website.product.tags.setting', 'product_tags_limit', self.product_tags_limit)
