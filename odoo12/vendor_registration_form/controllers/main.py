# -*- coding: utf-8 -*-

import base64
from odoo import http, _
from odoo.http import request


class CustomWebsiteMembership(http.Controller):
    @http.route([
        '''/custom_vendor_request/details'''
    ], type='http', auth="public", website=True)
    def custom_vendor_request_details(self, timeout=15, **post):
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        partner = request.env.user.partner_id
        product_categorys = request.env['product.category'].sudo().search([('custom_display_on_vendor_registration', '=', True)])

        if 'vat' in post:
            existing_partner = request.env['res.partner'].sudo().search([('vat', '=', post['vat'])], limit=1)
            if existing_partner:
                vals = {
                    'message': "You are already registered with this GST number.",
                }
                return http.request.render('vendor_registration_form.Vendor_Enquiry_Form_company_gst', vals)
            else:
                # Fetching details using External API
                vies_vat_data, _ = request.env['res.partner'].sudo()._rpc_remote_api(
                    'search_vat',
                    {'vat': post['vat'], }, timeout=timeout)
                if not vies_vat_data:
                    vals = {
                        'message': "No Details Found For GST Number",
                    }
                    return http.request.render('vendor_registration_form.Vendor_Enquiry_Form_company_gst', vals)
                else:
                    name = vies_vat_data.get('name', '')
                    street = vies_vat_data.get('street', '')
                    city = vies_vat_data.get('city', '')
                    zip_code = vies_vat_data.get('zip', '')
                    email = vies_vat_data.get('email', '')

                    vals = {
                        'countries': countries,
                        'states': states,
                        'partner': partner,
                        'gst_value': post['vat'],
                        'gst_autocomplete': {
                            'name': name,
                            'street1': street,
                            'city': city,
                            'zip': zip_code,
                            'email': email
                        }
                    }

        else:
            vals = {
                'countries': countries,
                'states': states,
                'partner': partner,
            }
        return http.request.render('vendor_registration_form.custom_portal_create_vendor_request', vals)

        # values = {
        #     'countries': countries,
        #     'states': states,
        #     'product_categorys': product_categorys,
        # }
        # return request.render(
        #     "vendor_registration_form.custom_portal_create_vendor_request",
        #     values
        # )

    @http.route('/company_registration_gst', type='http', auth='public', website=True)
    def company_registration(self, **kw):
        return http.request.render('vendor_registration_form.Vendor_Enquiry_Form_company_gst')



    @http.route([
        '''/vendor_registration_menu'''
    ], type='http', auth="public", website=True)
    def vendor_registration_menu_page(self, **post):
        return request.render(
            "vendor_registration_form.vendor_registration_templates",
        )


    @http.route([
        '''/create/custom_vendor_request'''
    ], type='http', auth="public", website=True)
    def custom_create_vendor_request(self, **post):
        vals ={
            'company_type': post.get('vendor_type', 'person'),
            'name': post.get('name', ''),
            'vat': post.get('vat', ''),
            'email': post.get('email', ''),
            'phone': post.get('phone', ''),
            'mobile': post.get('mobile', ''),
            'street': post.get('street', ''),
            'street2': post.get('street2', ''),
            'city': post.get('city', ''),
            'zip': post.get('zipcode', ''),
            'country_id': int(post.get('country_id', False)),
            'state_id': int(post.get('state_id', False)) if post.get('state_id') else None,
            'website': post.get('website_link', ''),
            'x_studio_services': post.get('x_studio_services', ''),
            'x_studio_company_turnover':post.get('x_studio_company_turnover',''),
#             'x_studio_established_in': post.get('x_studio_established_in', ''),
            'x_studio_field_C6Cal': post.get('x_studio_field_C6Cal', ''),
            'x_studio_top_5_customers_for_reference': post.get('x_studio_top_5_customers_for_reference', ''),
            'x_studio_last_2_yr_avg_revenue_in_crores': post.get('x_studio_last_2_yr_avg_revenue_in_crores', ''),
            'x_studio_social_contact_skypewechatother': post.get('x_studio_social_contact_skypewechatother', ''),
           # 'x_studio_company_profile_1' : post.get('company_profile', ''),
            'supplier_rank':1,
            'customer':False,
            'supplier':True,
            'comment': post.get('comment', ''),
        }

        if post.get('x_studio_established_in', False):
            vals.update({
                'x_studio_established_in': post.get('x_studio_established_in', '')
            })

        if post.get('company_profile', False):
            company_profile = post.get('company_profile').read()
            # company_profile_name = company_profile.name
            # cp = request.env['ir.attachment'].sudo().create({
            # 'name':company_profile_name,
            # 'datas_fname': company_profile_name,
            # 'res_name': company_profile_name,
            # 'type': 'binary',
            # 'res_model': 'res.partner',
            # # 'res_id': project_id,
            # 'datas': base64.b64encode(company_profile),
            # })

            vals.update({
                'x_studio_company_profile_1': base64.b64encode(company_profile)
            })
        if post.get('company_reg', False):
            company_reg = post.get('company_reg').read()
            vals.update({
                'x_studio_company_registration_1': base64.b64encode(company_reg)
            })
        if post.get('product_road_map', False):
            product_road_map = post.get('product_road_map').read()
            vals.update({
                'x_studio_product_road_map_1': base64.b64encode(product_road_map)
            })
        if post.get('qc_doc', False):
            qc_doc = post.get('qc_doc').read()
            vals.update({
                'x_studio_quality_control_doc_1': base64.b64encode(qc_doc)
            })


        if post.get('selected_vendor_product_category', False):
            selected_category = str(post.get('selected_vendor_product_category'))
            vals.update({
                'custom_product_category_ids': [(6, 0, list(tuple(map(int, selected_category.split(',')))))]
            })
        if post.get('vendor_image'):
            image = post.get('vendor_image').read()
            vals.update({
                'image': base64.b64encode(image),
            })
        if post.get('major_supplier'):
            vals.update({
                'custom_major_supplier_of_item': post.get('major_supplier')
            })
        partner_id = request.env['res.partner'].sudo().create(vals)
        if partner_id:
            if post.get('child1_name', False):
                child1_vals = {
                    'company_type': 'person',
                    'parent_id': partner_id.id,
                    'name': post.get('child1_name', ''),
                    'email': post.get('child1_email', ''),
                    'phone': post.get('child1_phone', ''),
                    'function': post.get('child1_job', ''),
                }
                child1_id = request.env['res.partner'].sudo().create(child1_vals)
            if post.get('child2_name', False):
                child2_vals = {
                    'company_type': 'person',
                    'parent_id': partner_id.id,
                    'name': post.get('child2_name', ''),
                    'email': post.get('child2_email', ''),
                    'phone': post.get('child2_phone', ''),
                    'function': post.get('child2_job', ''),
                }
                child2_id = request.env['res.partner'].sudo().create(child2_vals)
            if post.get('child3_name', False):
                child3_vals = {
                    'company_type': 'person',
                    'parent_id': partner_id.id,
                    'name': post.get('child3_name', ''),
                    'email': post.get('child3_email', ''),
                    'phone': post.get('child3_phone', ''),
                    'function': post.get('child3_job',''),
                }
                child3_id = request.env['res.partner'].sudo().create(child3_vals)
            template = request.env.ref('vendor_registration_form.custom_mail_template_vendor_registration_request')
            template.sudo().send_mail(partner_id.id)
            
        return request.render(
            "vendor_registration_form.custom_vanver_child_successfully_created_message"
        )
