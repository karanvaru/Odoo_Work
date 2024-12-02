from odoo.addons.website_helpdesk_support_ticket.controllers.main import HelpdeskSupport
from odoo import http, _
from odoo.http import request, Controller
import base64


class HelpdeskSupport(HelpdeskSupport):

    @http.route(['/website_helpdesk_support_ticket/ticket_submitted'], type='http', auth="public", methods=['POST'],
                website=True)
    def ticket_submitted(self, **post):
        check_result = self._check_domain(**post)
        if not check_result:
            try:
                return request.render('helpdesk_domain_restriction.domain_ticket_email', {})
            except:
                pass

        cr, uid, context, pool = http.request.cr, http.request.uid, http.request.context, request.env
        #        Partner = request.env['res.partner'].sudo().search([('email', '=', post['email'])], limit=1) odoo13
        if request.env.user.has_group('base.group_public'):
            Partner = request.env['res.partner'].sudo().search([('email', '=', post['email'])], limit=1)
        else:
            Partner = request.env.user.partner_id

        if Partner:
            team_obj = http.request.env['support.team']
            team_match = team_obj.sudo().search([('is_team', '=', True)], limit=1)

            if post.get('team_id', False):
                team_match = team_obj.sudo().browse(int(post['team_id']))

            support = pool['helpdesk.support'].sudo().with_context(post=post).create({
                'subject': post['subject'],
                'team_id': team_match.id,
                # 'partner_id' :team_match.leader_id.id, odoo13
                'user_id': team_match.leader_id.id,
                'team_leader_id': team_match.leader_id.id,
                'email': post['email'],
                'phone': post['phone'],
                'category': post['category'],
                'description': post['description'],
                'priority': post['priority'],
                'partner_id': Partner.id,
                'custome_client_user_id': request.env.user.id,
                'custom_customer_name': post['customer_id'],
            })

            values = {
                'support': support
            }

            attachment_list = request.httprequest.files.getlist('attachment')
            for image in attachment_list:
                if post.get('attachment'):
                    attachments = {
                        'res_name': image.filename,
                        'res_model': 'helpdesk.support',
                        'res_id': support,
                        # 'datas': base64.encodebytes(image.read()),
                        'datas': base64.encodebytes(image.read()),
                        'type': 'binary',
                        # 'datas_fname': image.filename,
                        'name': image.filename,
                    }
                    attachment_obj = http.request.env['ir.attachment']
                    attach = attachment_obj.sudo().create(attachments)
            if len(attachment_list) > 0 and post.get('attachment'):
                group_msg = (
                    'The customer has sent one or more attachments with this helpdesk ticket. Name of attachment(s): ')
                for attach in attachment_list:
                    group_msg = group_msg + '\n' + attach.filename
                group_msg = group_msg + '\n' + '. The attachment icon is located above in the top menu. View or download the attachment there.'
                support.sudo().message_post(body=_(group_msg), message_type='comment')

            return request.render('website_helpdesk_support_ticket.thanks_mail_send', values)
        else:
            my_ret = self.custom_guest_ticket_create(**post)
            if not my_ret:
                return request.render('website_helpdesk_support_ticket.support_invalid', {})
            else:
                return request.render('website_helpdesk_support_ticket.thanks_mail_send', my_ret)
