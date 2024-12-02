from odoo import http
from odoo.http import request


class HelpMe(http.Controller):

    @http.route('/action_prepare_question/', auth="public", type="json", methods=['POST'])
    def action_prepare_question(self, **kwargs):
        result = http.request.env['product.tag.category'].sudo().action_prepare_question()
        return result

    @http.route('/action_question_result/', auth="public", type="json", methods=['POST'])
    def action_question_result(self, **kwargs):
        print ("kwargs -----",kwargs)
        result = http.request.env['product.tag.category'].sudo().action_question_result(formData=kwargs['form_data'])
        return result