from odoo import http, _
from odoo.http import request, Controller
import base64
import re
# from ifscApi.getDetails import FetchData
# name = 'ifscApi'

import requests
import json
import xmltodict
import logging

_logger = logging.getLogger(__name__)


class VendorRegistration(http.Controller):

    def is_valid_gstin(self, gstin):
        # Regular expression to match the GSTIN pattern
        pattern = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')

        if pattern.match(gstin):
            return True
        return False

    def is_valid_pan(self, pan):
        pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')
        if pattern.match(pan):
            return True
        return False

    @http.route([
        '/vendor-verification/<string:id_encoded>'],
        type='http',
        auth="public",
        website=True
    )
    def vendor_verification(self, id_encoded, **post):
        id_decode_bytes = id_encoded.encode("ascii")
        id_decode_bytes_str = base64.b64decode(id_decode_bytes)
        id_decoded = id_decode_bytes_str.decode("ascii")
        partner_id = request.env['res.partner'].sudo().browse(int(id_decoded))
        if partner_id.approval_state == 'form_submitted':
            return request.render(
                'qno_vendor_registration.website_verification_already_submitted_page',
                {'partner': partner_id}
            )
        else:
            return request.render(
                'qno_vendor_registration.website_verification_customer_detail',
                {'partner': partner_id}
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
            organization = request.env['organization.type'].sudo().search([])

            partner_id.update({
                'name': kw['name'],
                'email': kw['email'],
                'mobile': kw['mobile'],
                'contact_person_name': kw['contact_person_name'] or '',
                'type': 'invoice',
            })
            if kw['other_contact_name'] != '' or kw['other_contact_name'] != '':
                contact_details_list = []
                delivery_contact_details = {
                    'name': kw['other_contact_name'],
                    'mobile': kw['other_contact_mobile'],
                    'type': 'invoice',
                    'parent_id': int(kw['partner_id'])
                }
                invoice_contact_details = {
                    'name': kw['other_contact_name'],
                    'mobile': kw['other_contact_mobile'],
                    'type': 'delivery',
                    'parent_id': int(kw['partner_id'])
                }

                invoice_child_id = request.env['res.partner'].sudo().create(invoice_contact_details)
                delivery_child_id = request.env['res.partner'].sudo().create(delivery_contact_details)

                contact_details_list.append((4, invoice_child_id.id))
                contact_details_list.append((4, delivery_child_id.id))

                partner_id.sudo().write({'child_ids': contact_details_list})
            if partner_id.approval_state == 'form_submitted':
                return request.render(
                    'qno_vendor_registration.website_verification_already_submitted_page',
                    {
                        'partner': partner_id
                    }
                )
            else:
                return request.render(
                    'qno_vendor_registration.website_verification_pre_fill_company_detail',
                    {
                        'partner': partner_id,
                        'organization': organization
                    }
                )

    @http.route(
        '/customer_verification_pref_fill_company',
        methods=['GET', 'POST', 'FILES'],
        type='http',
        auth='public',
        website=True
    )
    def customer_verification_pre_fill_company(self, **kw):
        if 'partner_id' in kw:

            valid_pan = self.is_valid_pan(kw['Pan'])
            if not valid_pan:
                return False

            business_category = request.env['business.category'].sudo().search([])
            partner_id = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
            data_record = kw['company_pan']
            ir_values = {
                'name': "Company Pan",
                'type': 'binary',
                'datas': base64.encodebytes(data_record.read()),
                'store_fname': data_record,
            }
            data_id = request.env['ir.attachment'].sudo().create(ir_values)
            if 'organization' in kw:
                if kw['organization'] == 'none':
                    partner_id.update({
                        'organization_type_id': '',
                    })
                else:
                    partner_id.update({
                        'organization_type_id': int(kw['organization']),
                    })
            partner_id.update({
                'prefill_check_upload': ir_values['datas'],
                'prefill_check_upload_name': data_record.filename,
                'company_pan': kw['Pan'],
            })
            if partner_id.approval_state == 'form_submitted':
                return request.render(
                    'qno_vendor_registration.website_verification_already_submitted_page',
                    {
                        'partner': partner_id
                    }
                )
            else:
                return request.render(
                    'qno_vendor_registration.website_verification_company_detail',
                    {
                        'partner': partner_id,
                        'category': business_category
                    }
                )

    @http.route(
        '/customer_verification_company',
        methods=['POST'],
        type='http',
        auth='public',
        website=True
    )
    def customer_verification_company(self, **kw):
        if 'partner_id' in kw:
            valid_gstin = self.is_valid_gstin(kw['gstin'])
            if not valid_gstin:
                return False

            partner_id = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
            data_record = kw['business_tan_upload']
            ir_values = {
                'name': "Company Pan",
                'type': 'binary',
                'datas': base64.encodebytes(data_record.read()),
                'store_fname': data_record,
            }
            data_id = request.env['ir.attachment'].sudo().create(ir_values)

            if 'authorised_signatory_pan_upload' in kw:
                authorised_data_record = kw['authorised_signatory_pan_upload']
                authorised_ir_values = {
                    'name': "Authorised Signatory Pan",
                    'type': 'binary',
                    'datas': base64.encodebytes(authorised_data_record.read()),
                    'store_fname': authorised_data_record,
                }
                partner_id.update({
                    'authorised_signatory_pan_upload': authorised_ir_values['datas'],
                    'authorised_signatory_pan_upload_name': authorised_data_record.filename,
                })

            if 'gst_certificate_upload' in kw:
                gst_data_record = kw['gst_certificate_upload']
                gst_certificate_ir_values = {
                    'name': "GST Certificate Pan",
                    'type': 'binary',
                    'datas': base64.encodebytes(gst_data_record.read()),
                    'store_fname': gst_data_record,
                }
                partner_id.update({
                    'gst_certificate_upload': gst_certificate_ir_values['datas'],
                    'gst_certificate_upload_name': gst_data_record.filename,
                })

            partner_id.update({
                'vat': kw['gstin'],
                'authorised_signatory_pan': kw['authorised_pan'],
                #                 'business_category_id': int(kw['category']),
                # 'l10n_in_gst_treatment': kw['l10n_in_gst_treatment'],
                'business_tan': kw['business_tan'],
                'company_details_upload': ir_values['datas'],
                'company_details_upload_name': data_record.filename,
                'msme_no': kw['msme_no'],
            })
            if 'l10n_in_gst_treatment' in kw:
                if kw['l10n_in_gst_treatment'] == 'none':
                    partner_id.update({
                        'l10n_in_gst_treatment': '',
                    })
                else:
                    partner_id.update({
                        'l10n_in_gst_treatment': kw['l10n_in_gst_treatment'],
                    })

            if 'cin_llpin' in kw:
                partner_id.update({
                    'company_registry': kw['cin_llpin'],
                })
            if 'business_tan' in kw:
                partner_id.update({
                    'business_tan': kw['business_tan'],
                })
            if 'msme_type' in kw:
                if kw['msme_type'] == 'none':
                    partner_id.update({
                        'msme_type': '',
                    })
                else:
                    partner_id.update({
                        'msme_type': kw['msme_type'],
                    })

            GSTIN = kw['gstin']
            GSTRESPONSE = {}
            # sap_conf_id = request.env['sap.configuration'].sudo().search([], limit=1)
            sap_conf_id = request.env.company.api_url
            # URL = "http://136.243.59.116:60009/Service.asmx/getGSTINDetails"
            GSTRESPONSE_URL = requests.get(sap_conf_id + "/Service.asmx/getGSTINDetails" + "?GSTIN=" + GSTIN)
            if GSTRESPONSE_URL.status_code == 200:
                resp = GSTRESPONSE_URL.text
                #                 resp =     """
                #                     <?xml version="1.0" encoding="utf-8"?>
                #                     <string xmlns="http://tempuri.org/">{"error":false,"data":{"stjCd":"GJ007","lgnm":"PRASHANT PATEL","stj":"Ghatak 7 (Ahmedabad)","dty":"Regular","adadr":[],"cxdt":"","gstin":"24BMXPP9423L1Z5","nba":["Office / Sale Office"],"lstupdt":"15/12/2022","rgdt":"16/07/2021","ctb":"Proprietorship","pradr":{"addr":{"bnm":"SANDALWOOD ELEGANCE","loc":"SOLA, AHMEDABAD","st":"NR. MADHUVAN BUNGLOWS, B/H. KARGIL PETROL PUMP","bno":"BLOCK B/402","dst":"Ahmedabad","lt":"","locality":"","pncd":"382470","landMark":"","stcd":"Gujarat","geocodelvl":"NA","flno":"","lg":""},"ntr":"Office / Sale Office"},"tradeNam":"KIRAN INFOSOFT","sts":"Active","ctjCd":"WT0705","ctj":"RANGE V","einvoiceStatus":"No"}}</string>
                #                     """
                xpars = xmltodict.parse(resp.strip())
                for xp in xpars:
                    for x in xpars[xp]:
                        if "data" in xpars[xp][x]:
                            json_object = json.loads(xpars[xp][x])
                            if "data" in json_object:
                                GSTRESPONSE = json_object['data']

            GSTRESPONSE_STATIC = {
                "stjCd": "GJ016",
                "dty": "Regular",
                "lgnm": "QNOMIX TECHNOLOGIES",
                "stj": "Ghatak 16 (Ahmedabad)",
                "adadr": [],
                "cxdt": "",
                "gstin": "24AAAFQ7405R1ZW",
                "nba": [
                    "Supplier of Services"
                ],
                "lstupdt": "02/09/2018",
                "ctb": "Partnership",
                "rgdt": "31/08/2018",
                "pradr": {
                    "addr": {
                        "bnm": "LATI BAZAR ZONE- II",
                        "st": "OPP. DEEPAK HOTEL, GITA MANDIR, KHEMBHAI ROAD",
                        "loc": "AHMEDABAD",
                        "bno": "1062/9/32/1, 26/27/F/7, TPS 1",
                        "dst": "Ahmedabad",
                        "lt": "",
                        "locality": "",
                        "pncd": "380022",
                        "landMark": "",
                        "stcd": "Gujarat",
                        "geocodelvl": "",
                        "flno": "FIRST",
                        "lg": ""
                    },
                    "ntr": "Supplier of Services"
                },
                "ctjCd": "WS0104",
                "tradeNam": "QNOMIX TECHNOLOGIES",
                "sts": "Active",
                "ctj": "RANGE IV",
                "einvoiceStatus": "No"
            }
            data = GSTRESPONSE['pradr']['addr']

            address1 = '{},{}'.format(data['bno'], data['bnm'])
            address2 = data['st']
            city = data['dst']
            pincode = data['pncd']
            state = data['stcd']
            address_dct = {
                'address1': address1,
                'address2': address2,
                'city': city,
                'pincode': pincode,
                'state': state,
            }
            if partner_id.approval_state == 'form_submitted':
                return request.render(
                    'qno_vendor_registration.website_verification_already_submitted_page',
                    {
                        'partner': partner_id
                    }
                )
            else:
                return request.render(
                    'qno_vendor_registration.website_verification_partner_address',
                    {
                        'partner': partner_id,
                        'address_dct': address_dct,
                    }
                )

    @http.route(
        '/customer_address_details',
        methods=['POST'],
        type='http',
        auth='public',
        website=True
    )
    def customer_address_details(self, **kw):
        if 'partner_id' in kw:
            partner_address_dct = {}
            partner_id = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
            if 'address1' in kw:
                partner_address_dct['street'] = kw['address1']
            if 'address2' in kw:
                partner_address_dct['street2'] = kw['address2']
            if 'city' in kw:
                city_id = request.env['res.city'].sudo().search([('name', '=', kw['city'])], limit=1)
                if city_id:
                    partner_address_dct['city_id'] = city_id.id
                else:
                    partner_address_dct['city'] = kw['city']
            if 'pincode' in kw:
                partner_address_dct['zip'] = kw['pincode']
            if 'state' in kw:
                state_id = request.env['res.country.state'].sudo().search([('name', '=', kw['state'])], limit=1)
                if state_id:
                    country_id = request.env['res.country'].sudo().search([('id', '=', state_id.country_id.id)],
                                                                          limit=1)
                    partner_address_dct['state_id'] = state_id.id
                    partner_address_dct['country_id'] = country_id.id
                else:
                    partner_address_dct['state_name'] = kw['state']

            partner_id.update(partner_address_dct)
            for child in partner_id.child_ids:
                child.update(partner_address_dct)

            bank_ids = request.env['res.bank'].sudo().search([])
            if partner_id.approval_state == 'form_submitted':
                return request.render(
                    'qno_vendor_registration.website_verification_already_submitted_page',
                    {
                        'partner': partner_id
                    }
                )
            else:
                return request.render(
                    'qno_vendor_registration.website_verification_bank_details',
                    {
                        'partner': partner_id,
                        'bank_ids': bank_ids
                    }
                )

    @http.route(
        '/customer_verification_bank_details',
        methods=['GET', 'POST', 'FILES'],
        type='http',
        auth='public',
        website=True
    )
    def customer_verification_bank_details(self, **kw):
        if 'partner_id' in kw:

            bank_id = request.env['res.bank']
            partner_id = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
            data_record = kw['bank_cheque']
            if partner_id.approval_state == 'form_submitted':
                template_id = 'qno_vendor_registration.website_verification_already_submitted_page'
                return request.render(
                    template_id,
                    {
                        'partner': partner_id
                    }
                )
            else:
                template_id = 'qno_vendor_registration.website_verification_thanks_page'

            IFSC_Code = kw['ifsc_code']
            URL = "https://ifsc.razorpay.com/"
            bank_data = requests.get(URL + IFSC_Code).json()
            if 'BANK' not in bank_data:
                message = "No Bank Detail Found For IFSC Code"
                return request.render(
                    'qno_vendor_registration.website_verification_bank_details',
                    {
                        'msg': message,
                        'partner': partner_id,
                        'kw': kw,
                    }
                )

            #             bank_name = bank_id.sudo().search([('bic', '=', IFSC_Code)])

            #             if not bank_name:
            #                 bank_name = bank_id.sudo().create({
            #                     'name': bank_data['BANK'],
            #                     'bic': IFSC_Code
            #                 })

            ir_values = {
                'name': "Company Pan",
                'type': 'binary',
                'datas': base64.encodebytes(data_record.read()),
                'store_fname': data_record,
            }

            data_list = []
            data_dct = {
                'acc_holder_name': kw['account_name'],
                'bank_bic': kw['ifsc_code'],
                'acc_number': kw['account_number'],
                'upload_bank_cheque': ir_values['datas'],
                'upload_bank_cheque_name': data_record.filename,
                # 'bank_id': bank_name.id
            }
            if kw['bank_id'] == 'none':
                data_dct.update({
                    'bank_id': ''
                })
            else:
                bank_name = bank_id.sudo().browse(int(kw['bank_id']))
                data_dct.update({
                    'bank_id': bank_name.id
                })

            data_list.append((0, 0, data_dct))
            if 'other_bank_details' in kw:

                other_bank_cheque = kw['other_bank_cheque']
                other_bank_cheque_value = {
                    'name': "Bank Chaque Value",
                    'type': 'binary',
                    'datas': base64.encodebytes(other_bank_cheque.read()),
                    'store_fname': other_bank_cheque,
                }
                if kw['other_ifsc_code'] != '':
                    other_IFSC_Code = kw['other_ifsc_code']
                    URL = "https://ifsc.razorpay.com/"
                    other_bank_data = requests.get(URL + other_IFSC_Code).json()
                    other_bank_name = bank_id.sudo().search([('bic', '=', other_IFSC_Code)])
                    if 'BANK' not in other_bank_data:
                        message = "No Bank Detail Found For IFSC Code Other"
                        return request.render(
                            'qno_vendor_registration.website_verification_bank_details',
                            {
                                'other_msg': message,
                                'partner': partner_id,
                                'kw': kw,
                            }
                        )
                    if not other_bank_name:
                        other_bank_name = bank_id.sudo().create({
                            'name': other_bank_data['BANK'],
                            'bic': IFSC_Code
                        })

                    data_dct_other = {
                        'acc_holder_name': kw['other_account_name'],
                        'bank_bic': kw['other_ifsc_code'],
                        'acc_number': kw['other_account_number'],
                        'upload_bank_cheque': other_bank_cheque_value['datas'],
                        'upload_bank_cheque_name': other_bank_cheque.filename,
                        # 'bank_id': other_bank_name.id
                    }
                    if kw['other_bank_id'] == 'none':
                        data_dct_other.update({
                            'bank_id': ''
                        })
                    else:
                        bank_name = bank_id.sudo().browse(int(kw['other_bank_id']))
                        data_dct_other.update({
                            'bank_id': bank_name.id
                        })
                    data_list.append((0, 0, data_dct_other))

            partner_id.update({
                'bank_ids': data_list,
                # 'approval_state': 'form_submitted',
            })

            # return_value = ('qno_vendor_registration.website_verification_thanks_page',
            #     {
            #         'partner': partner_id
            #     })
            # partner_id.approval_state == 'form_submitted':
            #             partner_2 = partner_id.copy()
            #             partner_2_contact_details_list = []
            #             for rec in partner_id.child_ids:
            #                 contact_details_partner_2 = {
            #                     'name': rec.name,
            #                     'mobile': rec.mobile,
            #                     'type': 'delivery',
            #                     'parent_id': partner_id.id,
            #                 }
            #                 child_id_2 = request.env['res.partner'].sudo().create(contact_details_partner_2)
            #                 partner_2_contact_details_list.append((4, child_id_2.id))

            #             partner_id.update({
            # #                 'type': 'delivery',
            # #                 'name': partner_id.name,
            #                 'bank_ids': data_list,
            # #                 'organization_type_id': partner_id.organization_type_id.id,
            # #                 'company_pan': partner_id.company_pan,
            # #                 'authorised_signatory_pan': partner_id.authorised_signatory_pan,
            # #                 'msme_type': partner_id.msme_type,
            # #                 'business_tan': partner_id.business_tan,
            # #                 'approval_state': partner_id.approval_state,
            # #                 'child_ids': partner_2_contact_details_list,
            #
            #             })
            #     return request.render(
            #         'qno_vendor_registration.website_verification_already_submitted_page',
            #         {
            #             'partner': partner_id
            #         }
            #     )
            # else:

            partner_id.update({
                'approval_state': 'form_submitted',
            })

            return request.render(
                template_id,
                {
                    'partner': partner_id
                }
            )
