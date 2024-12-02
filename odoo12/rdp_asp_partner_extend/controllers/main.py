# -*- coding: utf-8 -*-

import base64
from odoo import http, _
from odoo.http import request


class CustomWebsiteASP(http.Controller):

    @http.route(['''/aspr'''], type="http", auth="public", website=True)
    def asp_ticket(self, **kw):
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        sericeable_product = request.env['service.product_cat'].sudo().search([])
        seiviceable_state = request.env['res.country.state'].sudo().search([])
        seiviceable_districts = request.env['service.districts'].sudo().search([])
        service_categorys = request.env['service.categories'].sudo().search([])
        service_type = request.env['service.types'].sudo().search([])
        service_delivery = request.env['service.delivery_by'].sudo().search([])
        locations = request.env['asp.locations'].sudo().search([])
        crms_used = request.env['asp.crms'].sudo().search([])
        other_brand = request.env['product.brand.amz.ept'].sudo().search([])
        asp_rec = request.env['asp.partner'].sudo().search([])
        # print("doctor_rec...", doctor_rec)
        return http.request.render('rdp_asp_partner_extend.aspr', 
        {
         'asp_rec': asp_rec,
         'countries': countries,
         'states': states,
         'sericeable_product': sericeable_product,
         'seiviceable_state': seiviceable_state,
         'seiviceable_districts': seiviceable_districts,
         'service_categorys': service_categorys,
         'service_type': service_type,
         'service_delivery': service_delivery,
         'locations': locations,
         'crms_used': crms_used,
         'other_brand': other_brand,
        
        })

    @http.route(['''/create/aspregistration'''], type="http", auth="public", website=True)
    def aspr(self, **kw):

        service_categories = []
        data_values = request.httprequest.values.to_dict(flat=False)
        
        service_categories = data_values.get('service_categories', []) #multi_selection
        service_categorie_ids = [int(i) for i in service_categories] #multi_selections

        service_product_cat = data_values.get('service_product_cat', [])
        service_product_cat_ids = [int(i) for i in service_product_cat]

        service_states = data_values.get('service_states', [])
        service_states_ids = [int(i) for i in service_states]

        service_dist = data_values.get('service_dist', [])
        service_dist_ids = [int(i) for i in service_dist]

        service_type = data_values.get('service_type', [])
        service_type_ids = [int(i) for i in service_type]

        service_delivery = data_values.get('service_delivery', [])
        service_delivery_ids = [int(i) for i in service_delivery]

        other_brand = data_values.get('other_brand', [])
        other_brand_ids = [int(i) for i in other_brand]




        asp_ls=request.env['asp.partner'].sudo().search([])
        # note =kw.get('service_product_cat')
        note = "Service Product Categories:" + str(kw.get('service_product_cat')) + "\n Seiviceable States:" + str(kw.get('service_states')) + "\n Serviceable Districts:" + str(kw.get('service_dist')) + "\n Service Categories:" + str(kw.get('service_categories')) + "\n Service Type:" + str(kw.get('service_type_ids')) + "\n Service Locations:" + str(kw.get('location_ids')) + "\n Crms Used:" + str(kw.get('using_crm_ids')) + "\n Other Brands:" + str(kw.get('other_brand_ids')) + "\n Seiviceable Delivery:" + str(kw.get('service_delivery'))
                 

        asp_val = {
            'year_established': kw.get('year_established'),
            'total_people':kw.get('total_people'),
            'name': kw.get('name'),
            'company_mail': kw.get('company_mail'),
            'avg_turn_over': kw.get('avg_turn_over'),
            'promoter_name': kw.get('promoter_name'),
            'promoter_email': kw.get('promoter_email'),
            'promoter_mobile': kw.get('promoter_mobile'),
            'service_delivery_head_name': kw.get('service_delivery_head_name'),
            'service_delivery_head_email': kw.get('service_delivery_head_email'),
            'service_delivery_head_mobile': kw.get('service_delivery_head_mobile'),
            'senior_technical_person_name': kw.get('senior_technical_person_name'),
            'senior_technical_person_email': kw.get('senior_technical_person_email'),
            'senior_technical_person_mobile': kw.get('senior_technical_person_mobile'),
            'rma_center': kw.get('rma_center'),
            'is_gst_registered': kw.get('is_gst_registered'),
            'country': kw.get('country', False) if kw.get('country') else None,
            'state': kw.get('state', False) if kw.get('state') else None,
            # 'asp_contact_name':kw.get('asp_contact_name'),
            'street': kw.get('street'),
            'street2': kw.get('street2'),
            'zip': kw.get('zip'),
            'city': kw.get('city'),
            'gst_number': kw.get('gst_number'),
            'notes': note,
            'list_of_certificates': kw.get('list_of_certificates'),
            'list_of_awards': kw.get('list_of_awards'),
            'service_delivery_years': kw.get('service_delivery_years'),
            'service_delivery_achivements': kw.get('service_delivery_achivements'),
#             'company_profile': kw.get('company_profile'),
#             'customer_testmonial': kw.get('customer_testmonial'),
#             'sla_document': kw.get('sla_document'),
#             'escalation_document': kw.get('escalation_document'),
            'customer_feedback': kw.get('customer_feedback'),
            'shelf_place': kw.get('shelf_place'),
            'ready_to_use_rdp_crm': kw.get('ready_to_use_rdp_crm'),
            'ready_to_for_weekly_sla_reviews': kw.get('ready_to_for_weekly_sla_reviews'),
            'onsite_support_executives': kw.get('onsite_support_executives'),
            'insite_support_executives': kw.get('insite_support_executives'),
            'number_of_calls_expecting_from_rdp_per_month': kw.get('number_of_calls_expecting_from_rdp_per_month'),
            'number_of_calls_you_are_attending_per_day': kw.get('number_of_calls_you_are_attending_per_day'),
            'onsite_calls_every_day': kw.get('onsite_calls_every_day'),
            'training_certificates': kw.get('training_certificates'),
            'training_on_softskills': kw.get('training_on_softskills'),
            'training_on_hardskills': kw.get('training_on_hardskills'),
            'company_name': kw.get('name'),
            'service_categories': [(6, 0, service_categorie_ids)],
            'service_product_cat': [(6, 0, service_product_cat_ids)],
            'service_states': [(6, 0, service_states_ids)],
            'service_dist': [(6, 0, service_dist_ids)],
            'service_type_ids': [(6, 0, service_type_ids)],
            'service_delivery_by': [(6, 0, service_delivery_ids)],
            'asp_other_brands': [(6, 0, other_brand_ids)],
            # 'service_type':kw.get('service_type'),
            # 'service_cat':kw.get('service_cat'),
            # 'serviceable_state_cat':kw.get('serviceable_state_cat'),
            # 'service_product_category':kw.get('service_product_category'),
            # 'used_crms':kw.get('used_crms'),
            # 'branch_location':kw.get('branch_location'),

            # 'service_product_cat': kw.getlist('service_product_cat', False) if kw.getlist('service_product_cat') else None,
            

          
        }
        print("asp_val -------", asp_val)
        asp_re = request.env['res.partner'].sudo().create({
            'name': kw.get('name'),
            'street': kw.get('street'),
            'street2': kw.get('street2'),
            'zip': kw.get('zip'),
            'city': kw.get('city'),
            'state_id': kw.get('state', False) if kw.get('state') else None,
            'country_id': int(kw.get('country', False)),
            'email': kw.get('company_mail'),
            'vat': kw.get('gst_number'),
        })
        asp_val.update({"vendor": asp_re.id})
        res = asp_ls.create(asp_val)

        return request.render("rdp_asp_partner_extend.asp_thanks", {'asp_val': res})
     
      
