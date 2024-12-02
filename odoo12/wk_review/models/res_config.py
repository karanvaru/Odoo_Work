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
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class WebsiteReviewConfig(models.TransientModel):
    _name = 'website.review.config'
    _inherit = 'res.config.settings'

    review_no = fields.Integer(
        string="No. of Reviews", help="Set default numbers of review to show on website.")
    auto_publish = fields.Boolean(
        string="Auto Publish Review", help="Publish user's review automatically.")
    message_when_unpublish = fields.Text(string="Message", default=False)

    @api.multi
    def set_values(self):
        super(WebsiteReviewConfig, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('website.review.config', 'auto_publish', self.auto_publish or False)
        IrDefault.set('website.review.config', 'review_no', self.review_no)
        IrDefault.set('website.review.config', 'message_when_unpublish', self.message_when_unpublish)
        return True

    @api.model
    def get_values(self, fields=None):
        res = super(WebsiteReviewConfig, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        review_no = IrDefault.get('website.review.config', 'review_no') or 1
        auto_publish = IrDefault.get('website.review.config', 'auto_publish')
        message_when_unpublish = IrDefault.get('website.review.config', 'message_when_unpublish') or "Congratulation!!! your review has been submitted successfully, it will publish with in 24 hours."
        res.update({'review_no': review_no, 'auto_publish': auto_publish, 'message_when_unpublish': message_when_unpublish})
        return res

    @api.multi
    def check_review_no(self):
        if self.review_no > 0:
            return True
        else:
            return False

    _constraints = [
        (check_review_no, '\n\nNumber of review must be greter than 0.', ['review_no'])]
