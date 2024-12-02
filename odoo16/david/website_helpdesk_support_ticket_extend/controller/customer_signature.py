import binascii
from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    @http.route(['/my/ticket/<int:ticket_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, ticket_id, access_token=None, name=None, signature=None, csrf=False):
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('helpdesk.support', ticket_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'custom_helpdesk_sign_by': request.env.user.id,
                'custom_helpdesk_sign_date': fields.Datetime.now(),
                'custom_signature_helpdesk_support': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        return {
            'force_refresh': True,
        }
