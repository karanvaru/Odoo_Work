# -*- coding: utf-8 -*-

from collections import OrderedDict
import werkzeug
import base64
from odoo import http, _
from odoo.http import request
#from odoo import models,registry, SUPERUSER_ID odoo13
from odoo import registry
# from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv.expression import OR

class HelpdeskSupport(http.Controller):

    def _check_domain(self, **post):
        return True

    #@http.route(['/website_helpdesk_support_ticket/ticket_submitted'], type='http', auth="public", methods=['POST'], website=True)
    def custom_guest_ticket_create(self, **post):
        return False


    @http.route(['/website_helpdesk_support_ticket/ticket_submitted'], type='http', auth="public", methods=['POST'], website=True)
    def ticket_submitted(self, **post):
        check_result = self._check_domain(**post)
        if not check_result:
            try:
                return request.render('helpdesk_domain_restriction.domain_ticket_email',{})
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
            team_match = team_obj.sudo().search([('is_team','=', True)], limit=1)

            if post.get('team_id', False):
                team_match = team_obj.sudo().browse(int(post['team_id']))
                
            support = pool['helpdesk.support'].sudo().with_context(post=post).create({
                'subject': post['subject'],
                'team_id' :team_match.id,
                #'partner_id' :team_match.leader_id.id, odoo13
                'user_id' :team_match.leader_id.id,
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
                'support':support
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
                               #'datas_fname': image.filename,
                               'name': image.filename,
                           }
                    attachment_obj = http.request.env['ir.attachment']
                    attach = attachment_obj.sudo().create(attachments)
            if len(attachment_list) > 0 and post.get('attachment'):
                group_msg = 'Customer has sent %s attachments to this helpdesk ticket. Name of attachments are: ' % (len(attachment_list))
                for attach in attachment_list:
                    group_msg = group_msg + '\n' + attach.filename
                group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
                support.sudo().message_post(body=_(group_msg),message_type='comment')
                    
            return request.render('website_helpdesk_support_ticket.thanks_mail_send', values)
        else:
            my_ret = self.custom_guest_ticket_create(**post)
            if not my_ret:
                return request.render('website_helpdesk_support_ticket.support_invalid',{})
            else:
                return request.render('website_helpdesk_support_ticket.thanks_mail_send', my_ret)

    
    # not necessary  odoo13
#    @http.route(['/website_helpdesk_support_ticket/invite'], auth='public', website=True, methods=['POST'])
#    def index_user_invite(self, **kw):
#        email = kw.get('email')
#        name = kw.get('name')
#        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
#        user = request.env['res.users'].browse(request.uid)
#        user_exist = request.env['res.users'].sudo().search([('login','=',str(email))])
#        vals = {
#                  'user_id':user_exist,
#                }
#        if user_exist:
#            return http.request.render('website_helpdesk_support_ticket.user_alredy_exist', vals)
#        value={
#              'name': name,
#              'email': email,
#              'invitation_date':datetime.date.today(),
#              'referrer_user_id':user.id,
#              }
#        user_info_id = self.create_history(value)
#        base_url = http.request.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069') + '/page/website_helpdesk_support_ticket.user_thanks'
#        url = "%s?user_info=%s" %(base_url, user_info_id.id)
#        reject_url = http.request.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069') + '/page/website_helpdesk_support_ticket.user_thanks_reject'
#        rejected_url = "%s?user_info=%s" %(reject_url, user_info_id.id)
#        local_context = http.request.env.context.copy()
#        issue_template = http.request.env.ref('website_helpdesk_support_ticket.email_template_helpdesk_ticket')
#        local_context.update({'user_email': email, 'url': url, 'name':name,'rejected_url':rejected_url})
#        issue_template.sudo().with_context(local_context).send_mail(request.uid, force_send=True)
       
    
    @http.route(['/helpdesk_email/feedback/<int:order_id>'], type='http', auth='public', website=True)
    def feedback_email(self, order_id, **kw):
        values = {}
        ticket_obj_id = request.env['helpdesk.support'].browse(order_id)
        values.update({'ticket_id': ticket_obj_id,'ticket_rec_id':order_id})
        return request.render("website_helpdesk_support_ticket.website_helpdesk_feedback", values) 
       
    
    @http.route(['/helpdesk/feedback/'],
                type='http', auth='public', website=True)
    def start_rating(self, **kw):
        partner_id = kw['partner_id']
        user_id = kw['ticket_rec_id']
        ticket_obj = request.env['helpdesk.support'].browse(int(user_id))
        #if partner_id == UserInput.partner_id.id:
        vals = {
              # 'rating':kw['star'],
              # 'rating': kw.get('star'),
              'comment':kw['comment'],
            }
        if 'star' in kw:
           vals.update({'rating': kw.get('star')})
        ticket_obj.sudo().write(vals)
        if not 'star' in kw:
            customer_msg = _(ticket_obj.partner_id.name + 'comment is %s') % (kw['comment'],)
        else:
            customer_msg = _(ticket_obj.partner_id.name + 'has send this feedback rating is %s and comment is %s') % (kw['star'],kw['comment'],)
        ticket_obj.sudo().message_post(body=customer_msg)
        return http.request.render("website_helpdesk_support_ticket.successful_feedback")

    
    @http.route(['/website_support_ticket/search_user_ticket'], type='http', auth="user", methods=['POST'], website=True)
    def search_user_ticket(self, **post):
        Ticket = request.env['helpdesk.support'].sudo().search([('name', '=', post['ticket_no'])])
        if Ticket:
            portal_link = "/my/ticket/%s" %(Ticket.id)
            return werkzeug.utils.redirect(portal_link)
        else:
            return http.request.render('website_helpdesk_support_ticket.ticket_invalid',{})

# class website_account(website_account):

class CustomerPortal(CustomerPortal):
    _items_per_page = 20

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'ticket_count' in counters:
            ticket_count = request.env['helpdesk.support'].sudo().search_count([('partner_id', 'child_of', [partner.commercial_partner_id.id])])
            values['ticket_count'] = ticket_count
        return values


#     @http.route()
#     def account(self, **kw):
#         """ Add ticket documents to main account page """
#         response = super(CustomerPortal, self).account(**kw)
#         partner = request.env.user.partner_id
#         ticket = request.env['helpdesk.support']
#         ticket_count = ticket.sudo().search_count([
#         ('partner_id', 'child_of', [partner.commercial_partner_id.id])
#           ])
#         response.qcontext.update({
#         'ticket_count': ticket_count,
#         })
#         return response
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ticket = request.env['helpdesk.support']
        ticket_count = ticket.sudo().search_count([
        ('partner_id', 'child_of', [partner.commercial_partner_id.id])
          ])
        values.update({
            'ticket_count': ticket_count,
            'page_name': 'ticket_page',
        })
        return values
    
    
    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_ticket(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        support_obj = http.request.env['helpdesk.support']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # count for pager
        ticket_count = support_obj.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/tickets",
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'subject'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        # searchbar_inputs = {
        #     'title': {'input': 'title', 'label': _('Search <span class="nolabel"> (in Title)</span>')},
        #     'issue_no': {'input': 'issue_no', 'label': _('Search in Issue Number')},
        #     'date': {'input': 'request_date', 'label': _('Search in date')},
        #     'all': {'input': 'all', 'label': _('Search in All')},
        # }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        #archive_groups = self._get_archive_groups('project.task', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
#            if search_in in ('stage', 'all'): odoo13
#                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])odoo13
            if search_in in ('stage', 'all'):
                stage_id = request.env['helpdesk.stage.config'].sudo().search([('name', 'ilike',  search)])
                search_domain = OR([search_domain, [('stage_id', 'in', stage_id.ids)]])
            domain += search_domain

        # content according to pager and archive selected
        tickets = support_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'tickets': tickets,
            'page_name': 'ticket_page',
            'pager': pager,
            'default_url': '/my/tickets',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("website_helpdesk_support_ticket.display_tickets", values)
       
    
    @http.route(['/my/ticket/<model("helpdesk.support"):ticket>'], type='http', auth="user", website=True)
    def my_ticket(self, ticket=None, access_token=None, **kw):
        attachment_list = request.httprequest.files.getlist('attachment')
        support_obj = http.request.env['helpdesk.support'].sudo().browse(ticket.id)

        # validation of ticket if other user access ticket
        partner = request.env.user.partner_id
        support_object = http.request.env['helpdesk.support']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        tickets = support_object.sudo().search(domain).ids
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
            group_msg = 'Customer has sent %s attachments to this helpdesk ticket. Name of attachments are: ' % (len(attachment_list))
            for attach in attachment_list:
                group_msg = group_msg + '\n' + attach.filename
            group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
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
            return http.request.render('website_helpdesk_support_ticket.successful_ticket_send',{
            })
        if kw.get('ticket_comment'):
            customer_msg = _('%s') % (kw.get('ticket_comment'))
            support_obj.sudo().message_post(body=customer_msg,
                                            message_type='comment',
                                            subtype="mt_comment",
                                            author_id=support_obj.partner_id.id)
            return http.request.render('website_helpdesk_support_ticket.successful_ticket_send',{
            })
        return request.render("website_helpdesk_support_ticket.display_ticket", {'ticket': ticket, 'token':access_token, 'user': request.env.user})
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
