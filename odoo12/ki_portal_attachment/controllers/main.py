from odoo import fields, http, _, tools
from odoo.http import request
from odoo.addons.portal.controllers.mail import PortalChatter
import unicodedata


class Portalattach(PortalChatter):

    @http.route(['/mail/chatter_post'], type='http', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        kw.pop('portal_multi_attach_input')
        attachments_list = request.httprequest.files.getlist('portal_multi_attach_input')
        new_attachment = []
        for attach in attachments_list:
            filename = attach.filename
            if request.httprequest.user_agent.browser == 'safari':
                filename = unicodedata.normalize('NFD', attach.filename)
            if filename:
                new_attachment.append([filename, attach.read()])

        if new_attachment:
            new_dict = dict(
                attachments = new_attachment or [],
                ** kw
            )
        else:
            new_dict = dict(**kw)
        call_super = super(Portalattach, self).portal_chatter_post(res_model, res_id, message, **new_dict)
        return call_super
