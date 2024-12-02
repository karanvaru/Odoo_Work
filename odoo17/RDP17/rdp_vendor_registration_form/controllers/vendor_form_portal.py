# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import base64
import html
from werkzeug.utils import redirect


class CompanyVendorController(http.Controller):
    
    @http.route('/individual_registration', type='http', auth='public', website=True)
    def individual_registration(self, timeout=15, **kwargs):
        """
        Handle individual registration process.
        """
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        partner = request.env.user.partner_id

        # Check if GST number is already registered

        if 'vat' in kwargs:
            existing_partner = request.env['res.partner'].sudo().search([('vat', '=', kwargs['vat'])], limit=1)
            if existing_partner:
                vals = {
                    'message': "You are already registered with this GST number.",
                }
                return http.request.render('rdp_vendor_registration_form.Vendor_Enquiry_Form_company_gst', vals)
            else:
                # Fetching details using External API
                vies_vat_data, _ = request.env['iap.autocomplete.api'].sudo()._request_partner_autocomplete(
                    'search_vat',
                    {'vat': kwargs['vat'], }, timeout=timeout)
                if not vies_vat_data:
                    vals = {
                        'message': "No Details Found For GST Number",
                    }
                    return http.request.render('rdp_vendor_registration_form.Vendor_Enquiry_Form_company_gst', vals)
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
                        'gst_value': kwargs['vat'],
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
        return http.request.render('rdp_vendor_registration_form.Vendor_Enquiry_Form', vals)


    @http.route('/company_registration_gst', type='http', auth='public', website=True)
    def company_registration(self, **kw):
        return http.request.render('rdp_vendor_registration_form.Vendor_Enquiry_Form_company_gst')

    @http.route('/web_forms', type="http", auth="public", website=True)
    def le_webform(self):
        return http.request.render('rdp_vendor_registration_form.vendor_registration_template')

    @http.route('/samples', methods=['GET', 'POST', 'FILES'], type='http', auth='public', website=True)
    def vendor_enquiry_form(self, **kw):
        additional_title = "Vendor Registration"
        vendor_type = "company"
        states = request.env['res.country.state'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        product_categorys = request.env['product.category'].sudo().search([])
        error = {}
        # partner_values = {}c
        if request.httprequest.method == 'POST':
            post_data = request.httprequest.form.to_dict()
            print('post data is validating')

            if not post_data.get('name'):
                error['name'] = "Please enter company name."
            if not post_data.get('email'):
                error['email'] = "Please enter email address."
            if not post_data.get('phone'):
                error['phone'] = "Please enter phone number."
            if not post_data.get('mobile'):
                error['mobile'] = "Please enter mobile number."
            if not post_data.get('street'):
                error['street'] = "Please enter street address."
            if not post_data.get('city'):
                error['city'] = "Please enter city."
            if not post_data.get('state_id'):
                error['state_id'] = "Please select state."
            if not post_data.get('country_id'):
                error['country_id'] = "Please select country."


            if not error:
                print('data is saving in dict')
                # Save form data
                model = request.env['res.partner']

                company_profile_document = False
                for document in request.httprequest.files.getlist('company_profile'):
                    company_profile_document = document

                company_reg_document = False
                for document in request.httprequest.files.getlist('company_reg'):
                    company_reg_document = document

                product_road_map_document = False
                for document in request.httprequest.files.getlist('product_road_map'):
                    product_road_map_document = document

                qc_doc_document = False
                for document in request.httprequest.files.getlist('qc_doc'):
                    qc_doc_document = document

                vendor_image_document = False
                for document in request.httprequest.files.getlist('vendor_image'):
                    vendor_image_document = document

                vendor_type = False
                if post_data['x_studio_field_C6Cal'] == 'Manufacturer':
                    vendor_type = 'manufacturer'
                if post_data['x_studio_field_C6Cal'] == 'Trader':
                    vendor_type = 'trader'
                if post_data['x_studio_field_C6Cal'] == 'Manufacturer/Trader':
                    vendor_type = 'manufacturer_trader'
                if post_data['x_studio_field_C6Cal'] == 'Other':
                    vendor_type = 'other'

                revenue_category = False
                if post_data['x_studio_company_turnover'] == 'Less than 1 Crore':
                    revenue_category = 'rev_less_1_cr'
                if post_data['x_studio_company_turnover'] == '1 to 5 Crores':
                    revenue_category = 'rev_1_to_5'
                if post_data['x_studio_company_turnover'] == '5 to 25 Crores':
                    revenue_category = 'rev_5_to_25'
                if post_data['x_studio_company_turnover'] == '25 to 100 Crores':
                    revenue_category = 'rev_25_to_100'
                if post_data['x_studio_company_turnover'] == '100 to 250 Crores':
                    revenue_category = 'rev_100_to_250'
                if post_data['x_studio_company_turnover'] == '250 to 1000 Crores':
                    revenue_category = 'rev_250_to_1000'
                if post_data['x_studio_company_turnover'] == '1000+ Crores':
                    revenue_category = 'rev_1000_plus'

                vat_value = False
                company_type = False
                if 'vat' in kw:
                    vat_value = post_data['vat']
                    company_type = 'company'

                comment = post_data['comment']
                comments = '<p>' + comment.replace('\n', '<br/>') + '</p>'

                partner_values = {
                    'name': post_data['name'],
                    'email': post_data['email'],
                    'phone': post_data['phone'],
                    'mobile': post_data['mobile'],
                    'street': post_data['street'],
                    'street2': post_data['street2'],
                    'city': post_data['city'],
                    'state_id': int(post_data['state_id']),
                    'country_id': int(post_data['country_id']),
                    'vat': vat_value,
                    'company_type': company_type,
                    'zip': post_data['zipcode'],
                    'website': post_data['website_link'],
                    'company_profile': base64.b64encode(company_profile_document.read()),
                    'company_registration_certificate': base64.b64encode(company_reg_document.read()),
                    'product_road_map': base64.b64encode(product_road_map_document.read()),
                    'quality_control_document': base64.b64encode(qc_doc_document.read()),
                    'established_in': post_data['established_in'],
                    'revenue_category': revenue_category,
                    'last_2_year_avg_revenue': post_data['x_studio_last_2_yr_avg_revenue_in_crores'],
                    'social_contact': post_data['x_studio_social_contact_skypewechatother'],
                    'company_logo': base64.b64encode(vendor_image_document.read()),
                    'vendor_type': vendor_type,
                    'major_suppliers_of_product_components': post_data['major_supplier'],
                    'top_5_customers_for_reference': post_data['x_studio_top_5_customers_for_reference'],
                    'services': post_data['x_studio_services'],
                    'comment': comments,
                }
                
                existing_contact_email = request.env['res.partner'].sudo().search([('email', '=', post_data['email'])], limit=1)
                existing_contact_phone = request.env['res.partner'].sudo().search([('phone', '=', post_data['phone'])], limit=1)

                if existing_contact_email and existing_contact_phone:
                    # If both email and phone already exist
                    return http.request.render('rdp_vendor_registration_form.existing_contact_both_mail_and_phone_message')
                elif existing_contact_email:
                    # If only email already exists
                    return http.request.render('rdp_vendor_registration_form.existing_contact_E_mail_message')
                elif existing_contact_phone:
                    # If only phone already exists
                    return http.request.render('rdp_vendor_registration_form.existing_contact_Phone_message')
                else:
                    new_contact = False
                    # If no existing contact found, create a new one
                    try:
                        new_contact = request.env['res.partner'].sudo().create(partner_values)
                        if post_data['child1_name']:
                            request.env['res.partner'].sudo().create({
                                'name': post_data['child1_name'],
                                'function': post_data['child1_job'],
                                'email': post_data['child1_email'],
                                'phone': post_data['child1_phone'],
                                'parent_id': new_contact.id,
                            })
                        if post_data['child2_name']:
                            request.env['res.partner'].sudo().create({
                                'name': post_data['child2_name'],
                                'function': post_data['child2_job'],
                                'email': post_data['child2_email'],
                                'phone': post_data['child2_phone'],
                                'parent_id': new_contact.id,
                            })
                        if post_data['child3_name']:
                            request.env['res.partner'].sudo().create({
                                'name': post_data['child3_name'],
                                'function': post_data['child3_job'],
                                'email': post_data['child3_email'],
                                'phone': post_data['child3_phone'],
                                'parent_id': new_contact.id,
                            })

                        request.cr.commit()
                        if new_contact:
                            new_contact = new_contact.id
                        return http.request.render('rdp_vendor_registration_form.vendor_registration_success', {'id': new_contact})

                    except Exception as e:
                        print(f"Error creating contact: {e}")
                    # new_contact = request.env['res.partner'].create(partner_values)

                return http.request.make_response('error while saving')
        return http.request.render('rdp_vendor_registration_form.Vendor_Enquiry_Form')
