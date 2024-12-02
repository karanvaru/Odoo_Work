# -*- coding: utf-8 -*-

from collections import OrderedDict
import werkzeug
import base64
from odoo import http, _
from odoo.http import request, Controller
from odoo.addons.portal.controllers.portal import CustomerPortal, route
from odoo.addons.portal.controllers import portal


class HelpdeskSupport(http.Controller):

    @http.route(['/email-verification/<int:ticket>'], type='http', auth="user", website=True)
    def email_verification(self, ticket, **post):
        ticket_id = request.env['helpdesk.support'].sudo().browse(ticket)
        return request.render('website_helpdesk_support_ticket_extend.website_verification_ticket',
                              {'ticket': ticket_id})

    @http.route(['/email_verification_data'], type='http', auth="user", website=True)
    def email_verification_data(self, **post):
        ticket_id = request.env['helpdesk.support'].sudo().browse(int(post['ticke_val']))
        if post['varify'] == "yes":
            stage = request.env['helpdesk.stage.config'].sudo().search([('stage_type', '=', 'closed')])
            ticket_id.update({
                'stage_id': stage.id,
            })
        else:
            ticket_id.update({
                'comment': post['reason'],
            })
        return http.request.render('website.contactus_thanks')


class CustomerPortal(CustomerPortal):

    @http.route(['/my/ticket/<model("helpdesk.support"):ticket>'], type='http', auth="user", website=True)
    def my_ticket(self, ticket=None, access_token=None, **kw):
        attachment_list = request.httprequest.files.getlist('attachment')
        user = request.env.user
        support_obj = http.request.env['helpdesk.support'].sudo().browse(ticket.id)
        partner = request.env.user.partner_id
        support_team = http.request.env['support.team'].sudo().search([('team_ids', 'in', [user.id])])
        domain = [
            '|', '|', ('user_id', '=', user.id),
            ('team_id', 'in', support_team.ids),
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        tickets = support_obj.sudo().search(domain).ids
        if support_obj.id not in tickets:
            ticket = http.request.env['helpdesk.support'].sudo()
        for image in attachment_list:
            if kw.get('attachment'):
                attachments = {
                    'res_name': image.filename,
                    'res_model': 'helpdesk.support',
                    'res_id': ticket.id,
                    # 'datas': base64.encodebytes(image.read()),
                    'datas': base64.encodebytes(image.read()),
                    'type': 'binary',
                    # 'datas_fname': image.filename,
                    'name': image.filename,
                }
                attachment_obj = http.request.env['ir.attachment']
                attachment_obj.sudo().create(attachments)
        if len(attachment_list) > 0:
            group_msg = 'Customer has sent %s attachments to this helpdesk ticket. Name of attachments are: ' % (
                len(attachment_list))
            for attach in attachment_list:
                group_msg = group_msg + '\n' + attach.filename
            group_msg = group_msg + '\n' + '. You can see top attachment menu to download attachments.'
            support_obj.sudo().message_post(body=_(group_msg),
                                            message_type='comment',
                                            subtype="mt_comment",
                                            author_id=support_obj.partner_id.id
                                            )
            customer_msg = _('%s') % (kw.get('ticket_comment'))
            support_obj.sudo().message_post(body=customer_msg,
                                            message_type='comment',
                                            subtype="mt_comment",
                                            author_id=support_obj.partner_id.id)
            return http.request.render('website_helpdesk_support_ticket.successful_ticket_send', {
            })
        if kw.get('ticket_comment'):
            customer_msg = _('%s') % (kw.get('ticket_comment'))
            support_obj.sudo().message_post(body=customer_msg,
                                            message_type='comment',
                                            subtype="mt_comment",
                                            author_id=support_obj.partner_id.id)
            return http.request.render('website_helpdesk_support_ticket.successful_ticket_send', {
            })
        return request.render("website_helpdesk_support_ticket.display_ticket",
                              {'ticket': ticket, 'token': access_token, 'user': request.env.user})

# class CustomerPortal(portal.CustomerPortal):

# class ProjectCustomerPortal(CustomerPortal):
# def _prepare_home_portal_values(self, counters):
#     values = super()._prepare_home_portal_values(counters)
#     if not request.env.user.has_group('website_helpdesk_support_ticket_extend.group_show_portal_account'):
#         values['custom_estimate_count'] = 0
#         values['task_count'] = 0
#         values['timesheet_count'] = 0
#         values['ticket_count'] = 0
#         values['quotation_count'] = 0
#         values['order_count'] = 0
#         values['purchase_count'] = 0
#         values['invoice_count'] = 0
#         values['project_count'] = 0
#         values['job_card_count_custom'] = 0
#     return values
