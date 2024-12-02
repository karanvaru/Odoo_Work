from odoo import api, fields, models, _

class HrApplicantPortal(models.Model):
    _inherit = 'hr.applicant'

    employee_code = fields.Char('RDP Employee Code',track_visibility="always")

    def website_form_input_filter(self, request, values):
        if request.params.get('employee_code'):
            values.update({'employee_code': request.params.get('employee_code')})
        return super().website_form_input_filter(request, values)
