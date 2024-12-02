# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _product_review(self, review_array, product_template_id):
        vals = {}
        partner_obj = self.env["res.users"].sudo().browse(self._uid)
        if partner_obj:
            vals['partner_id'] = partner_obj.partner_id.id
        if review_array.get('title'):
            vals['title'] = review_array['title']
        if review_array.get('msg'):
            vals['msg'] = review_array['msg']
        if review_array.get('contact_name'):
            vals['customer'] = review_array['contact_name']
        if review_array.get('email'):
            vals['email'] = review_array['email']
        if review_array.get('stars'):
            vals['rating'] = int(review_array['stars'])
        vals['template_id'] = product_template_id
        review_id = self.env['user.review'].sudo().create(vals)
        return review_id
