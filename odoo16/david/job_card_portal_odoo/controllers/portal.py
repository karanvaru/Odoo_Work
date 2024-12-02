# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http,fields, _
from odoo.http import request
from markupsafe import Markup
from binascii import Error as binascii_error
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.osv.expression import OR, AND


class JobCardPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'job_card_count_custom' in counters:
            values['job_card_count_custom'] = request.env['project.task'].sudo().search_count(self._get_jobcard_domain_custom())
        return values

    def _jobcard_get_page_view_values_custom(self, jobcard_id, access_token, **kwargs):
        page_name = 'jobcard_page'
        history = 'my_jobcard_history'
        values = {
            'page_name': page_name,
            'jobcard_id':jobcard_id,
        }
        return self._get_page_view_values(jobcard_id, access_token, values, history, False, **kwargs)

    def _get_jobcard_domain_custom(self):
        return [('partner_id','child_of',request.env.user.partner_id.id),('is_jobcard', '=', True)]


    def _jobcard_get_searchbar_sortings_custom(self):
        values = {
            'date': {'label': _('Newest'), 'order': 'create_date desc', 'sequence': 1},
            'number':{'label': _('Number'), 'order':'number', 'sequence':2},
            'name': {'label': _('Title'), 'order': 'name', 'sequence': 3},
            'project': {'label': _('Project'), 'order': 'project_id, stage_id', 'sequence': 4},
            'users': {'label': _('Assignees'), 'order': 'user_ids', 'sequence': 5},
            'stage': {'label': _('Stage'), 'order': 'stage_id, project_id', 'sequence': 6},
            'date_deadline': {'label': _('Deadline'), 'order': 'date_deadline asc', 'sequence': 9},
        }
        return values

    def _jobcard_get_searchbar_inputs_custom(self):
        values = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>')), 'order': 1},
            'number': {'input': 'number', 'label': _('Search in Number'), 'order': 2},
            'project': {'input': 'project', 'label': _('Search in Project'), 'order': 3},
            'users': {'input': 'users', 'label': _('Search in Assignees'), 'order': 4},
            'stage': {'input': 'stage', 'label': _('Search in Stages'), 'order': 5},
            'priority': {'input': 'priority', 'label': _('Search in Priority'), 'order': 7},
            'message': {'input': 'message', 'label': _('Search in Messages'), 'order': 11},
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _jobcard_get_search_domain_custom(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('name', 'ilike', search)])
            search_domain.append([('description', 'ilike', search)])
        if search_in in ('number', 'all'):
            search_domain.append([('number', 'ilike', search)])
        if search_in in ('customer', 'all'):
            search_domain.append([('partner_id', 'ilike', search)])
        if search_in in ('message', 'all'):
            search_domain.append([('message_ids.body', 'ilike', search)])
        if search_in in ('stage', 'all'):
            search_domain.append([('stage_id', 'ilike', search)])
        if search_in in ('project', 'all'):
            search_domain.append([('project_id', 'ilike', search)])
        if search_in in ('ref', 'all'):
            search_domain.append([('id', 'ilike', search)])
        if search_in in ('milestone', 'all'):
            search_domain.append([('milestone_id', 'ilike', search)])
        if search_in in ('users', 'all'):
            user_ids = request.env['res.users'].sudo().search([('name', 'ilike', search)])
            search_domain.append([('user_ids', 'in', user_ids.ids)])
        if search_in in ('priority', 'all'):
            search_domain.append([('priority', 'ilike', search == 'normal' and '0' or '1')])
        if search_in in ('status', 'all'):
            search_domain.append([
                ('kanban_state', 'ilike', 'normal' if search == 'In Progress' else 'done' if search == 'Ready' else 'blocked' if search == 'Blocked' else search)
            ])
        return OR(search_domain)

    @http.route(['/my/jobcards', '/my/jobcards/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_jobcards_details(self, page=1, sortby=None, filterby=None, search=None, search_in='all', **kw):

        jobcard_custom_obj = request.env['project.task'].sudo()
        domain = self._get_jobcard_domain_custom()
        jobcard_custom_count = jobcard_custom_obj.search_count(domain)
        searchbar_sortings = self._jobcard_get_searchbar_sortings_custom()
        searchbar_inputs = self._jobcard_get_searchbar_inputs_custom()
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if search and search_in:
            domain += self._jobcard_get_search_domain_custom(search_in, search)

        pager = portal_pager(
            url="/web/portal/job_card_custom",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
            total=jobcard_custom_count,
            page=page,
            step=self._items_per_page
        )
        total_jobcard_custom = jobcard_custom_obj.search(domain, order=order,limit=self._items_per_page, offset=pager['offset'])
        values = self._prepare_portal_layout_values()
        values.update({
            'total_jobcard_custom': total_jobcard_custom,
            'page_name': 'job_card_custom',
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'pager': pager,
            'default_url': '/web/portal/job_card_custom'
        })
        return request.render('job_card_portal_odoo.portal_my_jobcards', values)

    
    @http.route('/my/jobcard/<int:jobcard_id_id>', type='http', auth='user', website=True)
    def portal_my_jobcard_form_details(self, jobcard_id_id, access_token=None, **kwargs):
        try:
            jobcard_sudo = self._document_check_access('project.task', jobcard_id_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._jobcard_get_page_view_values_custom(jobcard_sudo, access_token, **kwargs)
        return request.render("job_card_portal_odoo.portal_my_jobcard_form", values)


    @http.route(['/my/jobcards/<int:jobcard_id>/accept'], type='json', auth="user", website=True)
    def custom_job_card_accept_signature(self, jobcard_id, access_token=None, name=None, signature=None):
        access_token = access_token or request.httprequest.args.get('access_token')
        jobcard_sudo = request.env['project.task'].sudo().browse(jobcard_id)
        try:
            jobcard_sudo.write({
                'custom_job_sign_by': request.env.user,
                'custom_job_sign_date': fields.Datetime.now(),
                'custom_signature_job_card': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}
        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
        }