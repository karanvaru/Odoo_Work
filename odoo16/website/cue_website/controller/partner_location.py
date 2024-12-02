from odoo import http
from odoo.http import request


class PartnerLocation(http.Controller):

    @http.route('/partnerlocation/', auth="public", type="json", methods=['POST'])
    def all_location(self):
        
        partner_id_categ = http.request.env['res.partner.category'].sudo().search([('name', '=',  'Partner')])

        domain = []
        if partner_id_categ:
            domain.append(('category_id', 'in', partner_id_categ.id))
        partner_ids = http.request.env['res.partner'].sudo().search(domain)
        
        cities = partner_ids.mapped('city_id')
        states = cities.mapped('state_id')
#         cities = http.request.env['res.city'].sudo().search([('country_id.code', 'ilike', 'IN')])
#         states = cities.mapped('state_id')
        
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_location_options", {
                'cities': cities,
                'states': states
            })
        }

    @http.route('/partnerlocationcity/', auth="public", type="json", methods=['POST'])
    def all_location_city(self, **_kwargs):
        state = _kwargs['city_state']
        city_list = []
        if state and state != 'state_select':
            state_id = int(state)
            
            partner_id_categ = http.request.env['res.partner.category'].sudo().search([('name', '=',  'Partner')])
            domain = []
            if partner_id_categ:
                domain.append(('category_id', 'in', partner_id_categ.id))
            domain += [('state_id.id', '=', state_id)]
            partner_ids = http.request.env['res.partner'].sudo().search(domain)
            
            cities = partner_ids.mapped('city_id')
            
#             cities = http.request.env['res.city'].sudo().search([('state_id.id', '=', state_id)])
            for c in cities:
                city_list.append(c)
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_location_options_city", {
                'cities': city_list,
            })
        }
