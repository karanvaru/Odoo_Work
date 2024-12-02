# from gevent.libev.watcher import prepare
from odoo import fields, http, _, tools
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import \
    CustomerPortal, pager as portal_pager, get_records_pager
from collections import OrderedDict
import json, base64
from dateutil.parser import parse
from operator import itemgetter
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
import datetime
import pytz
from datetime import timedelta
from odoo.exceptions import AccessError, MissingError, ValidationError


class CRM_Bid_portal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CRM_Bid_portal, self)._prepare_portal_layout_values()
        values['crm_bid_count_draft'] = 0
        values['crm_bid_count_oppo'] = 0
        if request.env.user.has_group('ki_crm_bid.group_enable_bid_access'):
            values['crm_bid_count_draft'] = request.env['crm.bid'].search_count(
                [('user_id', '=', request.env.user.id), ('state', '=', 'draft')])
            values['crm_bid_count_oppo'] = request.env['crm.bid'].search_count(
                [('user_id', '=', request.env.user.id), ('state', '=', 'opportunity')])

        return values

    @http.route(['/my/crm/bid', '/my/crm/bid/page/<int:page>'], type='http', auth="user", website=True)
    def crm_Bid_portal_list_view(self, page=1, date_begin=None, date_end=None, sortby='bid_date_asc', filterby=None,
                                 search=None, search_in='bid', groupby='none', **kw):
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

        if not request.env.user.has_group('ki_crm_bid.group_enable_bid_access'):
            return request.redirect('/my')
        values = self._prepare_portal_layout_values()
        crm_order = request.env['crm.bid']

        domain = [('user_id', '=', request.env.user.id)]

        searchbar_sortings = {
            'bid_date_asc': {'label': _('Close Date Asc'), 'order': 'bid_closing_date asc,id asc'},
            'bid_date': {'label': _('Close Date Desc'), 'order': 'bid_closing_date desc, id desc'},
            'date': {'label': _('Created Date Desc'), 'order': 'create_date desc, id desc'},
            'date_asc': {'label': _('Created Date Asc'), 'order': 'create_date asc, id asc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'opportunity': {'label': _('Opportunity'), 'domain': [('state', '=', 'opportunity')]}
        }
        searchbar_inputs = {
            'bid': {'input': 'bid', 'label': _('Search in #BID')},
            'sku': {'input': 'sku', 'label': _('Search in SKU')},
            'catalog': {'input': 'catalog', 'label': _('Search in Catalog')},
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
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        archive_groups = self._get_archive_groups('crm.bid', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('bid'):
                search_domain = OR(
                    [search_domain, [('name', 'ilike', search)]])
            if search_in in ('sku'):
                search_domain = OR([search_domain, [('x_studio_gem_sku', 'ilike', search)]])
            if search_in in ('catalog'):
                search_domain = OR(
                    [search_domain, [('x_studio_catalog_id', 'ilike', search)]])
            domain += search_domain

        crm_count = crm_order.search_count(domain)

        #         pager = portal_pager(
        #             url="/my/crm/bid",
        #              url_args={
        #                 'date_begin': date_begin,
        #                 'date_end': date_end,
        #                 'sortby': sortby,
        #                 'filterby': filterby,
        #                 'search': search,
        #                 'search_in': search_in,
        # #                 'groupby': groupby
        #             },
        #             total=crm_count,
        #             page=page,
        #             step=self._items_per_page
        #         )

        def call_search_method(domain=[]):
            if groupby != 'none':
                return request.env['crm.bid'].search(domain, order=order)
            else:
                return request.env['crm.bid'].search(domain, order=order, limit=self._items_per_page,
                                                     offset=(page - 1) * self._items_per_page)

        bid_ids = request.env['crm.bid'].sudo()
        tasks = request.env['crm.bid'].search(domain, order=order, limit=self._items_per_page,
                                              offset=(page - 1) * self._items_per_page)

        groupby_items_per_page = 2
        if groupby == 'date':
            time_data = bid_ids.read_group(domain, ['bid_closing_date'], ['bid_closing_date:day'], orderby=order,
                                           limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:day'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'date_week':
            time_data = bid_ids.read_group(domain, ['bid_closing_date'],
                                           ['bid_closing_date:week'], orderby=order, limit=groupby_items_per_page,
                                           offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:week'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'date_month':
            time_data = bid_ids.read_group(domain, ['bid_closing_date'],
                                           ['bid_closing_date:month'], orderby=order, limit=groupby_items_per_page,
                                           offset=(page - 1) * groupby_items_per_page)
            #             grouped_tasks = [request.env['crm.bid'].concat(*g) for k, g in groupbyelem(tasks, itemgetter('bid_closing_date'))]

            grouped_tasks = [[k['bid_closing_date:month'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'date_quarter':
            time_data = bid_ids.read_group(domain, ['bid_closing_date'],
                                           ['bid_closing_date:quarter'], orderby=order, limit=groupby_items_per_page,
                                           offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:quarter'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'date_year':
            time_data = bid_ids.read_group(domain, ['bid_closing_date'],
                                           ['bid_closing_date:year'], orderby=order, limit=groupby_items_per_page,
                                           offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['bid_closing_date:year'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'create_date':
            time_data = bid_ids.read_group(domain, ['create_date'], ['create_date:day'], orderby=order,
                                           limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:day'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'create_week':
            time_data = bid_ids.read_group(domain, ['create_date'], ['create_date:week'], orderby=order,
                                           limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:week'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'create_month':
            time_data = bid_ids.read_group(domain, ['create_date'], ['create_date:month'], orderby=order,
                                           limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:month'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'create_quarter':
            time_data = bid_ids.read_group(domain, ['create_date'], ['create_date:quarter'], orderby=order,
                                           limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:quarter'], call_search_method(k['__domain'])] for k in time_data]
        elif groupby == 'create_year':
            time_data = bid_ids.read_group(domain, ['create_date'], ['create_date:year'], orderby=order,
                                           limit=groupby_items_per_page, offset=(page - 1) * groupby_items_per_page)
            grouped_tasks = [[k['create_date:year'], call_search_method(k['__domain'])] for k in time_data]
        else:
            grouped_tasks = [['', tasks]]

        if groupby != 'none':
            pager = portal_pager(
                url="/my/crm/bid",
                url_args={
                    'date_begin': date_begin,
                    'date_end': date_end,
                    'sortby': sortby,
                    'filterby': filterby,
                    'search': search,
                    'search_in': search_in,
                    'groupby': groupby
                },
                total=crm_count,
                page=page,
                step=self._items_per_page
            )
        else:
            pager = portal_pager(
                url="/my/crm/bid",
                url_args={
                    'date_begin': date_begin,
                    'date_end': date_end,
                    'sortby': sortby,
                    'filterby': filterby,
                    'search': search,
                    'search_in': search_in,
                    #                 'groupby': groupby
                },
                total=crm_count,
                page=page,
                step=self._items_per_page
            )

        orders = crm_order.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_bid_history'] = orders.ids[:100]
        values.update({
            'date': date_begin,
            'crm_Bids': orders,
            'page_name': 'crm_bid',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/crm/bid',
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'groupby': groupby,
            'search': search,
            'reset_url': '/my/crm/bid'
        })

        return request.render("ki_crm_bid.crm_Bid_portal_template_list", values)

    MANDATORY_CRM_TENDER_FIELDS = [
        "name",
        "bid_closing_date",
        "crm_product_category_id",
        "x_studio_quantity",
        "value",
        "x_studio_opportunity_type_1",
        "user_id",
        "team_id",
        "gem_customer_name",
        "customer_city",
        'bid_published_date',
        "customer_pincode",
        "customer_state_id",
        "crm_mii_content_id",
        "crm_capture_type_id",
        "crm_category_type_id",
        "bid_to_ra_id",
        "bid_type_id",
        "mii_purchase_preference"
    ]
    OPTIONAL_CRM_TENDER_FIELDS = [
        "x_studio_gem_model_no",
        "x_studio_gem_sku",
        "x_studio_catalog_id",
        "catalog_id_amd",
        # "bid_published_date",
        "file_upload",
        "description",
        "priority"
    ]

    def _set_bit_values(self):
        bid_id = request.env['crm.bid']

        country_india = request.env.ref("base.in")
        vals = {
            'error': {},
            'error_message': [],
            'mode': 'read',
            'bid_id': bid_id,
            'page_name': 'crm_bid',
            'users': request.env['res.users'].search_read([], ['id', 'name']),
            'teams': request.env['crm.team'].search_read([], ['id', 'name']),
            'states': request.env['res.country.state'].search_read([('country_id', '=', country_india.id)],
                                                                   ['id', 'name']),
            'bid_mii_ids': request.env['crm.mii.content'].search_read([], ['id', 'name']),
            'bid_cap_ids': request.env['crm.capture.type'].search_read([], ['id', 'name']),
            'bid_cat_ids': request.env['crm.category.type'].search_read([], ['id', 'name']),
            'bid_ra_ids': request.env['crm.bid.ra'].search_read([], ['id', 'name']),
            'bid_type_ids': request.env['crm.bid.type'].search_read([], ['id', 'name']),
            'opportunities': [{
                'id': i,
                'name': j
            } for i, j in dict(bid_id._fields['x_studio_opportunity_type_1'].selection).items()],
            'categories': request.env['crm.product.category'].search_read([], ['id', 'name']),
            'form_action': '/'
        }
        return vals

    @http.route(['/my/bid/<int:bid_id>'], type='http', auth='user', website=True)
    def portal_bid_detail(self, bid_id, **kw):
        if not request.env.user.has_group('ki_crm_bid.group_enable_bid_access'):
            return request.redirect('/my')
        try:
            bid_id = request.env['crm.bid'].browse(bid_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if not bid_id:
            return request.redirect('/bid/create')
        values = self._set_bit_values()
        if bid_id:
            tz_name = request.env.user.tz or request._context.get('tz')
            if not tz_name:
                raise ValidationError(
                    _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
            tz = pytz.timezone(tz_name)
            bid_closing_date = pytz.utc.localize(bid_id.bid_closing_date, is_dst=None).astimezone(tz)
            # bid_published_date = pytz.utc.localize(bid_id.bid_published_date, is_dst=None).astimezone(tz)
            values.update({
                'bid_id': bid_id,
                'bid_closing_date': bid_closing_date.strftime('%d/%m/%Y %I:%M %p'),
                # 'bid_published_date': bid_published_date.strftime('%d/%m/%Y %I:%M %p')
            })
            if bid_id.bid_published_date:
                bid_published_date = pytz.utc.localize(bid_id.bid_published_date, is_dst=None).astimezone(tz)
                values.update({
                    'bid_published_date': bid_published_date.strftime('%d/%m/%Y %I:%M %p')
                })

        new_vals = self._get_page_view_values(bid_id, None, values, 'my_bid_history', False, **kw)
        response = request.render("ki_crm_bid.crm_Bid_portal_form_view_new", new_vals)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/bid/create', '/bid/edit/<int:bid_id>'], type='http', auth='user', website=True)
    def portal_bid_edit_create(self, bid_id=False, **kw):
        if not request.env.user.has_group('ki_crm_bid.group_enable_bid_access'):
            return request.redirect('/my')
        values = self._set_bit_values()
        if bid_id:
            try:
                bid_id = request.env['crm.bid'].browse(bid_id)
                if not bid_id:
                    return request.redirect('/bid/create')
            except (AccessError, MissingError):
                return request.redirect('/my')
        values.update({
            'mode': 'edit'
        })

        if kw.get('bid_closing_date'):
            date_str = datetime.datetime.strptime(kw.get('bid_closing_date'), "%d/%m/%Y %H:%M:%S").strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT)
            tz_name = request.env.user.tz or request._context.get('tz')
            if not tz_name:
                raise ValidationError(
                    _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
            local = pytz.timezone(tz_name)
            naive = fields.Datetime.from_string(date_str)
            local_dt = local.localize(naive, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            new_date_str = fields.Datetime.to_string(utc_dt)
            kw['bid_closing_date'] = new_date_str

        if kw.get('bid_published_date'):
            date_str = datetime.datetime.strptime(kw.get('bid_published_date'), "%d/%m/%Y %H:%M:%S").strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT)
            tz_name = request.env.user.tz or request._context.get('tz')
            if not tz_name:
                raise ValidationError(
                    _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
            local = pytz.timezone(tz_name)
            naive = fields.Datetime.from_string(date_str)
            local_dt = local.localize(naive, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            new_date_str = fields.Datetime.to_string(utc_dt)
            kw['bid_published_date'] = new_date_str

        kw['priority'] = '0'
        if kw.get('priority_1'):
            kw['priority'] = '1'
            kw.pop('priority_1')
        if kw.get('priority_2'):
            kw['priority'] = '2'
            kw.pop('priority_2')
        if kw.get('priority_3'):
            kw['priority'] = '3'
            kw.pop('priority_3')

        if kw and request.httprequest.method == 'POST':
            error, error_message = self.details_Bid_form_validate(kw)
            values.update({'error': error, 'error_message': error_message})
            # values.update(post)
            if not error:
                new_values = {key: kw[key] for key in self.MANDATORY_CRM_TENDER_FIELDS}
                new_values.update({key: kw[key] for key in self.OPTIONAL_CRM_TENDER_FIELDS if key in kw})
                file_upload_new = False
                if 'file_upload' in new_values.keys():
                    file_upload_new = new_values.pop('file_upload')
                try:
                    new_values.update({
                        'planned_revenue': new_values['value'] or 0
                    })
                    if bid_id:
                        bid_id.write(new_values)
                    else:
                        bid_id = values.get('bid_id').create(new_values)

                    if file_upload_new:
                        attachment_value = {
                            'name': file_upload_new.filename,
                            'datas': base64.encodestring(file_upload_new.read()),
                            'datas_fname': file_upload_new.filename,
                            'res_model': 'crm.bid',
                            'res_id': bid_id.id,
                        }
                        attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
                        if attachment_id:
                            bid_id.sudo()['file_upload'] = [(4, attachment_id.id)]

                    values.update({
                        'mode': 'read'
                    })
                except Exception as e:
                    values.update({
                        'error_message': [e],
                        'mode': 'edit'
                    })
        if values.get('mode') == 'edit':
            values.update({
                'bid_id': bid_id if type(bid_id) not in (float, int) else False,
                'form_action': '/bid/create' if not bid_id else '/bid/edit/%s' % (bid_id.id)
            })
            if type(bid_id) not in (float, int) and bid_id:
                tz_name = request.env.user.tz or request._context.get('tz')
                if not tz_name:
                    raise ValidationError(
                        _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
                tz = pytz.timezone(tz_name)
                bid_closing_date = pytz.utc.localize(bid_id.bid_closing_date, is_dst=None).astimezone(tz)
                values.update({
                    'bid_closing_date': bid_closing_date.strftime('%d/%m/%Y %I:%M %p')
                })
            response = request.render("ki_crm_bid.crm_Bid_portal_form_view_new", values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        else:
            return request.redirect(bid_id.access_url)

    @http.route('/bid/master/<int:bid_id>', type='http', auth='user', website=True)
    def portal_bid_master_create(self, bid_id, **kw):
        if not request.env.user.has_group('ki_crm_bid.group_enable_bid_access'):
            return request.redirect('/my')
        try:
            bid_id = request.env['crm.bid'].browse(bid_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if not bid_id:
            return request.redirect('/bid/create')
        values = self._set_bit_values()
        error, error_message = self.details_Bid_form_validate(kw, bid_id)
        values.update({'error': error, 'error_message': error_message})
        if not error:
            if not bid_id.crm_lead_id:
                bid_id.action_master_opportunity(for_website=True)
            response = request.render("ki_crm_bid.bid_master_thankyou", {
                'opportunity_url': bid_id.access_url
            })
            return response
        if type(bid_id) not in (float, int) and bid_id:
            tz_name = request.env.user.tz or request._context.get('tz')
            if not tz_name:
                raise ValidationError(
                    _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
            tz = pytz.timezone(tz_name)
            bid_closing_date = pytz.utc.localize(bid_id.bid_closing_date, is_dst=None).astimezone(tz)
            values.update({
                'bid_closing_date': bid_closing_date.strftime('%d/%m/%Y %I:%M %p')
            })
        values.update({
            'bid_id': bid_id
        })
        response = request.render("ki_crm_bid.crm_Bid_portal_form_view_new", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def details_Bid_form_validate(self, data, bid_id=False):
        error = dict()
        error_message = []

        if bid_id:
            bid = bid_id.read()
            for field_name in self.MANDATORY_CRM_TENDER_FIELDS + self.OPTIONAL_CRM_TENDER_FIELDS:
                if not bid[0].get(field_name) and field_name not in ['file_upload', 'description', 'priority']:
                    error[field_name] = 'missing'
        else:
            for field_name in self.MANDATORY_CRM_TENDER_FIELDS:
                if not data.get(field_name):
                    error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data if k not in self.MANDATORY_CRM_TENDER_FIELDS + self.OPTIONAL_CRM_TENDER_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))
        return error, error_message
