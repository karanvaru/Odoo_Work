# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import base64
import json
import logging
from datetime import datetime
from werkzeug.exceptions import NotFound

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
logger = logging.getLogger(__name__)


class WebsiteHrRecruitmentCustom(WebsiteHrRecruitment):
    @http.route('''/jobs/apply/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''', type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()

        error = {}
        default = {}
        country_ids = request.env['res.country'].sudo().search([])
        state_ids = request.env['res.country.state'].sudo().search([])

        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        if 'submitted' in kwargs:
            try:
                academic_info = []
                certificate_info = []
                professional_info = []
                if kwargs.get('all_details_data'):
                    datas = kwargs.get('all_details_data')
                    load_json_datas = json.loads(datas)
                    if load_json_datas.get('academic_details'):
                        for vals in load_json_datas.get('academic_details'):
                            f_start_date = datetime.strptime(
                                vals.get('start_date'), '%m/%d/%Y')
                            start_date = datetime.strftime(
                                f_start_date, DEFAULT_SERVER_DATE_FORMAT)
                            f_end_date = datetime.strptime(
                                vals.get('end_date'), '%m/%d/%Y')
                            end_date = datetime.strftime(
                                f_end_date, DEFAULT_SERVER_DATE_FORMAT)
                            academic_info += [(0, 0, {
                                'course_name': vals.get('course_name') or '',
                                'branch': vals.get('branch') or '',
                                'organization': vals.get('organization') or '',
                                'start_date': start_date,
                                'end_date': end_date,
                                'marks': float(vals.get('marks')) if vals.get('marks') else 0,
                            })]
                    if load_json_datas.get('certificate_details'):
                        for vals in load_json_datas.get('certificate_details'):
                            f_start_date = datetime.strptime(
                                vals.get('start_date'), '%m/%d/%Y')
                            start_date = datetime.strftime(
                                f_start_date, DEFAULT_SERVER_DATE_FORMAT)
                            f_end_date = datetime.strptime(
                                vals.get('end_date'), '%m/%d/%Y')
                            end_date = datetime.strftime(
                                f_end_date, DEFAULT_SERVER_DATE_FORMAT)
                            certificate_info += [(0, 0, {
                                'course_name': vals.get('course_name') or '',
                                'branch': vals.get('branch') or '',
                                'organization': vals.get('organization') or '',
                                'start_date': start_date,
                                'end_date': end_date,
                                'certificate_des': vals.get('certificate_des') or '',
                                'attachment_ids': [(0, 0, {'name': vals.get('filename'), 'res_model': 'certificate.detail', 'datas': bytes(vals.get('filedata'), 'utf-8'), 'mimetype': vals.get('filetype')})] if vals.get('filename') else False
                            })]
                    if load_json_datas.get('professional_details'):
                        for vals in load_json_datas.get('professional_details'):
                            f_start_date = datetime.strptime(
                                vals.get('start_date'), '%m/%d/%Y')
                            start_date = datetime.strftime(
                                f_start_date, DEFAULT_SERVER_DATE_FORMAT)
                            f_end_date = datetime.strptime(
                                vals.get('end_date'), '%m/%d/%Y')
                            end_date = datetime.strftime(
                                f_end_date, DEFAULT_SERVER_DATE_FORMAT)
                            professional_info += [(0, 0, {
                                'name': vals.get('name') or '',
                                'department': vals.get('department') or '',
                                'organization': vals.get('organization') or '',
                                'work_des': vals.get('work_des') or '',
                                'work_exp': vals.get('work_exp') or '',
                                'start_date': start_date,
                                'end_date': end_date,
                                'projects': vals.get('projects') or '',
                            })]
                birthday = False
                if kwargs.get('birthday') and kwargs.get('birthday').strip():
                    try:
                        f_birthday = datetime.strptime(kwargs.get('birthday'), '%m/%d/%Y')
                        birthday = datetime.strftime(f_birthday, DEFAULT_SERVER_DATE_FORMAT)
                    except ValueError as e:
                        logger.warning(e)
                values = {
                    'name': '%s\'s Application' % kwargs.get('partner_name'),
                    'partner_name': kwargs.get('partner_name') or '',
                    'last_name': kwargs.get('last_name') or '',
                    'email_from': kwargs.get('email_from') or '',
                    'gender': kwargs.get('gender') or False,
                    'country_of_birth': int(kwargs.get('country_of_birth')) if kwargs.get('country_of_birth') else False,
                    'marital': kwargs.get('marital') or False,
                    'partner_phone': kwargs.get('partner_phone') or '',
                    'partner_mobile': kwargs.get('partner_phone') or '',
                    'address1': kwargs.get('address1') or '',
                    'address2': kwargs.get('address2') or '',
                    'city': kwargs.get('city') or '',
                    'zipcode': kwargs.get('zipcode') or '',
                    'birthday': birthday,
                    'country_id': int(kwargs.get('country_id')) if kwargs.get('country_id') else False,
                    'state_id': int(kwargs.get('state_id')) if kwargs.get('state_id') else False,
                    'job_id': job.id if job else False,
                    'description': kwargs.get('description') or '',
                    'personal_detail_ids': academic_info if academic_info else False,
                    'certificate_detail_ids': certificate_info if certificate_info else False,
                    'professional_detail_ids': professional_info if professional_info else False
                }

                rec = request.env['hr.applicant'].sudo().create(values)
                if rec and 'Resume' in kwargs:
                    file = kwargs.get('Resume')
                    if file:
                        attachment_value = {
                            'name': file.filename,
                            'datas': base64.encodebytes(file.read()),
                            'res_model': 'hr.applicant',
                            'res_id': rec.id,
                        }
                        request.env['ir.attachment'].sudo().create(
                            attachment_value)
                if rec:
                    base_url = request.env['ir.config_parameter'].sudo(
                    ).get_param('web.base.url')
                    access_url = base_url + '/my/applications/' + \
                        str(rec.id) + '?access_token=' + rec.access_token
                    return request.redirect('/job-thank-you?access_url=%s' % (access_url))
            except Exception as e:
                response = request.render("website_hr_recruitment.apply", {
                    'job': job,
                    'error': e,
                    'default': default,
                    'country_ids': country_ids,
                    'state_ids': state_ids
                })
                return response
        response = request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
            'country_ids': country_ids,
            'state_ids': state_ids
        })
        return response

    @http.route('/change_country', type='json', auth="public", website=True)
    def change_country(self, **kwargs):
        states_list = []
        if kwargs.get('country_id'):
            states = request.env['res.country.state'].sudo().search(
                [('country_id', '=', int(kwargs.get('country_id')))])
            for vals in states:
                states_list.append({'name': vals.name, 'id': vals.id})
            return states_list

    @http.route('/job/add/row', type='json', auth="public", methods=['POST'], website=True)
    def add_job_row(self, **kwargs):
        if kwargs.get('type') == 'personal':
            data = request.env['ir.ui.view']._render_template(
                "job_portal_kanak.add_acadamic_info")
            return {'data': data, 'type': 'personal'}
        if kwargs.get('type') == 'certificate':
            data = request.env['ir.ui.view']._render_template(
                "job_portal_kanak.add_certificate_info")
            return {'data': data, 'type': 'certificate'}
        if kwargs.get('type') == 'professional':
            data = request.env['ir.ui.view']._render_template(
                "job_portal_kanak.add_professional_info")
            return {'data': data, 'type': 'professional'}


