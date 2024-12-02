from odoo import fields, http, _, tools
from odoo.http import request
from odoo.osv.expression import OR
from odoo.exceptions import AccessError, MissingError, ValidationError
import pytz
from odoo.addons.portal.controllers.portal import \
    CustomerPortal, pager as portal_pager, get_records_pager


class CRM_lead_portal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(CRM_lead_portal, self)._prepare_portal_layout_values()
        values['crm_lead_count'] = 0
        values['crm_lead_count'] = request.env['crm.lead'].search_count([('user_id', '=', request.env.user.id)])

        return values

    @http.route(['/lead/portal', '/lead/portal/page/<int:page>'], type='http', auth="user", website=True)
    def crm_lead_portal_list_view(self, groupby='none', page=1, date_begin=None, date_end=None,
                                  search=None, search_in="name",
                                  sortby='bid_date_asc'):

        if groupby:
            if 'date_week' in groupby:
                groupby = 'date_week'
            elif 'date_month' in groupby:
                groupby = 'date_month'
            elif 'date_quarter' in groupby:
                groupby = 'date_quarter'
            elif 'date_year' in groupby:
                groupby = 'date_year'
            elif 'create_date' in groupby:
                groupby = 'create_date'
            elif 'create_week' in groupby:
                groupby = 'create_week'
            elif 'create_month' in groupby:
                groupby = 'create_month'
            elif 'create_quarter' in groupby:
                groupby = 'create_quarter'
            elif 'create_year' in groupby:
                groupby = 'create_year'
            elif 'date' in groupby:
                groupby = 'date'
            else:
                groupby = 'none'

        values = self._prepare_portal_layout_values()
        lead_or = request.env['crm.lead']
        domain = [('user_id', '=', request.env.user.id)]
        searchbar_sortings = {
            'bid_date_asc': {'label': _('Close Date Asc'), 'order': 'bid_closing_date asc,id asc'},
            'bid_date': {'label': _('Close Date Desc'), 'order': 'bid_closing_date desc, id desc'},
            'date': {'label': _('Created Date Desc'), 'order': 'create_date desc, id desc'},
            'date_asc': {'label': _('Created Date Asc'), 'order': 'create_date asc, id asc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
        }
        searchbar_inputs = {
            'name': {'label': 'Search In Opportunity', 'input': 'name'},
            'sku': {'label': 'Search In Sku', 'input': 'sku'},
            'catelog': {'label': 'Search In Catelog', 'input': 'catelog'},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'date': {'input': 'date', 'label': _('Closing Date')},
            'date_week': {'input': 'date', 'label': _('Closing Week')},
            'date_month': {'input': 'date', 'label': _('Closing Month')},
            'date_quarter': {'input': 'date', 'label': _('Closing Quarter')},
            'date_year': {'input': 'date', 'label': _('Closing Year')},
            'create_date': {'input': 'date', 'label': _('Create Date')},
            'create_week': {'input': 'date', 'label': _('Create Week')},
            'create_month': {'input': 'date', 'label': _('Create Month')},
            'create_quarter': {'input': 'date', 'label': _('Create Quarter')},
            'create_year': {'input': 'date', 'label': _('Create Year')},
        }
        if not sortby:
            sortby = 'bid_date'
        order = searchbar_sortings[sortby]['order']
        archive_groups = self._get_archive_groups('crm.lead', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        if search and search_in:
            search_domain = []
            if search_in in ('name'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('sku'):
                search_domain = OR([search_domain, [('x_studio_gem_sku', 'ilike', search)]])
            if search_in in ('catelog'):
                search_domain = OR([search_domain, [('x_studio_catalog_id', 'ilike', search)]])
            domain += search_domain

        def call_search_method(domain=[]):
            if groupby != 'none':
                return request.env['crm.lead'].search(domain, order=order)
            else:
                return request.env['crm.lead'].search(domain, order=order, limit=self._items_per_page,
                                                      offset=(page - 1) * self._items_per_page)

        lead_ids = request.env['crm.lead'].sudo()
        tasks = request.env['crm.lead'].search(domain, order=order, limit=self._items_per_page,
                                               offset=(page - 1) * self._items_per_page)
        total_order = lead_or.search_count(domain)

        groupby_items_per_page = 1
        if groupby == 'date':
            time_data = lead_ids.read_group(domain, ['bid_closing_date'], ['bid_closing_date:day'], orderby=order,
                                            limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:day'],call_search_method(k['__domain']), k['bid_closing_date_count']] for k in time_data]

        elif groupby == 'date_week':
            time_data = lead_ids.read_group(domain, ['bid_closing_date'],
                                            ['bid_closing_date:week'], orderby=order, limit=groupby_items_per_page,
                                            offset=(page - 1) * groupby_items_per_page)

            grouped_tasks = [[k['bid_closing_date:week'], call_search_method(k['__domain']), k['bid_closing_date_count']] for k in time_data]
        elif groupby == 'date_month':
            time_data = lead_ids.read_group(domain, ['bid_closing_date'],
                                            ['bid_closing_date:month'], orderby=order, limit=groupby_items_per_page,
                                            offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:month'], call_search_method(k['__domain']), k['bid_closing_date_count']] for k in time_data]
        elif groupby == 'date_quarter':
            time_data = lead_ids.read_group(domain, ['bid_closing_date'],
                                            ['bid_closing_date:quarter'], orderby=order, limit=groupby_items_per_page,
                                            offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:quarter'], call_search_method(k['__domain']), k['bid_closing_date_count']] for k in time_data]
        elif groupby == 'date_year':
            time_data = lead_ids.read_group(domain, ['bid_closing_date'],
                                            ['bid_closing_date:year'], orderby=order, limit=groupby_items_per_page,
                                            offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:year'], call_search_method(k['__domain']), k['bid_closing_date_count']] for k in time_data]
        elif groupby == 'create_date':
            time_data = lead_ids.read_group(domain, ['create_date'], ['create_date:day'], orderby=order,
                                            limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:day'], call_search_method(k['__domain']), k['create_date_count']] for k in time_data]
        elif groupby == 'create_week':
            time_data = lead_ids.read_group(domain, ['create_date'], ['create_date:week'], orderby=order,
                                            limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:week'], call_search_method(k['__domain']), k['create_date_count']] for k in time_data]
        elif groupby == 'create_month':
            time_data = lead_ids.read_group(domain, ['create_date'], ['create_date:month'], orderby=order,
                                            limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:month'], call_search_method(k['__domain']), k['create_date_count']] for k in time_data]
        elif groupby == 'create_quarter':
            time_data = lead_ids.read_group(domain, ['create_date'], ['create_date:quarter'], orderby=order,
                                            limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:quarter'], call_search_method(k['__domain']), k['create_date_count']] for k in time_data]
        elif groupby == 'create_year':
            time_data = lead_ids.read_group(domain, ['create_date'], ['create_date:year'], orderby=order,
                                            limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:year'], call_search_method(k['__domain']), k['create_date_count']] for k in time_data]
        else:
            grouped_tasks = [['', tasks]]

        if groupby != 'none':
            pager = portal_pager(
                url="/lead/portal",
                url_args={
                    'date_begin': date_begin,
                    'date_end': date_end,
                    'sortby': sortby,
                    'search': search,
                    'search_in': search_in,
                    'groupby': groupby
                },
                total=total_order,
                page=page,
                step=self._items_per_page
            )
        else:
            pager = portal_pager(
                url="/lead/portal",
                url_args={
                    'date_begin': date_begin,
                    'date_end': date_end,
                    'sortby': sortby,
                    'search': search,
                    'search_in': search_in,
                },
                total=total_order,
                page=page,
                step=self._items_per_page
            )
        lead_order = lead_or.search(
            domain,
            order=order,
            offset=pager['offset'],
            limit=self._items_per_page
        )

        request.session['my_lead_history'] = lead_order.ids[:100]
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'lead_list': lead_order,
            'page_name': 'crm_lead',
            'pager': pager,
            'groupby': groupby,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'searchbar_inputs': searchbar_inputs,
            'search': search,
            'default_url': '/lead/portal',
            'searchbar_groupby': searchbar_groupby,
            'grouped_tasks': grouped_tasks,
            'archive_groups': archive_groups,
            'reset_url': '/lead/portal'
        })
        return request.render("ki_crm_bid.crm_lead_portal_template_list", values)

    def _set_lead_values(self):
        lead_id = request.env['crm.lead']
        country_india = request.env.ref("base.in")
        vals = {
            'error': {},
            'error_message': [],
            'mode': 'read',
            'lead_id': lead_id,
            'page_name': 'crm_lead',
            'users': request.env['res.users'].search_read([], ['id', 'name']),
            'teams': request.env['crm.team'].search_read([], ['id', 'name']),
            'states': request.env['res.country.state'].search_read([('country_id', '=', country_india.id)],
                                                                   ['id', 'name']),
            'bid_mii_ids': request.env['crm.mii.content'].search_read([], ['id', 'name']),
            'bid_cap_ids': request.env['crm.capture.type'].search_read([], ['id', 'name']),
            'bid_cat_ids': request.env['crm.category.type'].search_read([], ['id', 'name']),
            'bid_ra_ids': request.env['crm.bid.ra'].search_read([], ['id', 'name']),
            'bid_type_ids': request.env['crm.bid.type'].search_read([], ['id', 'name']),
            'categories': request.env['crm.product.category'].search_read([], ['id', 'name']),
            'form_action': '/'
        }
        return vals

    @http.route(['/my/lead/<int:lead_id>'], type='http', auth='user', website=True)
    def portal_lead_detail(self, lead_id, **kw):
        if not request.env.user.has_group('ki_crm_bid.group_enable_bid_access'):
            return request.redirect('/my')
        try:
            lead_id = request.env['crm.lead'].browse(lead_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._set_lead_values()
        if lead_id:
            tz_name = request.env.user.tz or request._context.get('tz')
            if not tz_name:
                raise ValidationError(
                    _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
            tz = pytz.timezone(tz_name)
            bid_closing_date = pytz.utc.localize(lead_id.bid_closing_date, is_dst=None).astimezone(tz)
            values.update({
                'lead_id': lead_id,
                'bid_closing_date': bid_closing_date.strftime('%d/%m/%Y %I:%M %p'),
            })

        new_vals = self._get_page_view_values(lead_id, None, values, 'my_lead_history', False, **kw)
        response = request.render("ki_crm_bid.crm_lead_portal_form_view_new", new_vals)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
