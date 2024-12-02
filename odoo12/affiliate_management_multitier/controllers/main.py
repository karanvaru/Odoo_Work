#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
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
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
# from odoo.addons.affiliate_management.controllers.affiliate_website import affiliate_website
from odoo.addons.affiliate_management.controllers.home import Home

class WebsiteAffiliate(Home):


    @http.route('/affiliate/join', auth='public', type='json', website=True, methods=['POST'])
    def join(self, email, **kw):
        keyExist = self._checkCookieExist()
        affRequestObj = request.env['affiliate.request'].sudo()
        new_user = False
        aff = affRequestObj.search([('name', '=', email)])
        if not aff:
            new_user = True
        result = super(WebsiteAffiliate, self).join(email=email)
        if new_user:
            newRequest = affRequestObj.search([('name', '=', email)])
            if newRequest and keyExist.get('status'):
                newRequest.write({
                    'parent_aff_key':keyExist.get('key')
                })
        return result


    def _checkCookieExist(self):
        cookies = dict(request.httprequest.cookies)
        result = {'status':False,'key':""}
        for k, v in cookies.items():
            if 'affkey_' in k:
                result['status'] = True
                result['key'] = k.split("affkey_")[1]
        return result