# -*- coding: utf-8 -*-

from collections import OrderedDict

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        values['custom_estimate_count'] = request.env['sale.estimate'].sudo().search_count(domain)
        return values

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        values.update({
            'custom_estimate_count': request.env['sale.estimate'].sudo().search_count(domain)
        })
        return values

    @http.route(['/my/estimates', '/my/estimates/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_estimates(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []

            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            
            domain += search_domain

        # estimate count
        custom_estimate_count = request.env['sale.estimate'].sudo().search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/estimates",
            url_args={
                'date_begin': date_begin,
                'date_end': date_end,
                'sortby': sortby,
                'filterby': filterby
            },
            total=custom_estimate_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        
        estimates = request.env['sale.estimate'].sudo().search(domain, order=order,
                                                   limit=self._items_per_page,
                                                   offset=pager['offset'])
        request.session['my_estimates_history'] = estimates.ids[:100]


        values.update({
            'date': date_begin,
            'date_end': date_end,
            'estimates': estimates,
            'page_name': 'sub_estimates',
            'default_url': '/my/estimates',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("sale_estimate_customer_portal.portal_my_estimates", values)

    # @http.route(['/estimate_report/print/pdf/<int:estimate_id>'], type='http', auth="public", website=True)
    # def portal_estimate_report(self, **kw):
    #     estimate_id = kw['estimate_id']
    #     if estimate_id:
    #         # pdf = request.env.ref('odoo_sale_estimates.report_estimate_information').sudo().render_qweb_pdf([estimate_id])[0] #odoo13
    #         pdf = request.env.ref('odoo_sale_estimates.report_estimate_information').sudo()._render_qweb_pdf([estimate_id])[0] #odoo14
    #         pdfhttpheaders = [
    #             ('Content-Type', 'application/pdf'),
    #             ('Content-Length', len(pdf)),
    #         ]
    #         return request.make_response(pdf, headers=pdfhttpheaders)
    #     else:
    #         return request.redirect('/')

    @http.route(['/estimate_report/print/pdf/<model("sale.estimate"):estimate_id>'], type='http', auth="user", website=True)
    def portal_estimate_report_customs(self, estimate_id, access_token=None, report_type='pdf', download=False, **kw):
        try:
            estimate_order_sudo = self._document_check_access('sale.estimate', estimate_id.id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=estimate_order_sudo, report_type=report_type, report_ref='odoo_sale_estimates.report_estimate_information', download=download)

        return request.redirect('/my')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
