# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _


class WebkulWebsiteAddons(models.TransientModel):
    _inherit = 'webkul.website.addons'

    @api.multi
    def get_configuration_view(self):
        stock_config_ids = self.env['website.stock.config.settings'].search([])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('website_stock.action_website_stock_configuration')
        list_view_id = imd.xmlid_to_res_id('website_stock.view_wk_website_config_settings_tree')
        form_view_id = imd.xmlid_to_res_id('website_stock.view_wk_website_config_settings')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(stock_config_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = stock_config_ids[0].id
        return result

# Responsible Developer:- Sunny Kumar Yadav #