class JobPortalKanak(http.Controller):
    @http.route(['/add/jobs'], type='http', auth="user", website=True)
    def add_jobs(self, **kwargs):
        user = request.env.user
        if not user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            return request.redirect('/')
        values = {}
        areas_ids = request.env['hr.functional'].sudo().search([])
        categories_ids = request.env['hr.department'].sudo().search([])
        values = {
            'areas_ids': areas_ids,
            'categories_ids': categories_ids,
            'error': None
        }
        if 'submitted' in kwargs:
            try:
                close_date = False
                if 'close_date' in kwargs and kwargs.get('close_date'):
                    t_close_date = datetime.strptime(
                        kwargs.get('close_date'), '%m/%d/%Y')
                    close_date = datetime.strftime(
                        t_close_date, DEFAULT_SERVER_DATE_FORMAT)
                function_ids = request.httprequest.form.getlist(
                    'functional_area')
                functional_area_ids = []
                if function_ids:
                    for val in function_ids:
                        functional_area_ids.append(int(val))
                datas = {
                    'name': kwargs.get('name') or '',
                    'department_id': int(kwargs.get('department_id')) if kwargs.get('department_id') else False,
                    'no_of_recruitment': int(kwargs.get('no_of_recruitment')) if kwargs.get('no_of_recruitment') else 0,
                    'description': kwargs.get('description') or '',
                    'functional_area': [(6, 0, functional_area_ids)] if functional_area_ids else False,
                    'close_date': close_date if close_date else False,
                    'user_id': request.env.user.id,
                    'website_published': True,
                    'website_id': request.website.id
                }
                rec = request.env['hr.job'].sudo().create(datas)
                if rec:
                    return request.redirect('/successfully/post/job')
            except Exception as e:
                values['error'] = e
                res = request.render('job_portal_kanak.add_job', values)
                return res
        response = request.render('job_portal_kanak.add_job', values)
        return response

    @http.route(['/successfully/post/job'], type='http', auth="user", website=True)
    def thanhs_for_posting_job(self):
        return request.render('job_portal_kanak.thanks_for_posting_job')


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        HrApplicant = request.env['hr.applicant'].sudo()
        applicant_count = HrApplicant.search_count(
            [('partner_id', '=', partner.id)])

        values.update({
            'applicant_count': applicant_count,
        })
        return values

    @http.route(['/my/applications', '/my/applications/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_application(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        HrApplicant = request.env['hr.applicant'].sudo()

        domain = [('partner_id', '=', partner.id)]

        searchbar_sortings = {
            'date': {'label': _('Application Date'), 'order': 'create_date desc'},
            'name': {'label': _('Reference'), 'order': 'applicant_number'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        applicant_count = HrApplicant.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/applications",
            url_args={'date_begin': date_begin,
                      'date_end': date_end, 'sortby': sortby},
            total=applicant_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        applications = HrApplicant.search(
            domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'applications': applications.sudo(),
            'page_name': 'applications',
            'pager': pager,
            'default_url': '/my/applications',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("job_portal_kanak.portal_my_applications", values)

    @http.route(['/my/applications/<int:application_id>'], type='http', auth="public", website=True)
    def portal_application_page(self, application_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            application_sudo = self._document_check_access(
                'hr.applicant', application_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = {
            'application': application_sudo,
            'token': access_token,
        }
        return request.render('job_portal_kanak.job_application_portal_template', values)
