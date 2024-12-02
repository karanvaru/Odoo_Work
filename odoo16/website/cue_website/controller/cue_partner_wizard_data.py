from odoo import http
from odoo.http import request


class CuePartnerWizardSubmit(http.Controller):
    @http.route('/cue_partner_wizard_submit/', auth="public", type="json", methods=['POST'])
    def cue_partner_wizard_submit(self, **_kwargs):
        vals = {
            'name': _kwargs['name'],
            'phone': _kwargs['phone'],
            'web_lead_type': 'partner',
            # 'city': _kwargs['city'],
            'lead_city_id': _kwargs['city'],
            'home_status': _kwargs['status'],
            'state_id': _kwargs['state_id']
        }
        request.env['crm.lead'].sudo().create(vals)

    @http.route('/cue_wizard_partner_state/', auth="public", type="json", methods=['POST'])
    def cue_wizard_partner_state(self, **_kwargs):
        if _kwargs['partner_state'] is not None:
            state = int(_kwargs['partner_state'])
            partner_cities = http.request.env['res.city'].sudo().search([('state_id', '=', int(state))])
            return {
                'message': request.env['ir.ui.view']._render_template("cue_website.template_partner_city_wizards", {
                    'partner_cities': partner_cities,
                })
            }

    # @http.route('/cue_partner_wizard_submit/', auth="public", type="json", methods=['POST'])
    # def cue_partner_wizard_submit(self, **_kwargs):
    #     vals = {
    #         'name': _kwargs['name'],
    #         'phone': _kwargs['phone'],
    #         'web_lead_type': 'partner',
    #         'city': _kwargs['city'],
    #         'exist_partner': _kwargs['exist_partner'],
    #     }
    #     request.env['crm.lead'].sudo().create(vals)
    #
    # @http.route('/PartnerCityWizard/', auth="public", type="json", methods=['POST'])
    # def partner_city_wizard(self):
    #     cities = http.request.env['res.city'].sudo().search([])
    #
    #     return {
    #         'message': request.env['ir.ui.view']._render_template("cue_website.template_partner_city_wizard", {
    #             'cities': cities,
    #         })
    #     }
