# -*- coding: utf-8 -*-
import requests
from html import unescape
import json
import pprint
import base64

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from lxml import etree
import xml.etree.ElementTree as ET
import xmltodict
from cryptography.fernet import Fernet

AddressType = {
    'invoice': 'bo_BillTo',
    'delivery': 'bo_ShipTo',
}
GstType = {
    'regular': 'gstRegularTDSISD',
    'composition': 'gstCompositionLevy',
    'unregistered': 'gstNonResidentTaxablePerson',
    'consumer': 'gstCasualTaxablePerson',
    'overseas': 'gstNonResidentTaxablePerson',
    'special_economic_zone': 'gstGoverDepartPSU',
    'deemed_export': 'gstGoverDepartPSU',
    'uin_holders': 'gstUNAgencyEmbassy',
    'e_commerce_operators': 'gstRegularTDSISD'
}
CardType = {
    'customer': 'cCustomer',
    'vendor': 'cSupplier'
}


class Partner(models.Model):
    _inherit = 'res.partner'

    approval_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('form_submitted', 'Submited'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default="draft",
        copy=False
    )

    organization_type_id = fields.Many2one(
        'organization.type',
        string="Organization",
        copy=False
    )

    company_pan = fields.Char(
        string='Company Pan',
        copy=False
    )
    prefill_check_upload = fields.Binary(
        string='Company Pan Document'
    )
    prefill_check_upload_name = fields.Char(
        string='Prefill Check Upload Name'
    )

    authorised_signatory_pan = fields.Char(
        string='Authorised Signatory Pan',
        copy=False
    )

    contact_person_name = fields.Char(
        string='Contact Person',
    )
    business_category_id = fields.Many2one(
        'business.category',
        string="Business Category",
        copy=False
    )
    business_tan = fields.Char(
        string='Business Tan',
        copy=False
    )

    company_details_upload = fields.Binary(
        string='Business Tan Document ',
        copy=False
    )
    company_details_upload_name = fields.Char(
        string='Company Detail Upload Name',
        copy=False
    )

    authorised_signatory_pan_upload = fields.Binary(
        string='Authorised Signatory Pan ',
        copy=False
    )
    authorised_signatory_pan_upload_name = fields.Char(
        string='Authorised Signatory Pan Name',
        copy=False
    )

    gst_certificate_upload = fields.Binary(
        string='GST Certificate ',
        copy=False
    )
    gst_certificate_upload_name = fields.Char(
        string='GST Certificate Name',
        copy=False
    )

    # bank_details_upload = fields.Binary(
    #     string='Bank Cheque'
    # )
    # bank_details_upload_name = fields.Char(
    #     string='Bank Details Upload Name'
    # )

    l10n_in_gst_treatment = fields.Selection(selection_add=[
        ('e_commerce_operators', 'E-Commerce Operators'),
    ])

    msme_type = fields.Selection(
        selection=[
            ('micro', 'Micro'),
            ('small', 'Small'),
            ('medium', 'Medium'),
        ],
        copy=False,
        string='MSME Type'
    )

    msme_no = fields.Char(
        string='MSME No',
        copy=False
    )
    state_name = fields.Char(
        string='State Name',
        copy=False
    )
    sap_card_code = fields.Char(
        string='SAP Card Sode',
        copy=False
    )
    sap_response = fields.Text(
        "SAP Response",
        copy=False
    )
    partner_type = fields.Selection(
        selection=[
            ('customer', 'Customer'),
            ('vendor', 'Vendor'),
        ],
        copy=False,
        string='Partner Type(Card Type)'
    )
    address_id_name = fields.Char(
        "Address ID",
        copy=False
    )

    partner_type_dict = {
        'contact': 'Contact',
        'invoice': 'Invoice Address',
        'delivery': 'Delivery Address',
        'private': 'Private Address',
        'other': 'Other Address',
    }

    customer_vendor_group_id = fields.Many2one(
        'customer.vendor.group',
        string="Customer Vendor Group",
        copy=False
    )

    @api.constrains('address_id_name', 'type')
    def check_address_id_name(self):
        for partner in self:
            manual_models = partner.parent_id.child_ids.filtered(
                lambda
                    modal: modal.type == partner.type and modal.address_id_name == partner.address_id_name and modal.parent_id == partner.parent_id and modal.address_id_name != False)
            for pt in manual_models:
                if pt != partner:
                    msg = '{} partners  Address ({}) And Type ({}) Already Used In Another Partner!'.format(
                        partner.name or '', partner.address_id_name,
                        partner.partner_type_dict.get(partner.type))
                    raise ValidationError(_(msg))

    @api.model
    def default_get(self, fields_list):
        res = super(Partner, self).default_get(fields_list)
        res['user_id'] = self.env.user.id
        return res

    def action_send_email(self):
        for rec in self:
            # sap_conf_id = rec.env['sap.configuration'].sudo().search([], limit=1)
            # if not sap_conf_id:
            #     raise ValidationError(_('Please Set SAP Configuration!'))
            sap_conf_id = self.env.company.api_url
            print("_______________  sap_conf_id", sap_conf_id)
            if not sap_conf_id:
                raise ValidationError(_('Please Set API URL!'))
            partner_id = str(rec.id)
            id_bytes = partner_id.encode("ascii")
            base64_bytes = base64.b64encode(id_bytes)
            id_encoded = base64_bytes.decode("ascii")
            url = self.get_base_url() + "/vendor-verification/%s" % id_encoded
            ctx = {
                'url': url
            }
            template_id = self.env.ref('qno_vendor_registration.customer_registration_send_mail_template')
            template_id.with_context(ctx).send_mail(rec.id, force_send=True)

            rec.write({
                'approval_state': 'sent'
            })

    def action_approve(self):
        self.write({
            'approval_state': 'approved'
        })

    def action_reject(self):
        self.write({
            'approval_state': 'rejected'
        })

    def action_reset_draft(self):
        self.write({
            'approval_state': 'draft'
        })

    @api.model
    def _get_data_common(self):
        if not self.partner_type:
            raise ValidationError(_('Please Define valid Card Type!'))

        data = {
            "CardName": self.name,
            "CardType": CardType[self.partner_type],
            "Series": 175,
            "Currency": "##",
            "Cellular": self.mobile,
            "EmailAddress": self.email,
            "Valid": "tYES",
            "Frozen": "tNO",
            "U_PortalVendorRefNo": str(self.id),
            "U_MSMEType": self.msme_type,
            "U_MSMERegNo": self.msme_no,
            'CreditLimit': self.credit_limit
        }
        return data

    @api.model
    def _get_data_BPAddresses(self):
        data_list = []
        count = 0
        for child in self.child_ids.filtered(lambda i: i.type in AddressType):
            if not child.address_id_name:
                raise ValidationError(_('Please add valid AddressID on %s Addrees' % (child.type)))
            data_list.append({
                "RowNum": count,
                "AddressType": AddressType.get(child.type, ''),
                "AddressName": child.address_id_name,
                "Street": child.street,
                "StreetNo": '',
                "Block": child.street2,
                "BuildingFloorRoom": "",
                "ZipCode": child.zip,
                "City": child.city,
                "Country": child.country_id.code,
                "State": child.state_id.code,
                "GSTIN": child.vat,
                "GstType": GstType.get(child.l10n_in_gst_treatment, '')
            })
            count += 1
        return {'BPAddresses': data_list}

    @api.model
    def _get_data_ContactEmployees(self):
        #         data = [
        #                 {
        #                     "Name": "Sarthik",
        #                     "FirstName": "Sarthik",
        #                     "MiddleName": ".",
        #                     "LastName": ".",
        #                     "Position": ".",
        #                     "MobilePhone": ".",
        #                     "E_Mail": "."
        #                 }
        #             ]
        data = []
        return {'ContactEmployees': data}

    @api.model
    def _get_data_BPBankAccounts(self):
        data_list = []
        for bank in self.bank_ids:
            data_list.append({
                "Branch": bank.bank_id.name,
                "Country": bank.bank_id.country.code or '',
                "BankCode": bank.bank_id.bank_code,
                "AccountNo": bank.acc_number,
                "AccountName": bank.acc_holder_name,
                "BICSwiftCode": bank.bank_id.bic,
            })

        return {'BPBankAccounts': data_list}

    @api.model
    def _get_data_BPFiscalTaxIDCollection(self):
        #         data = []
        data = [
            {
                "TaxId0": self.company_pan,
            }
        ]

        #         data = [
        #                 {
        #                     "Address": "Thane",
        #                     "TaxId0": "AHBPQ1740Q",
        #                     "TaxId13": "AHBPQ1740Q"
        #                 }
        #             ]
        return {'BPFiscalTaxIDCollection': data}

    def action_submit_partner_to_sap(self):

        # config = self.env['sap.configuration'].search([], limit=1)
        # if not config:
        #     raise ValidationError(_('Please active SAP Configuration!'))

        # databasename = config.database_name
        databasename = self.env.company.database_name

        if not databasename:
            raise ValidationError(_('Please configure valid Database in SAP Configuration!'))

        # url = config.url
        url = self.env.company.url
        if not url:
            raise ValidationError(_('Please confiure valid URL in  SAP Configuration!'))
        # config_url = config.api_url
        config_url = self.env.company.api_url
        print("url ----------", url)

        # getBPSeries

        headers = {
        }

        # http://10.40.50.1:60009
        # 136.243.59.116
        getBPSeries_url = url + '/getBPSeries'
        getBPSeries_url = getBPSeries_url + '?DatabaseName=' + databasename

        getBPSeries_url = getBPSeries_url + '&CardType=' + CardType[self.partner_type]

        getBPSeries_url = getBPSeries_url + '&CardCode=' + "null"

        # Params -> DatabaseName, CardCode (Optional) ,CardType (cSupplier,cCustomer)
        print("getBPSeries_url ::::::::::::::::", getBPSeries_url)
        #         r = requests.post(getBPSeries_url, data={}, headers=headers, timeout=65)

        response = requests.request("GET", getBPSeries_url, headers=headers)
        print("response.text -------------------", response.text)
        respond = json.loads(response.text)

        print("rd.....................", r)

        #         try:
        #             r = requests.post(url, data=xml_transaction, headers=headers, timeout=65)
        r.raise_for_status()

        response = unescape(r.content.decode())

        print(x)
        data = {}
        data_common = self._get_data_common()
        data_BPAddresses = self._get_data_BPAddresses()
        data_ContactEmployees = self._get_data_ContactEmployees()
        data_BPBankAccounts = self._get_data_BPBankAccounts()
        data_BPFiscalTaxIDCollection = self._get_data_BPFiscalTaxIDCollection()

        data.update(data_common)
        data.update(data_BPAddresses)
        data.update(data_ContactEmployees)
        data.update(data_BPBankAccounts)
        data.update(data_BPFiscalTaxIDCollection)

        print(pprint.pformat(data))

        method = 'Add'
        xml_transaction = """<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Header>
                    <UserValue xmlns="http://tempuri.org/">
                    <DatabaseName>{databasename}</DatabaseName>                                            
                    <JSON>{data}</JSON>
                    <APIMethod>{method}</APIMethod>
                    </UserValue>
                </soap:Header>
                <soap:Body>
                    <BusinessPartners xmlns="http://tempuri.org/" />
                </soap:Body>
            </soap:Envelope>
        """.format(databasename=databasename, data=json.dumps(data), method=method)

        if self.sap_card_code:
            method = 'Update'
        xml_transaction = """<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Header>
                    <UserValue xmlns="http://tempuri.org/">
                    <DatabaseName>{databasename}</DatabaseName>                                            
                    <JSON>{data}</JSON>
                    <APIMethod>{method}</APIMethod>
                    <Code>{sap_card_code}</Code>
                    </UserValue>
                </soap:Header>
                <soap:Body>
                    <BusinessPartners xmlns="http://tempuri.org/" />
                </soap:Body>
            </soap:Envelope>
        """.format(databasename=databasename, data=json.dumps(data), method=method, sap_card_code=self.sap_card_code)

        headers = {
            'Content-Type': 'text/xml',
        }

        r = requests.post(url, data=xml_transaction, headers=headers, timeout=65)

        #         try:
        #             r = requests.post(url, data=xml_transaction, headers=headers, timeout=65)
        r.raise_for_status()

        response = unescape(r.content.decode())
        #         except Exception:
        #             response = "timeout"

        self.sap_response = response
        xpars = xmltodict.parse(response)

        for xp in xpars:
            for x in xpars[xp]:
                if x == 'soap:Body':
                    for a in xpars[xp][x]:
                        if 'BusinessPartnersResult' in xpars[xp][x][a]:
                            b = xpars[xp][x][a]['BusinessPartnersResult']
                            json_object = json.loads(b)
                            if 'CardCode' in json_object:
                                CardCode = json_object['CardCode']
                                self.sap_card_code = CardCode
