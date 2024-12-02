from odoo import http, _
from odoo.http import request
import base64
# Example of logging the data in your controller
import logging

_logger = logging.getLogger(__name__)


class ContactUsController(http.Controller):

    @http.route('/contact_forms', type="http", auth="public", website=True)
    def contact_forms(self):
        return http.request.render('rdp_contactus_form.website_contact_us_template')

    @http.route('/website_contact_form', type="http", auth="public", website=True)
    def website_contact_form(self, **kwargs):
        print("!!!!!  kwargs['partner_date'],", kwargs['partner_date'], )
        print("!!!!!  typeee'],", type(kwargs['partner_date']))
        data_dct = {}
        # if 'partner_work' in kwargs:
        #     data_dct.update({'name': kwargs['partner_work'], })
        if 'partner_name' in kwargs:
            data_dct.update({'partner_name': kwargs['partner_name'], })
        if 'partner_email' in kwargs:
            data_dct.update({'partner_email': kwargs['partner_email'], })
        if 'contact_mobile' in kwargs:
            data_dct.update({'customer_mobile': kwargs['contact_mobile'], })
        # if 'contact_device_no' in kwargs:
        #     data_dct.update({'contact_device_no': kwargs['contact_device_no'], })
        if 'contact_device_serial' in kwargs:
            data_dct.update({'serial_no': kwargs['contact_device_serial'], })
        if 'description' in kwargs:
            data_dct.update({'description': kwargs['description'], })
        if 'contact_order' in kwargs:
            data_dct.update({'order_id': kwargs['contact_order'], })
        if 'partner_product' in kwargs:
            data_dct.update({'product_id': int(kwargs['partner_product']), })
        if 'complain_type' in kwargs:
            data_dct.update({'helpdesk_ticket_type': int(kwargs['complain_type']), })
        if 'sub_complain_type' in kwargs:
            data_dct.update({'sub_complaint_type': kwargs['sub_complain_type'], })
        if 'product_purchase' in kwargs:
            data_dct.update({'product_purchase': kwargs['product_purchase'], })
        if 'partner_color' in kwargs:
            data_dct.update({'color': kwargs['partner_color'], })
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

        ticket = request.env['helpdesk.ticket'].sudo().create(data_dct)
        ticket.update({
            'name': ticket.ticket_ref
        })
        return request.render('rdp_contactus_form.contactus_thanks', {'name': ticket.ticket_ref})

    @http.route('/contactus', type="http", auth="public", website=True)
    def contact_us_forms(self):
        return http.request.render('rdp_contactus_form.website_contact_us_template')
