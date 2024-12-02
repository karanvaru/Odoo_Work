from odoo import http, _
from odoo.http import request, Controller
import base64
import logging

_logger = logging.getLogger(__name__)


class VendorRegistration(http.Controller):

    @http.route([
        '/customer-verification/<string:id_encoded>'],
        type='http',
        auth="public",
        website=True
    )
    def customer_verification(self, id_encoded, **post):
        id_decode_bytes = id_encoded.encode("ascii")
        id_decode_bytes_str = base64.b64decode(id_decode_bytes)
        id_decoded = id_decode_bytes_str.decode("ascii")
        partner_id = request.env['res.partner'].sudo().browse(int(id_decoded))
        country = request.env['res.country'].sudo().search([])
        return request.render(
            'de_charity_portal.website_verification_customer_detail', {
                'partner': partner_id,
                'country': country
            }
        )

    @http.route(
        '/customer_verification_data',
        methods=['GET', 'POST', 'FILES'],
        type='http',
        auth='public',
        website=True,
        csrf=False
    )
    def customer_verification_data(self, **kw):
        if 'partner_id' in kw:
            partner_id = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
            data_dct = {}
            field_mapping = {
                'partner_name': 'name',
                'partner_dob': 'dob',
                'partner_address': 'city',
                'partner_occupation': 'occupation',
                'partner_telephone': 'phone',
                'partner_fax': 'fax_number',
                'partner_email': 'email',
                'sex_type': 'sex',
                'partner_nationality': 'country_id',
                'partner_age': 'age',
                'partner_height': 'height',
                'm_status': 'marital_status',
                'primary_value': 'primary_edu',
                'high_school_value': 'high_school_edu',
                'collage_value': 'college_edu',
                'university_value': 'university_edu',
                'other_training': 'other_training',
                'referred_by_name': 'referred_by',
                'referred_of_name': 'referred_by_of',
                'physical_health': 'physical_health_rate',
                'partner_handicaps': 'part_illnesses',
                'partner_what': 'what',
                'partner_challenges': 'major_change_life',
                'denominational': 'demonational_preference',
                'background': 'religious_background',
                'name_spouse': 'spouse_name',
                'marr_address': 'spouse_address',
                'marr_phone': 'spouse_phone',
                'marr_occupation': 'spouse_occupation',
                'marr_mobile': 'spouse_mobile',
                'marr_date': 'spouse_dom',
                'marr_broken_dv': 'broken_by_divorce',
                'marr_death': 'death',
                'first_q_details': 'first_q_details',
                'second_q_details': 'second_q_details',
                'third_q_details': 'third_q_details',
                'fourth_q_details': 'fourth_q_details',
                'fifth_q_details': 'fifth_q_details',
            }
            boolean_fields = {
                'medication': 'prepare_medicine',
                'upset': 'emotional_upset',
                'phychotheraphy': 'is_counselling',
                'baptized': 'is_baptized',
                'confirmed': 'is_confirmed',
                'received': 'is_received',
            }

            for key, value in field_mapping.items():
                if key in kw:
                    data_dct.update({value: kw[key] if key != 'partner_nationality' else int(kw[key])})

            for key, value in boolean_fields.items():
                if key in kw:
                    data_dct.update({value: kw[key] == 'True'})

            # if 'partner_name' in kw:
            #     data_dct.update({'name': kw['partner_name']})
            # if 'partner_dob' in kw:
            #     data_dct.update({'dob': kw['partner_dob']})
            # if 'partner_address' in kw:
            #     data_dct.update({'city': kw['partner_address']})
            # if 'partner_occupation' in kw:
            #     data_dct.update({'occupation': kw['partner_occupation']})
            # if 'partner_telephone' in kw:
            #     data_dct.update({'phone': kw['partner_telephone']})
            # if 'partner_fax' in kw:
            #     data_dct.update({'fax_number': kw['partner_fax']})
            # if 'partner_email' in kw:
            #     data_dct.update({'email': kw['partner_email']})
            # if 'sex_type' in kw:
            #     data_dct.update({'sex': kw['sex_type']})
            # if 'partner_nationality' in kw:
            #     data_dct.update({'country_id': int(kw['partner_nationality'])})
            # if 'partner_age' in kw:
            #     data_dct.update({'age': kw['partner_age']})
            # if 'partner_height' in kw:
            #     data_dct.update({'height': kw['partner_height']})
            # if 'm_status' in kw:
            #     data_dct.update({'marital_status': kw['m_status']})
            # if 'primary_value' in kw:
            #     data_dct.update({'primary_edu': kw['primary_value']})
            # if 'high_school_value' in kw:
            #     data_dct.update({'high_school_edu': kw['high_school_value']})
            # if 'collage_value' in kw:
            #     data_dct.update({'college_edu': kw['collage_value']})
            # if 'university_value' in kw:
            #     data_dct.update({'university_edu': kw['university_value']})
            # if 'other_training' in kw:
            #     data_dct.update({'other_training': kw['other_training']})
            # if 'referred_by_name' in kw:
            #     data_dct.update({'referred_by': kw['referred_by_name']})
            # if 'referred_of_name' in kw:
            #     data_dct.update({'referred_by_of': kw['referred_of_name']})
            # if 'physical_health' in kw:
            #     data_dct.update({'physical_health_rate': kw['physical_health']})
            # if 'partner_handicaps' in kw:
            #     data_dct.update({'part_illnesses': kw['partner_handicaps']})
            # if 'medication' in kw:
            #     if kw['medication'] == 'True':
            #         data_dct.update({'prepare_medicine': True})
            #     else:
            #         data_dct.update({'prepare_medicine': False})
            # if 'partner_what' in kw:
            #     data_dct.update({'what': kw['partner_what']})
            # if 'upset' in kw:
            #     if kw['upset'] == 'True':
            #         data_dct.update({'emotional_upset': True})
            #     else:
            #         data_dct.update({'emotional_upset': False})
            # if 'phychotheraphy' in kw:
            #     if kw['phychotheraphy'] == 'True':
            #         data_dct.update({'is_counselling': True})
            #     else:
            #         data_dct.update({'is_counselling': False})
            # if 'partner_challenges' in kw:
            #     data_dct.update({'major_change_life': kw['partner_challenges']})
            # if 'denominational' in kw:
            #     data_dct.update({'demonational_preference': kw['denominational']})
            # if 'baptized' in kw:
            #     if kw['baptized'] == 'True':
            #         data_dct.update({'is_baptized': True})
            #     else:
            #         data_dct.update({'is_baptized': False})
            # if 'confirmed' in kw:
            #     if kw['confirmed'] == 'True':
            #         data_dct.update({'is_confirmed': True})
            #     else:
            #         data_dct.update({'is_confirmed': False})
            # if 'received' in kw:
            #     if kw['received'] == 'True':
            #         data_dct.update({'is_received': True})
            #     else:
            #         data_dct.update({'is_received': False})
            # if 'background' in kw:
            #     data_dct.update({'religious_background': kw['background']})
            # if 'name_spouse' in kw:
            #     data_dct.update({'spouse_name': kw['name_spouse']})
            # if 'marr_address' in kw:
            #     data_dct.update({'spouse_address': kw['marr_address']})
            # if 'marr_phone' in kw:
            #     data_dct.update({'spouse_phone': kw['marr_phone']})
            # if 'marr_occupation' in kw:
            #     data_dct.update({'spouse_occupation': kw['marr_occupation']})
            # if 'marr_mobile' in kw:
            #     data_dct.update({'spouse_mobile': kw['marr_mobile']})
            # if 'marr_date' in kw:
            #     data_dct.update({'spouse_dom': kw['marr_date']})
            # if 'marr_broken_dv' in kw:
            #     data_dct.update({'broken_by_divorce': kw['marr_broken_dv']})
            # if 'marr_death' in kw:
            #     data_dct.update({'death': kw['marr_death']})
            # if 'first_q_details' in kw:
            #     data_dct.update({'first_q_details': kw['first_q_details']})
            # if 'second_q_details' in kw:
            #     data_dct.update({'second_q_details': kw['second_q_details']})
            # if 'third_q_details' in kw:
            #     data_dct.update({'third_q_details': kw['third_q_details']})
            # if 'fourth_q_details' in kw:
            #     data_dct.update({'fourth_q_details': kw['fourth_q_details']})
            # if 'fifth_q_details' in kw:
            #     data_dct.update({'fifth_q_details': kw['fifth_q_details']})

            child_lst = []
            child_dct = {}
            for key, value in kw.items():
                number = key.split('_')[-1]
                if key.startswith('child_'):
                    number = key.split('_')[-1]
                    if number not in child_dct:
                        child_dct[number] = {}
                    if value == 'True':
                        value = True
                    if value == 'False':
                        value = False
                    child_dct[number][key.rsplit('_', 1)[0]] = value
            for rec in child_dct:
                if child_dct[rec]['child_id'] == '':
                    if child_dct[rec]['child_name'] != '':
                        child_dct[rec].pop("child_id")
                        child_lst.append((0, 0, child_dct[rec]))
            data_dct.update({'children_details_ids': child_lst})

            partner_id.update(data_dct)

            captain_data = ['Likes control', 'Confident', 'Firm', 'Likes challenge',
                            'Problem solver', 'Bold', 'Goal driven', 'Strong willed',
                            'Self-reliant', 'Persistent', 'Takes charge', 'Determined',
                            'Enterprising', 'Competitive', 'Productive', 'Purposeful',
                            'Adventurous', 'Independent', 'Action oriented']

            social_director_data = ['Enthusiastic', 'Visionary', 'Energetic', 'Promoter',
                                    'Mixes easily', 'Fun-loving', 'Spontaneous', 'Likes new ideas',
                                    'Optimistic', 'Takes risks', 'Motivator', 'Very verbal',
                                    'Friendly', 'Popular', 'Enjoys variety', 'Group oriented',
                                    'Initiator', 'Inspirational', 'Likes change']

            steward_data = ['Sensitive', 'Calm', 'Non-demanding', 'Enjoys routine',
                            'Relational', 'Adaptable', 'Thoughtful', 'Patient',
                            'Good listener', 'Loyal', 'Even-keeled', 'Gives in',
                            'Indecisive', 'Dislikes change', 'Dry humor', 'Sympathetic',
                            'Nurturing', 'Tolerant', 'Peace maker']

            navigator_data = ['Consistent', 'Reserved', 'Practical', 'Factual',
                              'Perfectionist', 'Detailed', 'Inquisitive', 'Persistent',
                              'Sensitive', 'Accurate', 'Controlled', 'Predictable',
                              'Orderly', 'Conscientious', 'Discerning', 'Analytical',
                              'Precise', 'Scheduled', 'Deliberate']

            return request.render(
                'de_charity_portal.website_verification_customer_personality_profile', {
                    'partner': partner_id,
                    'captain': captain_data,
                    'social_director': social_director_data,
                    'steward': steward_data,
                    'navigator': navigator_data
                }
            )

    @http.route(
        '/customer_personality_profile_data',
        methods=['GET', 'POST', 'FILES'],
        type='http',
        auth='public',
        website=True,
        csrf=False
    )
    def customer_personality_profile_data(self, **kw):
        if 'partner_id' in kw:
            company = request.env.company
            partner_id = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
            partner_id.the_captain_ids = [(5, 0, 0)]
            partner_id.the_social_director_ids = [(5, 0, 0)]
            partner_id.the_steward_ids = [(5, 0, 0)]
            partner_id.the_navigator_ids = [(5, 0, 0)]
            captain_lst = []
            social_lst = []
            steward_lst = []
            navigator_lst = []
            for profile_data in kw:
                if profile_data.startswith("captain_"):
                    cleaned_data = profile_data.replace("captain_", "")
                    captain_dct = {
                        'name': cleaned_data,
                        'value': 0 if kw[profile_data] == 'none' else int(kw[profile_data]),
                    }
                    captain_lst.append((0, 0, captain_dct))

                if profile_data.startswith("social_"):
                    cleaned_data = profile_data.replace("social_", "")
                    social_dct = {
                        'name': cleaned_data,
                        'value': 0 if kw[profile_data] == 'none' else int(kw[profile_data]),
                    }
                    social_lst.append((0, 0, social_dct))

                if profile_data.startswith("steward_"):
                    cleaned_data = profile_data.replace("steward_", "")
                    steward_dct = {
                        'name': cleaned_data,
                        'value': 0 if kw[profile_data] == 'none' else int(kw[profile_data]),
                    }
                    steward_lst.append((0, 0, steward_dct))

                if profile_data.startswith("navigator_"):
                    cleaned_data = profile_data.replace("navigator_", "")
                    navigator_dct = {
                        'name': cleaned_data,
                        'value': 0 if kw[profile_data] == 'none' else int(kw[profile_data]),
                    }
                    navigator_lst.append((0, 0, navigator_dct))
            partner_id.the_captain_ids = captain_lst
            partner_id.the_social_director_ids = social_lst
            partner_id.the_steward_ids = steward_lst
            partner_id.the_navigator_ids = navigator_lst
            # partner_id.is_content = True

            return request.render(
                'de_charity_portal.website_verification_customer_confidently_details', {
                    'partner': partner_id,
                    'company': company
                }
            )

    # @http.route(
    #     '/customer_confidential_policy_data',
    #     methods=['GET', 'POST', 'FILES'],
    #     type='http',
    #     auth='public',
    #     website=True,
    #     csrf=False
    # )
    # def customer_confidential_policy_data(self, **kw):
    #     partner_id = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
    #
    #     return request.render(
    #         'de_charity_portal.website_verification_thanks_page', {
    #             'partner': partner_id,
    #         }
    #     )

    @http.route('/save_signature', type='json', auth="public", methods=['POST'], website=True)
    def save_signature_partner(self, **kw):
        if 'partner' in kw:
            partner_id = request.env['res.partner'].sudo().browse(int(kw['partner']))
            signature = kw['signature']

            partner_id.update({
                'partner_signature': signature.split(',')[1]
            })

    @http.route('/delete/row', type='json', auth="public", methods=['POST'], website=True)
    def add_job_row(self, **kwargs):
        if kwargs['child_id'] != '':
            children_record = request.env['partner.children.details'].sudo().browse(int(kwargs['child_id']))
            if children_record:
                children_record.unlink()

    @http.route('/new_page', type='json', auth="public", methods=['POST'], website=True)
    def confirm_partner_policy_data(self, **kw):
        partner_id = request.env['res.partner'].sudo().browse(int(kw['partner']))
        partner_id.update({
            'is_content': True
        })
        data = {
            'is_content': partner_id.is_content,
        }
        return {'data': data}

    @http.route('/thanks_page', type='json', auth="public", methods=['POST'], website=True)
    def thanks_page_data(self, **kw):
        partner_id = request.env['res.partner'].sudo().browse(int(kw['partner']))
        data = {
            'is_content': partner_id.is_content,
        }
        return {'data': data}
