from odoo.addons.affiliate_management.controllers.affiliate_website import website_affiliate
from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class WebsiteAffiliateInherit(website_affiliate):

    @http.route('/affiliate/signup', auth='public', type='http', website=True)
    def register(self, **kw):
        result = super(WebsiteAffiliateInherit, self).register(**kw)
        token = request.httprequest.args.get('token') or 0
        user = request.env['affiliate.request'].sudo().search(
            [('signup_token', '=', token)], limit=1)
        if user.signup_valid and user.state == 'draft':
            result.qcontext.update({
                'aff_key': user.parent_aff_key
            })
        return result

    @http.route('/affiliate/register', auth='public', type='http', website=True)
    def register_affiliate(self, **kw):
        result = super(WebsiteAffiliateInherit, self).register_affiliate(**kw)
        if result.headers.get('Location') == '/affiliate' and not request.session.get('error', None):
            aff_request = request.env['affiliate.request'].sudo().search(
                [("name", "=", kw.get("login") or kw.get("email"))])
            aff_request.parent_aff_key = kw.get("aff_key")
            # aff_request.partner_id.aff_request_id = aff_request.id
        return result

    @http.route('/affiliate/', auth='public', type='http', website=True)
    def affiliate(self, **kw):
        result = super(WebsiteAffiliateInherit, self).affiliate(**kw)
        benefit_text = request.env['res.config.settings'].sudo().get_default_benefits_values()
        result.qcontext.update({
            'benefit_text': benefit_text.get('benefit_text')
        })
        return result

    @http.route('/affiliate/about', type='http', auth="user", website=True)
    def affiliate_about(self, **kw):
        result = super(WebsiteAffiliateInherit, self).affiliate_about(**kw)
        benefit_text = request.env['res.config.settings'].sudo().get_default_benefits_values()
        result.qcontext.update({
            'benefit_text': benefit_text.get('benefit_text')
        })
        return result

    @http.route('/affiliate/report', type='http', auth="user", website=True)
    def report(self, **kw):
        result = super(WebsiteAffiliateInherit, self).report(**kw)
        partner = request.env.user.partner_id
        visits = request.env['affiliate.visit'].sudo()
        prntcmsn_visit = visits.search([('affiliate_method', '=', 'parentcommission'), ('affiliate_partner_id', '=', partner.id), '|', '|',
                                        ('state', '=', 'invoice'), ('state', '=', 'confirm'), ('state', '=', 'paid')])
        result.qcontext.update({
            'prntcmsn_visit_count': len(prntcmsn_visit)
        })
        return result

    @http.route(['/my/commission', '/my/commission/page/<int:page>'], type='http', auth="user", website=True)
    def parentCommission(self, page=1, date_begin=None, date_end=None, **kw):
        values = {}
        partner = request.env.user.partner_id
        visits = request.env['affiliate.visit'].sudo()
        domain = [('affiliate_partner_id', '=', partner.id), ('affiliate_method', '=', 'parentcommission'), '|', '|',
                  ('state', '=', 'invoice'), ('state', '=', 'confirm'), ('state', '=', 'paid')]
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        prnt_comsn_count = visits.search_count(domain)
        pager = request.website.pager(
            url='/my/traffic',
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=prnt_comsn_count,
            page=page,
            step=10
        )
        prnt_comsn = visits.search(domain, limit=10, offset=pager['offset'])
        values.update({
            'pager': pager,
            'traffic': prnt_comsn,
            'default_url': '/my/commission'
        })

        return http.request.render('affiliate_management_multitier.parentcommission', values)

    @http.route(['/my/commission/<int:traffic>'], type='http', auth="user", website=True)
    def aff_commission_form(self, traffic=None, **kw):
        prnt_comsn_visit = request.env['affiliate.visit'].sudo().browse([traffic])
        return request.render("affiliate_management_multitier.parent_commission_form", {
            'traffic_detail': prnt_comsn_visit,
            'product_detail': request.env['product.product'].browse([prnt_comsn_visit.type_id]),
        })
