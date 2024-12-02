from odoo import http
from odoo.http import request
from datetime import datetime
import datetime
import base64


class RecruitmentAcademic(http.Controller):

    @http.route('/RecruitmentAcademicdata/', auth="public", type="json", methods=['POST'])
    def recruitment_academy_data(self, **_kwargs):
        recruitment = request.env['recruitment.academic'].sudo().search([])
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.cue_recruitment_form", {
                'recruitment': recruitment,
            })
        }

    @http.route('/RecruitmentAcademic', type='http', auth="public", website=True, csrf=False)
    def recruitment_from_data(self, **kw):
        if kw:
            dob = kw['dob']
            dob = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
            document = False
            academic_id = False
            if 'cv' in kw:
                for a in request.httprequest.files.getlist('cv'):
                    document = a
            if 'academics_list' in kw:
                academic_id = kw['academics_list']

            vals = {
                'name': kw['firstname'],
                'date_of_birth': dob,
                'phone': kw['phone'],
                'email': kw['email'],
                'specialization': kw['specialization'],
                'academic_id': academic_id,
                'description': kw['description'],
                'attachment_name': document.filename,
                'resume': base64.b64encode(document.read()),

            }
            request.env['job.requests'].sudo().create(vals)
            return request.render("cue_website.response_thanks", {})