from odoo import http
from odoo.http import request


class CueWizardSubmitData(http.Controller):
    @http.route('/cue_wizard_submit/', auth="public", type="json", methods=['POST'])
    def cue_wizard_submit_data(self, **_kwargs):
        vals = {
            'name': _kwargs['name'],
            'phone': _kwargs['phone'],
            'web_lead_type': 'user',
            # 'city': _kwargs['city'],
            'lead_city_id': _kwargs['city'],
            'home_status': _kwargs['status'],
            'state_id': _kwargs['state_id']
        }
        request.env['crm.lead'].sudo().create(vals)

    @http.route('/cue_wizard_user_state/', auth="public", type="json", methods=['POST'])
    def cue_wizard_user_state(self, **_kwargs):
        if _kwargs['user_state'] is not None:
            state = int(_kwargs['user_state'])
            user_cities = http.request.env['res.city'].sudo().search([('state_id', '=', int(state))])
            return {
                'message': request.env['ir.ui.view']._render_template("cue_website.template_user_city_wizards", {
                    'user_cities': user_cities,
                })
            }

    # @http.route('/UserCityWizard/', auth="public", type="json", methods=['POST'])
    # def user_city_wizard(self):
    #     cities = http.request.env['res.city'].sudo().search([])
    #
    #     return {
    #         'message': request.env['ir.ui.view']._render_template("cue_website.template_user_city_wizard", {
    #             'cities': cities,
    #         })
    #     }
