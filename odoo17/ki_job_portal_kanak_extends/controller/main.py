import base64
import json
import logging
from datetime import datetime
from werkzeug.exceptions import NotFound

from odoo import http, _
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

logger = logging.getLogger(__name__)


class WebsiteHrRecruitmentCustom(WebsiteHrRecruitment):
    @http.route('''/jobs/apply/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''',
                type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        field_value = request.env['recruitment.document.type'].sudo().search([])
        additional_info = []
        for rec in field_value:
            if str(rec.id) in kwargs:
                value = kwargs[str(rec.id)]
                additional_info += [(0, 0, {
                    'document': base64.encodebytes(value.read()),
                    'document_type_id': rec.id,
                    'document_name': value.filename
                })]
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
                                vals.get('start_date'), DEFAULT_SERVER_DATE_FORMAT)
                            start_date = datetime.strftime(
                                f_start_date, DEFAULT_SERVER_DATE_FORMAT)
                            f_end_date = datetime.strptime(
                                vals.get('end_date'), DEFAULT_SERVER_DATE_FORMAT)
                            end_date = datetime.strftime(
                                f_end_date, DEFAULT_SERVER_DATE_FORMAT)
                            academic_info += [(0, 0, {
                                'course_name': vals.get('course_name') or '',
                                'branch': vals.get('branch') or '',
                                'organization': vals.get('organization') or '',
                                'start_date': start_date,
                                'end_date': end_date,
                                'marks': vals.get('marks') if vals.get('marks') else 0,
                            })]
                    if load_json_datas.get('certificate_details'):
                        for vals in load_json_datas.get('certificate_details'):
                            f_start_date = datetime.strptime(
                                vals.get('start_date'), DEFAULT_SERVER_DATE_FORMAT)
                            start_date = datetime.strftime(
                                f_start_date, DEFAULT_SERVER_DATE_FORMAT)
                            f_end_date = datetime.strptime(
                                vals.get('end_date'), DEFAULT_SERVER_DATE_FORMAT)
                            end_date = datetime.strftime(
                                f_end_date, DEFAULT_SERVER_DATE_FORMAT)
                            certificate_info += [(0, 0, {
                                'course_name': vals.get('course_name') or '',
                                'branch': vals.get('branch') or '',
                                'organization': vals.get('organization') or '',
                                'start_date': start_date,
                                'end_date': end_date,
                                'certificate_des': vals.get('certificate_des') or '',
                                'attachment_ids': [(0, 0,
                                                    {'name': vals.get('filename'), 'res_model': 'certificate.detail',
                                                     'datas': bytes(vals.get('filedata'), 'utf-8'),
                                                     'mimetype': vals.get('filetype')})] if vals.get(
                                    'filename') else False
                            })]
                    if load_json_datas.get('professional_details'):
                        for vals in load_json_datas.get('professional_details'):
                            f_start_date = datetime.strptime(
                                vals.get('start_date'), DEFAULT_SERVER_DATE_FORMAT)
                            start_date = datetime.strftime(
                                f_start_date, DEFAULT_SERVER_DATE_FORMAT)
                            f_end_date = datetime.strptime(
                                vals.get('end_date'), DEFAULT_SERVER_DATE_FORMAT)
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
                        birthday = f_birthday

                    except ValueError as e:
                        logger.warning(e)
                values = {
                    'name': '%s\'s Application' % kwargs.get('partner_name'),
                    'partner_name': kwargs.get('partner_name') or '',
                    'last_name': kwargs.get('last_name') or '',
                    'email_from': kwargs.get('email_from') or '',
                    'gender': kwargs.get('gender') or False,
                    'country_of_birth': int(kwargs.get('country_of_birth')) if kwargs.get(
                        'country_of_birth') else False,
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
                    'recruitment_agent_id':  kwargs.get('agent') or False,
                    'description': kwargs.get('description') or '',
                    'personal_detail_ids': academic_info if academic_info else False,
                    'certificate_detail_ids': certificate_info if certificate_info else False,
                    'professional_detail_ids': professional_info if professional_info else False,
                    'middle_name': kwargs.get('middle_name') or '',
                    'country_of_nationality': int(kwargs.get('country_of_nationality')) if kwargs.get(
                        'country_of_nationality') else False,
                    'age': kwargs.get('age') or '',
                    'citizenship': kwargs.get('citizenship') or '',

                    'most_work_experience': kwargs.get('work_experience') or '',
                    'number_years_in_trade': kwargs.get('number_years') or '',
                    'hours_work_per_day': kwargs.get('many_hours_per_day') or '',
                    'days_work_per_week': kwargs.get('many_days_per_week') or '',
                    'weeks_per_month': kwargs.get('many_week_per_month') or '',
                    'month_per_year': kwargs.get('many_month_per_year') or '',
                    'year_per_5_10_year': kwargs.get('many_years_last_5to10') or '',
                    'describe_detail': kwargs.get('describe_in_detail') or '',
                    'complete_high_school_year': kwargs.get('year_complete_high_school') or '',
                    'varify_experience': kwargs.get('varify_word') or '',

                    'is_complete_high_school': 'yes' if kwargs.get('completed_high_school') == "True" else 'no',
                    'is_training': 'yes' if kwargs.get('training_trade') == "True" else 'no',
                    'is_other_trade_skill': 'yes' if kwargs.get('skilled_trade') == "True" else 'no',
                    'is_criminal_offence': 'yes' if kwargs.get('charged_criminal') == "True" else 'no',
                    'is_applied_visa': 'yes' if kwargs.get('applied_for_visa') == "True" else 'no',
                    'travelled_by_plane': 'yes' if kwargs.get('outside_country') == "True" else 'no',
                    'is_denied_visa': 'yes' if kwargs.get('denied_visa') == "True" else 'no',

                    # 'education_level': kwargs.get('education_level') or '',
                    # 'trade_applied': kwargs.get('trade_applied') or '',
                    # 'report_no_year': kwargs.get('trade_year') or '',
                    # 'report_hour_per_day': kwargs.get('hour_per_day') or '',
                    # 'report_day_per_week': kwargs.get('day_per_week') or '',
                    # 'report_week_per_month': kwargs.get('week_per_month') or '',
                    # 'report_month_per_year': kwargs.get('month_per_year') or '',
                    # 'year_work5_10': kwargs.get('year_trade_5_10') or '',
                    #
                    # 'report_is_training':  'yes' if kwargs.get('is_training') == "True" else 'no',
                    # 'report_is_skill': 'yes' if kwargs.get('trades_skilled') == "True" else 'no',
                    'application_document_ids': additional_info,
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
