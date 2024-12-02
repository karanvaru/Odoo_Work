from odoo import http
from odoo.http import request


class ResPartnerInherit(http.Controller):

    @http.route('/ResPartnerInherit/', auth="public", type="json", methods=['POST'])
    def all_partner(self, **_kwargs):
        city = _kwargs.get('city_select', 0)
        state_id = _kwargs.get('state_id', 0)
        
        partner_id_categ = http.request.env['res.partner.category'].sudo().search([('name', '=',  'Partner')])

        domain = []
        if partner_id_categ:
            domain.append(('category_id', 'in', partner_id_categ.id))
        
        city_id = int(city)
        
        if city_id:
            domain.append(('city_id', '=', int(city)))
        if int(state_id):
            domain.append(('state_id', '=', int(state_id)))

        partner_id = http.request.env['res.partner'].sudo().search(domain)

        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_partner_location_options", {
                'partner': partner_id
            })
        }

    @http.route('/ResPartnerInheritList/', auth="public", type="json", methods=['POST'])
    def all_partner_list(self, **_kwargs):
        partner_id_categ = http.request.env['res.partner.category'].sudo().search([('name', '=',  'Partner')])
        domain = []
        if partner_id_categ:
            domain.append(('category_id', 'in', partner_id_categ.id))

        partner_id_list = http.request.env['res.partner'].sudo().search(domain)
        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_partner_location_options", {
                'partner': partner_id_list
            })
        }