# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning

import logging
_log = logging.getLogger(__name__)


class WebkulWebsiteAddons(models.TransientModel):
    _inherit = 'webkul.website.addons'

    # Order
    module_website_preorder = fields.Boolean(string="Website Pre-Order")

    @api.multi
    def get_pre_order_configuration_setting(self):
        _log.info("********************************")
        ids = self.env['website.preorder.config.settings'].sudo().search([])
        _log.info("********************************")
        imd = self.env['ir.model.data'].sudo()
        _log.info("********************************")
        action = imd.xmlid_to_object(
            'website_preorder.action_website_preorder_configuration')
        list_view_id = imd.xmlid_to_res_id(
            'website_preorder.view_wk_website_preorder_config_settings_tree')
        form_view_id = imd.xmlid_to_res_id(
            'website_preorder.view_wk_website_preorder_config_settings')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(ids) < 2:
            result['views'] = [(form_view_id, 'form'), (list_view_id, 'tree')]
            if len(ids) == 1:
                result['res_id'] = ids.ids[0]
        _log.info("*********result*********%r**************",result)
        return result
