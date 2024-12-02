from odoo import http, _
from odoo.http import request
import base64
import logging
import json
import uuid


_logger = logging.getLogger(__name__)


class ContactUsController(http.Controller):

    @http.route('/fetch_data', type='json', auth="public", website=True)
    def fetch_data(self, **kwargs):
        result = {'success': False}

        try:
            raw_data = request.httprequest.get_data()  
            data = json.loads(raw_data)  
            partner_email = data.get('partner_email')  
            serial_no = data.get('serial_no')  
        except Exception as e:
            result['message'] = "Invalid request data."
            return result

        if partner_email:
            user = request.env['res.partner'].sudo().search([('email', '=', partner_email)], limit=1)
            if user:
                result = {
                    'success': True,
                    'partner_name': user.name,
                    'contact_mobile': user.phone,
                    'partner_email': user.email
                }
            else:
                result['message'] = "No contact found with the specified email."

        elif serial_no:
            lot = request.env['stock.lot'].sudo().search([('name', '=', serial_no)], limit=1)
            if lot and lot.product_id:
                product = lot.product_id
                variant_attributes = ",".join(
                    f"{attr.attribute_id.name}-{attr.name}"
                    for attr in product.product_template_attribute_value_ids
                )
                produdct_display_name = f"{product.name}({variant_attributes})" if variant_attributes else product.name
                result = {
                    'success': True,
                    'product_id': lot.product_id.id,
                    'product_name': produdct_display_name,
                    'serial_no': serial_no
                }
            else:
                result['message'] = "No product found with the specified serial number."

        return result

        
    @http.route('/contact_forms', type="http", auth="public", website=True)
    def contact_forms(self):
        return http.request.render('rdp_it_contactus_form_ev17_custom.website_contact_us_template')
    
    
    @http.route('/check_username', type='http', auth="public", website=True)
    def check_username(self, **kwargs):
        username = kwargs.get('username')
        
        user = request.env['res.users'].sudo().search([('name', '=', username)], limit=1)

        if user:
            request.session['asp_username'] = username
            return http.request.render('rdp_it_contactus_form_ev17_custom.website_contact_us_template')
        else:
            error_message = "The Username you entered does not exist. Give correct name."
            return request.render('rdp_it_contactus_form_ev17_custom.ASP_Username_Form', {'error_message': error_message})

    @http.route('/website_contact_form', type="http", auth="public", website=True)
    def website_contact_form(self, **kwargs):
        
        data_dct = {}

        asp_username = request.session.get('asp_username')
        if asp_username:
            asp_user = request.env['res.users'].sudo().search([('name', '=', asp_username)], limit=1)
            if asp_user:
                data_dct.update({'asp_engineer_id': asp_user.id})
            request.session.pop('asp_username', None)

        if 'partner_name' in kwargs:
            data_dct.update({'partner_name': kwargs['partner_name'], })
        if 'partner_email' in kwargs:
            data_dct.update({
                'email_cc': kwargs['partner_email'],
                'partner_email': kwargs['partner_email']
            })
        if 'contact_mobile' in kwargs:
            data_dct.update({
                'customer_mobile': kwargs['contact_mobile'],
                'partner_phone': kwargs['contact_mobile']
            })
        if 'contact_device_serial' in kwargs:
            data_dct.update({'serial_no': kwargs['contact_device_serial'], })
        if 'product_name' in kwargs:
            data_dct.update({'product_name': kwargs['product_name'], })
        if 'description' in kwargs:
            data_dct.update({'description': kwargs['description'], })
        if 'contact_order' in kwargs:
            data_dct.update({'order_id': kwargs['contact_order'], })
        if 'complain_type' in kwargs:
            data_dct.update({'helpdesk_ticket_type': int(kwargs['complain_type']), })
        if 'purchase_channel' in kwargs:
            data_dct.update({'purchase_channel_ids': kwargs['purchase_channel'], })
        if 'partner_date' in kwargs:
            data_dct.update({'purchase_date': kwargs['partner_date'], })
        if 'partner_street' in kwargs:
            data_dct.update({'street': kwargs['partner_street'], })
        if 'partner_city' in kwargs:
            data_dct.update({'city': int(kwargs['partner_city']), })
        if 'partner_state' in kwargs:
            data_dct.update({'state': int(kwargs['partner_state']), })
        if 'partner_country' in kwargs:
            data_dct.update({'country': int(kwargs['partner_country']), })
        if 'partner_pincode' in kwargs:
            data_dct.update({'pincode': kwargs['partner_pincode'], })
        if 'partner_landmark' in kwargs:
            data_dct.update({'landmark': kwargs['partner_landmark'], })
        if 'partner_invoice_number' in kwargs:
            data_dct.update({'invoice_number': kwargs['partner_invoice_number'], })
        if 'partner_invoice' in kwargs:
            data_dct.update({
                'upload_inv': base64.encodebytes(kwargs['partner_invoice'].read()),
                'document_name': kwargs['partner_invoice'].filename
            })

        try:
            ticket = request.env['helpdesk.ticket'].sudo().create(data_dct)
            ticket.update({'name': ticket.ticket_ref})
            return request.render('rdp_it_contactus_form_ev17_custom.contactus_thanks', {'name': ticket.ticket_ref})
        except Exception as e:
            error_message = str(e)
            return request.render('rdp_it_contactus_form_ev17_custom.contactus_error_form', {'error_message': error_message})

    @http.route('/contactus', type="http", auth="public", website=True)
    def contact_us_forms(self):
        return http.request.render('rdp_it_contactus_form_ev17_custom.website_contact_us_template')
    

    @http.route('/customer_type', type="http", auth="public", website=True)
    def customer_type(self):
        return http.request.render('rdp_it_contactus_form_ev17_custom.website_contact_us_template')
    
    @http.route('/asp_type', type="http", auth="public", website=True)
    def asp_type(self):
        return http.request.render('rdp_it_contactus_form_ev17_custom.ASP_Username_Form')